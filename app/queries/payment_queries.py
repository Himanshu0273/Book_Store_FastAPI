from sqlalchemy.orm import Session
from app.models.payments_model import Payments


class PaymentQueries:
    
    @staticmethod
    def get_payment_by_order_id(order_id: int, db: Session)->Payments | None:
        return db.query(Payments).filter_by(order_id=order_id).first()
    
    @staticmethod
    def get_payment_by_id(payment_id: int, db: Session)->Payments | None:
        return db.query(Payments).filter_by(payment_id=payment_id)