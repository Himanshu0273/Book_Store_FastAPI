from typing import List

from sqlalchemy.orm import Session

from app.models.orders_model import Order


class OrderQueries:

    @staticmethod
    def get_all_orders_of_customer(user_id: int, db: Session) -> List[Order] | None:
        return db.query(Order).filter(Order.user_id == user_id).all()

    @staticmethod
    def get_order_by_id(user_id: int, order_id: int, db: Session) -> Order | None:
        return (
            db.query(Order)
            .filter(Order.user_id == user_id, Order.id == order_id)
            .first()
        )
