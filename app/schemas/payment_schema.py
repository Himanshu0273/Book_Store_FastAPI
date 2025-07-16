from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.utils.enums import PaymentsEnum, PaymentMethodEnum, TransactionStatusEnum

class CreatePayment(BaseModel):
    mode_of_payment: PaymentMethodEnum
    
    model_config = ConfigDict(from_attributes=True)

class TransactionResponse(BaseModel):
    id: int
    payment_id: int
    txn_reference: str
    status: TransactionStatusEnum
    message: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PaymentResponse(BaseModel):
    id: int
    order_id: int
    total_cost: float
    mode_of_payment: PaymentMethodEnum
    attempts: int
    status: PaymentsEnum
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaymentWithTransactions(BaseModel):
    id: int
    order_id: int
    total_cost: float
    mode_of_payment: PaymentMethodEnum
    attempts: int
    status: PaymentsEnum
    created_at: datetime
    transactions: List[TransactionResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class PaymentStatusResponse(BaseModel):
    payment_id: int
    order_id: int
    payment_status: PaymentsEnum
    attempts: int
    max_attempts: int = 3
    can_retry: bool
    last_transaction_status: Optional[TransactionStatusEnum] = None
    last_transaction_message: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class PaymentSummary(BaseModel):
    """Summary response for payment operations"""
    order_id: int
    payment_id: int
    status: PaymentsEnum
    attempts: int
    total_cost: float
    message: str
    
    model_config = ConfigDict(from_attributes=True)