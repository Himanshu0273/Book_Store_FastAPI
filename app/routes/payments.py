import random
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.permissions import is_customer
from app.config.logger_config import func_logger
from app.db.session import get_db
from app.exceptions.book_exceptions import BookNotFound
from app.exceptions.db_exception import DBException
from app.exceptions.order_exceptions import OrderNotFound
from app.exceptions.payment_exceptions import (AttemptsExceeded,
                                               PaymentNotFound,
                                               TransactionNotAdded)
from app.models.orders_model import Order
from app.models.payments_model import Payments
from app.models.transaction_model import Transactions
from app.models.user_model import User
from app.queries.book_queries import BookQueries
from app.queries.cart_queries import CartQueries
from app.queries.order_queries import OrderQueries
from app.queries.payment_queries import PaymentQueries
from app.schemas.payment_schema import CreatePayment, PaymentResponse
from app.services.transactions import add_transaction, rollback_payment
from app.utils.enums import (CartActivityEnum, PaymentMethodEnum, PaymentsEnum,
                             TransactionStatusEnum)

payment_router = APIRouter(prefix="/payments", tags=["Payments"])


@payment_router.post("/{ord_id}", status_code=status.HTTP_201_CREATED)
def add_payment(
    ord_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_customer),
):
    try:
        func_logger.info(
            f"Initiating payment for Order ID: {ord_id} by User ID: {current_user.id}"
        )

        order = OrderQueries.get_order_by_id(
            user_id=current_user.id, order_id=ord_id, db=db
        )
        if not order:
            func_logger.warning(
                f"Order not found: Order ID {ord_id}, User ID: {current_user.id}"
            )
            raise OrderNotFound(order_id=ord_id)

        exists_payment = PaymentQueries.get_payment_by_order_id(order_id=ord_id, db=db)

        if not exists_payment:
            payment_mode = random.choice(
                [
                    PaymentMethodEnum.CARD,
                    PaymentMethodEnum.COD,
                    PaymentMethodEnum.UPI,
                    PaymentMethodEnum.NETBANKING,
                ]
            )

            new_payment = Payments(
                order_id=ord_id,
                total_cost=order.total,
                mode_of_payment=payment_mode,
                attempts=0,
                status=PaymentsEnum.PENDING,
            )
            db.add(new_payment)
            db.commit()
            db.refresh(new_payment)

            func_logger.info(
                f"Created new payment ID: {new_payment.id} for Order ID: {ord_id}"
            )

            transaction = add_transaction(payment=new_payment, db=db)
            if transaction is None:
                func_logger.error(
                    f"Transaction failed to process for Payment ID: {new_payment.id}"
                )
                raise TransactionNotAdded()

            if transaction.status == TransactionStatusEnum.SUCCESS:
                new_payment.status = PaymentsEnum.SUCCESSFUL
                order.payment_status = PaymentsEnum.SUCCESSFUL
                func_logger.info(
                    f"Payment ID: {new_payment.id} and Order ID: {order.id} marked as SUCCESSFUL"
                )

            db.commit()
            return {
                "message": "Payment initiated",
                "payment_id": new_payment.id,
                "transaction_id": transaction.id,
                "transaction_status": transaction.status,
            }

        if exists_payment.status == PaymentsEnum.SUCCESSFUL:
            func_logger.info(
                f"Payment ID: {exists_payment.id} already marked SUCCESSFUL — no further action taken."
            )
            return {
                "message": "Payment has already been completed successfully.",
                "payment_id": exists_payment.id,
                "status": exists_payment.status,
            }
        if exists_payment.attempts >= 3:
            exists_payment.status = PaymentsEnum.FAILED
            db.commit()
            func_logger.warning(
                f"Payment ID: {exists_payment.id} exceeded 3 attempts and was marked as FAILED"
            )
            rollback_payment(
                payment=exists_payment, ord_id=ord_id, user_id=current_user.id, db=db
            )
            raise AttemptsExceeded()

        transaction = add_transaction(payment=exists_payment, db=db)
        if transaction is None:
            func_logger.error(
                f"Transaction failed to process for existing Payment ID: {exists_payment.id}"
            )
            raise TransactionNotAdded()

        if transaction.status == TransactionStatusEnum.SUCCESS:
            exists_payment.status = PaymentsEnum.SUCCESSFUL
            order.payment_status = PaymentsEnum.SUCCESSFUL
            func_logger.info(
                f"Payment ID: {exists_payment.id} and Order ID: {order.id} marked as SUCCESSFUL"
            )

        db.commit()

        return {
            "message": "Transaction attempted",
            "payment_id": exists_payment.id,
            "transaction_id": transaction.id,
            "transaction_status": transaction.status,
        }

    except SQLAlchemyError as e:
        db.rollback()
        func_logger.exception(
            f"Database error during payment for Order ID: {ord_id}\nError: {e}"
        )
        raise DBException()

    except Exception as e:
        db.rollback()
        func_logger.exception(
            f"Unexpected error during payment for Order ID: {ord_id}\nError: {e}"
        )
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {e}")


@payment_router.patch("/soft-delete/{payment_id}", status_code=status.HTTP_200_OK)
def soft_delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_customer),
):
    try:
        func_logger.info(
            f"Soft-deleting Payment ID: {payment_id} for User ID: {current_user.id}"
        )

        payment = PaymentQueries.get_payment_by_id(payment_id=payment_id, db=db)
        if not payment or payment.order.user_id != current_user.id:
            func_logger.warning(f"Payment ID: {payment_id} not found or unauthorized")
            raise PaymentNotFound(payment_id=payment_id)

        order = payment.order
        cart = order.cart

        # Update statuses
        payment.status = PaymentsEnum.FAILED
        order.payment_status = PaymentsEnum.FAILED
        cart.status = CartActivityEnum.CANCELLED
        func_logger.info(
            f"Marked Payment ID: {payment_id} and Order ID: {order.id} as FAILED; Cart ID: {cart.id} as CANCELLED"
        )

        # Restore inventory
        cart_items = CartQueries.get_all_cart_items(cart_id=cart.id, db=db)
        for item in cart_items:
            book = BookQueries.get_book_by_id(book_id=item.book_id, db=db)
            if not book:
                func_logger.error(
                    f"Book ID {item.book_id} not found while restoring during soft delete."
                )
                raise BookNotFound(book_id=item.book_id)
            book.inventory.quantity += item.quantity
            func_logger.debug(f"Restored {item.quantity} to Book ID {item.book_id}")

        db.commit()
        func_logger.info(f"Soft delete completed for Payment ID: {payment_id}")
        return {
            "message": "Payment soft-deleted successfully",
            "payment_id": payment_id,
        }

    except SQLAlchemyError as e:
        db.rollback()
        func_logger.exception(
            f"DB error during soft delete for Payment ID: {payment_id} | Error: {e}"
        )
        raise DBException()

    except Exception as e:
        db.rollback()
        func_logger.exception(
            f"Unexpected error during soft delete for Payment ID: {payment_id}"
        )
        raise HTTPException(status_code=500, detail="Unexpected error occurred")
