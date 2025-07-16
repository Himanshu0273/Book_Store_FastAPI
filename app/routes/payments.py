from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.payment_schema import CreatePayment, PaymentResponse
from app.models.payments_model import Payments
from app.models.orders_model import Order
from app.models.user_model import User
from app.utils.enums import PaymentsEnum
from app.auth.permissions import is_customer
from typing import Optional
from app.config.logger_config import func_logger
from app.queries.payment_queries import PaymentQueries
from app.queries.order_queries import OrderQueries
from app.exceptions.order_exceptions import OrderNotFound
from app.services.simulate_payment import simulate_payment

payment_router = APIRouter(prefix="/payments", tags=["Payments"])

@payment_router.post("/start/{order_id}")
def start_payment(
    order_id: int,
    req: CreatePayment,
    background_tasks: BackgroundTasks,
    txn_status: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_customer)
):
    """
    Start payment process for an order
    - Creates payment record if doesn't exist
    - Handles retry logic for failed payments
    - Validates order ownership and status
    """
    order = OrderQueries.get_order_by_id(user_id=current_user.id, order_id=order_id, db=db)
    if not order:
        raise OrderNotFound(order_id=order_id)

    # Check if order is in valid state for payment
    if order.payment_status == PaymentsEnum.FAILED:
        raise HTTPException(
            status_code=400, 
            detail="Cannot process payment for cancelled order"
        )
    
    if order.payment_status == PaymentsEnum.SUCCESSFUL:
        raise HTTPException(
            status_code=400, 
            detail="Order already completed"
        )

    total_cost = order.total
    payment = PaymentQueries.get_payment_by_order_id(order_id=order_id, db=db)

    if not payment:
        # Create new payment record
        payment = Payments(
            order_id=order_id,
            total_cost=total_cost,
            mode_of_payment=req.mode_of_payment,
            status=PaymentsEnum.PENDING,
            attempts=0
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        func_logger.info(f"New payment created for order_id {order_id}")
    else:
        # Handle existing payment
        if payment.status == PaymentsEnum.SUCCESSFUL:
            raise HTTPException(
                status_code=400, 
                detail="Payment already successful"
            )
        elif payment.status == PaymentsEnum.FAILED:
            raise HTTPException(
                status_code=400, 
                detail="Payment failed after 3 attempts. Please create a new order."
            )
        elif payment.status == PaymentsEnum.PENDING and payment.attempts >= 3:
            raise HTTPException(
                status_code=400, 
                detail="Maximum payment attempts exceeded"
            )
        
        # Update payment method if different
        if payment.mode_of_payment != req.mode_of_payment:
            payment.mode_of_payment = req.mode_of_payment
            db.commit()
            func_logger.info(f"Payment method updated for payment_id {payment.id}")

    # Start background payment processing
    simulate_status = None
    if txn_status is not None:
        simulate_status = "success" if txn_status else "failure"
    
    background_tasks.add_task(simulate_payment,payment.id, simulate_status)
    
    func_logger.info(f"Payment simulation started for payment_id {payment.id}")
    return PaymentResponse.model_validate(payment)

@payment_router.get("/status/{order_id}")
def get_payment_status(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_customer)
):
    """
    Get payment status for an order
    """
    order = OrderQueries.get_order_by_id(user_id=current_user.id, order_id=order_id, db=db)
    if not order:
        raise OrderNotFound(order_id=order_id)
    
    payment = PaymentQueries.get_payment_by_order_id(order_id=order_id, db=db)
    if not payment:
        raise HTTPException(
            status_code=404,
            detail="No payment found for this order"
        )
    
    return PaymentResponse.model_validate(payment)

@payment_router.post("/retry/{order_id}")
def retry_payment(
    order_id: int,
    background_tasks: BackgroundTasks,
    txn_status: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_customer)
):
    """
    Retry payment for failed attempts (if attempts < 3)
    """
    order = OrderQueries.get_order_by_id(user_id=current_user.id, order_id=order_id, db=db)
    if not order:
        raise OrderNotFound(order_id=order_id)
    
    payment = PaymentQueries.get_payment_by_order_id(order_id=order_id, db=db)
    if not payment:
        raise HTTPException(
            status_code=404,
            detail="No payment found for this order"
        )
    
    if payment.status == PaymentsEnum.SUCCESSFUL:
        raise HTTPException(
            status_code=400,
            detail="Payment already successful"
        )
    
    if payment.attempts >= 3:
        raise HTTPException(
            status_code=400,
            detail="Maximum payment attempts exceeded"
        )
    
    # Start retry
    simulate_status = None
    if txn_status is not None:
        simulate_status = "success" if txn_status else "failure"
    
    background_tasks.add_task(simulate_payment, payment.id, simulate_status)
    
    return {"message": "Payment retry initiated", "attempts": payment.attempts}
    func_logger.info(f"Payment retry started for payment_id {payment.id}")