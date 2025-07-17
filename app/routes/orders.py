from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.permissions import is_admin, is_customer
from app.config.logger_config import func_logger
from app.db.session import get_db
from app.exceptions.book_exceptions import BookNotFound
from app.exceptions.cart_exceptions import CartNotFound
from app.exceptions.db_exception import DBException
from app.exceptions.order_exceptions import OrderNotFound
from app.exceptions.shipping_cost_exceptions import CountryNotFound
from app.models.cart_model import Cart
from app.models.orders_model import Order
from app.models.user_model import User
from app.queries.book_queries import BookQueries
from app.queries.cart_queries import CartQueries
from app.queries.order_queries import OrderQueries
from app.queries.shipping_cost_queries import ShippingCostQueries
from app.routes.cart import get_cart
from app.schemas.cartitem_schema import ShowCartItem
from app.schemas.order_schema import (CreateOrderSchema, ShowOrderSchema,
                                      UpdateOrderSchema)
from app.utils.enums import CartActivityEnum, PaymentsEnum
from app.utils.response import build_response
from app.utils.tax_utils import calculate_tax

order_router = APIRouter(prefix="/order", tags=["Order"])


@order_router.post("/", status_code=status.HTTP_201_CREATED)
def create_order(
    request: CreateOrderSchema,
    cart: Cart = Depends(get_cart),
    db: Session = Depends(get_db),
    user: User = Depends(is_customer),
):
    func_logger.info(
        f"Order creation started for user_id={user.id} and cart_id={cart.id}"
    )

    try:
        cost = 0

        cart_items = CartQueries.get_all_cart_items(cart_id=cart.id, db=db)

        if not cart_items:
            func_logger.warning(f"Cart ID {cart.id} has no items.")
            raise CartNotFound()

        for item in cart_items:
            cartitem = ShowCartItem.model_validate(item)
            book = BookQueries.get_book_by_id(book_id=item.book_id, db=db)

            if not book:
                raise BookNotFound(book_id=item.book_id)

            available_quantity = book.inventory.quantity
            if cartitem.quantity > available_quantity:
                func_logger.warning(
                    f"Book ID {item.book_id} has insufficient stock. "
                    f"Requested: {cartitem.quantity}, Available: {available_quantity}"
                )
                raise HTTPException(
                    status_code=400,
                    detail=f"Book '{book.title}' has only {available_quantity} in stock. Please update your cart.",
                )

            book.inventory.quantity -= cartitem.quantity
            func_logger.debug(
                f"Decremented book_id={item.book_id} by {cartitem.quantity}"
            )
            cost += cartitem.quantity * cartitem.price_when_added

        shipping_obj = ShippingCostQueries.get_country_by_name(
            country_name=request.country, db=db
        )

        if not shipping_obj:
            func_logger.error(
                f"No shipping entry found for country '{request.country}'"
            )
            raise CountryNotFound(country=request.country)

        shipping_cost = shipping_obj.cost
        taxes = calculate_tax(cart_cost=cost, shipping_cost=shipping_cost)
        total_cost = cost + shipping_cost + taxes

        final_order = Order(
            user_id=user.id,
            cart_id=cart.id,
            cart_cost=cost,
            shipping_cost=shipping_cost,
            taxes=taxes,
            total=total_cost,
            shipping_address=request.shipping_address,
            country=request.country,
        )

        cart.status = CartActivityEnum.ORDERED
        db.add(final_order)

        func_logger.info(
            f"Order created. Total: ₹{total_cost:.2f}. Cart marked as ORDERED."
        )

        db.commit()
        db.refresh(final_order)

        func_logger.info(f"Order committed successfully with order_id={final_order.id}")

        return build_response(
            status_code=status.HTTP_201_CREATED,
            payload=ShowOrderSchema.model_validate(final_order),
            message="The order was placed successfully",
        )

    except SQLAlchemyError as e:
        db.rollback()
        func_logger.error(f"Transaction failed: {str(e)}")
        raise DBException(detail="Internal server error")

    except Exception as e:
        db.rollback()
        func_logger.exception("Unexpected error during order creation")
        raise DBException(detail="Unexpected error occurred")


# Get all order details of a customer
@order_router.get("/get-order-details", status_code=status.HTTP_200_OK)
def get_all_order(
    db: Session = Depends(get_db), current_user: User = Depends(is_customer)
):
    func_logger.info(f"Fetching all orders for user_id={current_user.id}")

    try:
        orders = OrderQueries.get_all_orders_of_customer(user_id=current_user.id, db=db)

        if not orders:
            func_logger.warning(f"No orders found for user_id={current_user.id}")
            return build_response(
                status_code=status.HTTP_200_OK,
                payload=[],
                message="No orders found for this user.",
            )

        func_logger.info(f"{len(orders)} orders fetched for user_id={current_user.id}")
        return build_response(
            status_code=status.HTTP_200_OK,
            payload=List[ShowOrderSchema].model_validate(orders),
            message="Orders fetched successfully",
        )

    except SQLAlchemyError as e:
        db.rollback()
        func_logger.error(f"Transaction failed: {str(e)}")
        raise DBException(detail="Could not fetch orders")

    except Exception as e:
        db.rollback()
        func_logger.exception("Unexpected error during order creation")
        raise DBException(detail="Unexpected error occurred")


