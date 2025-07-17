import random

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config.logger_config import func_logger
from app.exceptions.book_exceptions import BookNotFound
from app.exceptions.db_exception import DBException
from app.models.cart_item_model import CartItem
from app.models.cart_model import Cart
from app.models.orders_model import Order
from app.models.payments_model import Payments
from app.models.transaction_model import Transactions
from app.queries.book_queries import BookQueries
from app.queries.cart_queries import CartQueries
from app.queries.order_queries import OrderQueries
from app.utils.enums import (CartActivityEnum, PaymentsEnum,
                             TransactionStatusEnum)


def add_transaction(payment: Payments, db: Session) -> Transactions | None:
    func_logger.info(f"Initiating transaction for Payment ID: {payment.id}")

    try:
        payment.attempts += 1
        func_logger.debug(f"Updated payment attempts to: {payment.attempts}")

        status = random.choice(
            [TransactionStatusEnum.FAILURE, TransactionStatusEnum.SUCCESS]
        )

        message = (
            "Transaction Successful"
            if status == TransactionStatusEnum.SUCCESS
            else "Transaction Failed"
        )

        transaction = Transactions(
            payment_id=payment.id, status=status, message=message
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        func_logger.info(
            f"Transaction {transaction.id} created for Payment ID: {payment.id} with status: {status}"
        )
        return transaction

    except SQLAlchemyError as e:
        db.rollback()
        func_logger.error(
            f"DB error during transaction for Payment ID: {payment.id} | Error: {e}"
        )
        return None

    except Exception as e:
        db.rollback()
        func_logger.exception(
            f"Unexpected error during transaction creation for Payment ID: {payment.id}"
        )
        return None


def rollback_payment(ord_id: int, user_id: int, payment: Payments, db: Session):
    try:
        func_logger.info(
            f"Rolling back Payment ID: {payment.id} for Order ID: {ord_id} and User ID: {user_id}"
        )
        if payment.attempts >= 3:
            func_logger.warning(
                f"Payment ID: {payment.id} has already reached max attempts."
            )
            return None

        order = OrderQueries.get_order_by_id(order_id=ord_id, user_id=user_id, db=db)
        if not order:
            func_logger.error(f"Order ID: {ord_id} not found for rollback.")
            return

        payment.status = PaymentsEnum.FAILED
        func_logger.debug(f"Payment ID: {payment.id} marked as FAILED")

        cart_items = CartQueries.get_all_cart_items(cart_id=order.cart_id, db=db)
        for item in cart_items:
            book = BookQueries.get_book_by_id(book_id=item.book_id, db=db)
            if not book:
                func_logger.error(f"Book ID {item.book_id} not found during rollback.")
                raise BookNotFound(book_id=item.book_id)

            book.inventory.quantity += item.quantity
            func_logger.debug(f"Restored {item.quantity} to book ID {item.book_id}")

        order.cart.status = CartActivityEnum.CANCELLED
        func_logger.info(f"Cart ID {order.cart_id} marked as CANCELLED")

        db.commit()
        func_logger.info(
            f"Rollback completed successfully for Payment ID: {payment.id}"
        )
        return {"rollback_success": True, "payment_id": payment.id}

    except SQLAlchemyError as e:
        db.rollback()
        func_logger.exception(
            f"DB error during rollback for Payment ID: {payment.id} | Error: {e}"
        )
        raise DBException()

    except Exception as e:
        db.rollback()
        func_logger.exception(
            f"Unexpected error during rollback for Payment ID: {payment.id}"
        )
        raise DBException()
