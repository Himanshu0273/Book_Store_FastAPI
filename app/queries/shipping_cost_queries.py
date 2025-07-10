from typing import List

from sqlalchemy.orm import Session

from app.models.shipping_cost_model import ShippingCost


class ShippingCostQueries:

    @staticmethod
    def get_all_rows(db: Session) -> List[ShippingCost]:
        return db.query(ShippingCost).all()

    @staticmethod
    def get_country_by_name(country_name: str, db: Session) -> ShippingCost:
        return (
            db.query(ShippingCost).filter(ShippingCost.country == country_name).first()
        )

    @staticmethod
    def get_country_by_id(id: int, db: Session) -> ShippingCost:
        return db.query(ShippingCost).filter(ShippingCost.id == id).first()
