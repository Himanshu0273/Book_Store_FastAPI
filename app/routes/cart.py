from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.permissions import is_customer
from app.config.logger_config import func_logger
from app.db.session import get_db
from app.exceptions.book_exceptions import BookNotFound
from app.exceptions.cart_exceptions import (
    CartNotFound,
    ItemQuantityLessThanZero,
    NotEnoughBooks,
)
from app.exceptions.db_exception import DBException
from app.models.book_model import Book
from app.models.cart_item_model import CartItem
from app.models.cart_model import Cart
from app.models.user_model import User
from app.queries.book_queries import BookQueries
from app.queries.cart_queries import CartQueries
from app.schemas.cart_schema import ShowCart
from app.schemas.cartitem_schema import CreateCartItem, ShowCartItem
from app.utils.response import build_response
from app.utils.update_cart import update_cart_totals

cart_router = APIRouter(prefix="/cart", tags=["Cart"])


# Create cart for a user
@cart_router.get("/", response_model=ShowCart)
def get_cart(user: User = Depends(is_customer), db: Session = Depends(get_db)):

    func_logger.info("GET - /cart")
    cart = CartQueries.get_user_cart(user=user, db=db)
    if not cart:
        func_logger.warning(f"Cart for the give user not found: {user.id}!")
        raise CartNotFound()

    func_logger.info(f"Cart for user: {user.id} fetched successfully!!")
    return cart


# Add items to the cart and row to cart item
@cart_router.post(
    "/add-item", response_model=ShowCartItem, status_code=status.HTTP_202_ACCEPTED
)
def add_item_to_cart(
    item: CreateCartItem,
    user: User = Depends(is_customer),
    db: Session = Depends(get_db),
):
    func_logger.info(f"POST - /cart/add-item")

    cart = CartQueries.get_user_cart(user=user, db=db)

    if not cart:
        func_logger.error(
            f"Cart not available for this user: {user.id}. Creating one..."
        )
        try:
            cart = CartQueries.create_cart(user_id=user.id, db=db)

        except Exception as e:
            db.rollback()
            func_logger.error(f"Failed to create cart for user: {e}")
            raise DBException()

    book = BookQueries.get_book_by_id(book_id=item.book_id, db=db)
    if not book:
        func_logger.error(f"Book not available with the ID: {item.book_id}")
        raise BookNotFound(book_id=item.book_id)

    if book.quantity < item.quantity:
        func_logger.error(
            f"There aren't enough books the maximum quantity available is: {book.quantity}"
        )
        raise NotEnoughBooks(quantity=book.quantity)

    if item.quantity <= 0:
        raise ItemQuantityLessThanZero()

    cart_item = CartQueries.get_cart_item_by_id(
        cart_id=cart.id, book_id=item.book_id, db=db
    )

    if cart_item:

        cart_item.quantity += item.quantity
        cart_item.updated_at = datetime.now(timezone.utc)

    else:
        cart_item = CartItem(
            cart_id=cart.id,
            book_id=item.book_id,
            quantity=item.quantity,
            price_when_added=book.price,
            updated_at=datetime.now(timezone.utc),
        )
        db.add(cart_item)
    db.flush()
    update_cart_totals(cart=cart)

    db.commit()
    db.refresh(cart_item)

    func_logger.info(f"Cart item added: user_id={user.id}, book_id={item.book_id}")
    return cart_item


# Get all cart items for a user
@cart_router.get("/all-items", status_code=status.HTTP_200_OK)
def get_all_items(
    db: Session = Depends(get_db),
    cart: Cart = Depends(get_cart),
    user: User = Depends(is_customer),
):

    func_logger.info("GET - /cart/all-items")
    items = CartQueries.get_all_cart_items(cart_id=cart.id, db=db)
    if not items:
        return build_response(
            status_code=status.HTTP_200_OK,
            payload="No items added in cart",
            message="The cart is empty",
        )

    return build_response(
        status_code=status.HTTP_200_OK,
        payload=items,
        message="These are all the items in your cart",
    )


# Add a book to the existing book quantity
@cart_router.patch("/add-book/{book_id}", status_code=status.HTTP_202_ACCEPTED)
def add_book_quantity(
    book_id: int,
    db: Session = Depends(get_db),
    cart: Cart = Depends(get_cart),
    user: User = Depends(is_customer),
):
    func_logger.info(f"PATCH - /cart/add-book/{book_id}")
    try:
        item = CartQueries.get_cart_item_by_id(cart_id=cart.id, book_id=book_id, db=db)
        if not item:
            func_logger.error(f"Could not find the item to increment: {book_id}")
            raise BookNotFound(book_id=book_id)

        book = BookQueries.get_book_by_id(book_id=book_id, db=db)

        if item.quantity + 1 > book.quantity:
            func_logger.error(
                f"There aren't enough books. Max available is: {book.quantity}"
            )
            raise NotEnoughBooks(quantity=book.quantity)

        item.quantity += 1
        item.updated_at = datetime.now(timezone.utc)

        update_cart_totals(cart=cart)

        db.commit()
        db.refresh(item)
        db.refresh(cart)

        return build_response(
            status_code=status.HTTP_202_ACCEPTED,
            payload={"book_id": book_id},
            message="Book quantity incremented successfully!",
        )
    except Exception as e:
        db.rollback()
        func_logger.exception(f"Error while incrementing book quantity: {e}")
        raise DBException()


# Subtract a book from the existing book quantity
@cart_router.patch("/subtract-book/{book_id}", status_code=status.HTTP_202_ACCEPTED)
def subtract_book_quantity(
    book_id: int,
    db: Session = Depends(get_db),
    cart: Cart = Depends(get_cart),
    user: User = Depends(is_customer),
):
    func_logger.info(f"PATCH - /cart/subtract-book/{book_id}")
    try:
        item = CartQueries.get_cart_item_by_id(cart_id=cart.id, book_id=book_id, db=db)
        if not item:
            func_logger.error(f"Could not find the item to decrement: {book_id}")
            raise BookNotFound(book_id=book_id)

        item.quantity -= 1
        if item.quantity == 0:
            db.delete(item)
        else:
            item.updated_at = datetime.now(timezone.utc)

        update_cart_totals(cart=cart)

        db.commit()
        db.refresh(cart)

        return build_response(
            status_code=status.HTTP_202_ACCEPTED,
            payload={"book_id": book_id},
            message="Book quantity decremented successfully!",
        )
    except Exception as e:
        db.rollback()
        func_logger.exception(f"Error while decrementing book quantity: {e}")
        raise DBException()


# Delete an item from the cart
@cart_router.delete("/delete-item/{book_id}", status_code=status.HTTP_200_OK)
def delete_book(
    book_id: int,
    cart: Cart = Depends(get_cart),
    user: User = Depends(is_customer),
    db: Session = Depends(get_db),
):
    func_logger.info(f"DELETE - /cart/delete-item/{book_id}")

    try:
        item = CartQueries.get_cart_item_by_id(cart_id=cart.id, book_id=book_id, db=db)

        if not item:
            func_logger.error(f"Book with ID: {book_id} not present!")
            raise BookNotFound(book_id=book_id)

        db.delete(item)
        db.commit()

        update_cart_totals(cart)
        db.commit()

        return build_response(
            status_code=status.HTTP_200_OK,
            payload=f"Book ID: {book_id}",
            message="The Book was successfully deleted from the cart",
        )

    except Exception as e:
        db.rollback()
        func_logger.exception(
            f"Failed to delete item from cart: book_id={book_id}, user_id={user.id}"
        )
        raise DBException()
