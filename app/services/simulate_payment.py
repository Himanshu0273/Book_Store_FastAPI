import random
import uuid
import time
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional

from app.models.transaction_model import Transactions
from app.models.payments_model import Payments
from app.models.cart_model import Cart
from app.models.cart_item_model import CartItem
from app.models.book_model import Book
from app.models.orders_model import Order  
from app.models.user_model import User  
from app.queries.cart_queries import CartQueries
from app.queries.order_queries import OrderQueries
from app.queries.book_queries import BookQueries
from app.utils.enums import PaymentsEnum, TransactionStatusEnum, CartActivityEnum 
from app.queries.payment_queries import PaymentQueries
from app.exceptions.payment_exceptions import PaymentNotFound, AttemptsExceeded
from app.exceptions.db_exception import DBException
from app.db.session import SessionLocal
from app.config.logger_config import func_logger


def simulate_payment(payment_id: int, user: User, simulate_status: Optional[str] = None):
    db = SessionLocal()
    try:
        func_logger.info(f"[START] Simulating payment for ID {payment_id}, simulate_status: {simulate_status}")
        time.sleep(3)

        payment = PaymentQueries.get_payment_by_id(payment_id=payment_id, db=db)
        if not payment:
            func_logger.warning(f"Payment not found with ID {payment_id}")
            raise PaymentNotFound

        # Get the associated order
        order = db.query(Order).filter(Order.id == payment.order_id).first()
        if not order:
            func_logger.error(f"Order not found for payment_id {payment_id}")
            raise Exception(f"Order not found for payment_id {payment_id}")

        # Decide success/failure
        if simulate_status is not None:
            success = simulate_status.lower() == "success"
        else:
            success = random.choice([True, False])

        txn_status = TransactionStatusEnum.SUCCESS if success else TransactionStatusEnum.FAILURE
        txn_message = "Successful Payment" if success else "Payment Failed"

        # Create transaction row
        transaction = Transactions(
            payment_id=payment.id,
            txn_reference=str(uuid.uuid4()),
            status=txn_status,
            message=txn_message
        )
        db.add(transaction)
        db.flush()
        func_logger.info(f"Transaction added for payment_id {payment_id} with status {txn_status}")

        # Update attempts
        payment.attempts += 1
        func_logger.info(f"Attempt #{payment.attempts} for payment_id {payment_id}")

        if success:
            # Payment successful - update both payment and order status
            payment.status = PaymentsEnum.SUCCESSFUL
            order.payment_status = PaymentsEnum.SUCCESSFUL  # or SUCCESS based on your enum
            func_logger.info(f"Payment ID {payment_id} and Order ID {order.id} marked as SUCCESSFUL")
        else:
            if payment.attempts >= 3:
                # Payment failed after 3 attempts
                payment.status = PaymentsEnum.FAILED
                order.payment_status = PaymentsEnum.SUCCESSFUL  # Mark order as cancelled
                func_logger.warning(f"Payment ID {payment_id} marked as FAILED after 3 attempts")
                func_logger.warning(f"Order ID {order.id} marked as CANCELLED")
                
                
                _rollback_cart_and_stock(payment.order_id, db)
            else:
                
                func_logger.info(f"Payment ID {payment_id} failed. More attempts allowed.")

        db.commit()
        func_logger.info(f"[DONE] simulate_payment committed for payment_id {payment_id}")

    except SQLAlchemyError as e:
        db.rollback()
        func_logger.error(f"[SQL ERROR] during simulate_payment: {e}")
        raise DBException()
    except Exception as e:
        db.rollback()
        func_logger.error(f"[EXCEPTION] during simulate_payment: {e}")
        raise
    finally:
        db.close()
        func_logger.info(f"[CLOSE] Session closed for Payment ID {payment_id}")


def _rollback_cart_and_stock(order_id: int, db, user_id: int):
    """
    Rollback cart items and restore book stock when payment fails after 3 attempts
    """
    try:
        order = OrderQueries.get_order_by_id(user_id=user_id, order_id=order_id, db=db)
        
        if not order:
            func_logger.warning(f"No order found with id {order_id}, cannot rollback.")
            return
        
        if not order.cart_id:
            func_logger.warning(f"No cart_id found for order_id {order_id}, cannot rollback.")
            return

        
        cart = CartQueries.get_cart_by_user_id(user_id=user_id, db=db)
        
        if not cart:
            func_logger.warning(f"No cart found with id {order.cart_id}, cannot rollback.")
            return

        cart_items = CartQueries.get_all_cart_items(cart_id=cart.id, db=db)
        
        for item in cart_items:
            book = BookQueries.get_book_by_id(book_id=item.book_id, db=db)
            if book:
                book.inventory.quantity += item.quantity
                func_logger.info(f"Restored {item.quantity} units to book_id {book.id}")
            
            
            db.delete(item)

        cart.status = CartActivityEnum.CANCELLED 
        
        func_logger.info(f"Cart rollback and stock restoration complete for order_id {order_id}")
        
    except Exception as e:
        func_logger.error(f"Error during cart rollback for order_id {order_id}: {e}")
        raise