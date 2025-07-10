from datetime import datetime, timezone
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.cart_item_model import CartItem
from app.models.cart_model import Cart
from app.models.user_model import User


class CartQueries:

    @staticmethod
    def create_cart(user_id: int, db: Session) -> Cart:

        existing_cart = db.query(Cart).filter_by(user_id=user_id).first()
        if existing_cart:
            return existing_cart

        cart = Cart(user_id=user_id, updated_at=datetime.now(timezone.utc))
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return cart

    @staticmethod
    def get_user_cart(user: User, db: Session):
        return db.query(Cart).filter(Cart.user_id == user.id).first()

    @staticmethod
    def get_cart_item_by_id(cart_id: int, book_id: int, db: Session) -> CartItem | None:
        return db.query(CartItem).filter_by(cart_id=cart_id, book_id=book_id).first()

    @staticmethod
    def get_all_cart_items(cart_id: int, db: Session) -> List[CartItem] | None:
        items = db.query(CartItem).filter(CartItem.cart_id == cart_id).all()
        return items if items else None