# Get a specific order for a customer
@order_router.get("/get-order/{order_id}", status_code=status.HTTP_200_OK)
def get_user_order_by_id(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_customer),
):

    func_logger.info(f"User ID {current_user.id} requested order ID {order_id}")

    try:
        order = OrderQueries.get_order_by_id(
            user_id=current_user.id, order_id=order_id, db=db
        )

        if not order:
            func_logger.warning(
                f"Order ID {order_id} not found for user_id={current_user.id}"
            )
            raise OrderNotFound(order_id=order_id)

        func_logger.info(
            f"Order ID {order_id} fetched successfully for user_id={current_user.id}"
        )
        return build_response(
            status_code=status.HTTP_200_OK,
            payload=ShowOrderSchema.model_validate(order),
            message="Order fetched successfully",
        )

    except SQLAlchemyError as e:
        db.rollback()
        func_logger.error(f"DB Error while fetching order_id={order_id}: {str(e)}")
        raise DBException()

    except Exception as e:
        db.rollback()
        func_logger.exception(f"Unexpected error while fetching order_id={order_id}")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")


# Update address in the order
@order_router.patch(
    "/update-address-in-address/{order_id}", status_code=status.HTTP_202_ACCEPTED
)
def update_address_in_order(
    request: UpdateOrderSchema,
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_customer),
):
    func_logger.info(
        f"User ID {current_user.id} requested address update for order ID {order_id}"
    )

    try:
        order = OrderQueries.get_order_by_id(
            order_id=order_id, user_id=current_user.id, db=db
        )

        if not order:
            func_logger.warning(
                f"Order ID {order_id} not found for user_id={current_user.id}"
            )
            raise OrderNotFound(order_id=order_id)

        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(order, key, value)

        db.commit()
        db.refresh(order)

        func_logger.info(
            f"Order ID {order_id} updated successfully by user_id={current_user.id}"
        )
        return build_response(
            status_code=status.HTTP_202_ACCEPTED,
            payload=order,
            message="Order updated successfully",
        )

    except SQLAlchemyError as e:
        db.rollback()
        func_logger.error(
            f"Database error while updating order_id={order_id}: {str(e)}"
        )
        raise DBException()

    except Exception as e:
        db.rollback()
        func_logger.exception(f"Unexpected error while updating order_id={order_id}")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")


# Delete order
@order_router.delete("/delete-order/{order_id}", status_code=status.HTTP_200_OK)
def delete_order_by_customer(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_customer),
):
    func_logger.info(
        f"Attempting to delete order_id={order_id} for user_id={current_user.id}"
    )

    try:
        order = OrderQueries.get_order_by_id(
            user_id=current_user.id, order_id=order_id, db=db
        )
        if not order:
            func_logger.warning(
                f"Order ID {order_id} not found for user_id={current_user.id}"
            )
            raise OrderNotFound(order_id=order_id)

        cart_id = order.cart_id
        cart_items = CartQueries.get_items_of_ordered_cart(cart_id=cart_id, db=db)

        if not cart_items:
            func_logger.warning(f"No cart items found for cart_id={cart_id}")

        for item in cart_items:
            cart_item = ShowCartItem.model_validate(item)
            book = BookQueries.get_book_by_id(book_id=item.book_id, db=db)
            if not book:
                func_logger.error(
                    f"Book ID {item.book_id} not found while restoring quantity."
                )
                raise BookNotFound(book_id=item.book_id)

            book.inventory.quantity += cart_item.quantity
            func_logger.debug(
                f"Restored {cart_item.quantity} to book_id={item.book_id}"
            )

        # Mark cart as cancelled
        order.cart.status = CartActivityEnum.CANCELLED
        func_logger.info(f"Cart ID {cart_id} status set to CANCELLED")

        db.delete(order)
        db.commit()
        func_logger.info(
            f"Order ID {order_id} deleted successfully for user_id={current_user.id}"
        )
        return build_response(
            status_code=status.HTTP_200_OK,
            payload=order_id,
            message=f"The order is deleted successfully",
        )

    except SQLAlchemyError as e:
        db.rollback()
        func_logger.error(
            f"Transaction failed while deleting order_id={order_id}: {str(e)}"
        )
        raise DBException(detail="Database error while deleting order")

    except Exception as e:
        db.rollback()
        func_logger.exception("Unexpected error while deleting order")
        raise DBException(detail="Unexpected error occurred during order deletion")
