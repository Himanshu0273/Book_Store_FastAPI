from enum import Enum


# Enum for genre of the books
class GenreEnum(str, Enum):
    FANTASY = "fantasy"
    SCI_FI = "sci-fi"
    MYSTERY = "mystery"
    THRILLER = "thriller"
    ROMANCE = "romance"
    ADVENTURE = "adventure"
    AUTOBIOGRAPHY = "autobiography"
    SELF_HELP = "self-help"
    BUSINESS = "business"
    TRUE_CRIME = "true-crime"
    HEALTH_AND_WELLNESS = "health-and-wellness"
    RELIGION = "religion"


class CartActivityEnum(str, Enum):
    ACTIVE = "ACTIVE"
    ORDERED = "ORDERED"
    CANCELLED = "CANCELLED"


class PaymentsEnum(str, Enum):
    PENDING = "PENDING"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"


class PaymentMethodEnum(str, Enum):
    UPI = "UPI"
    COD = "COD"
    CARD = "CARD"
    NETBANKING = "NETBANKING"


class TransactionStatusEnum(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    
# class OrderStatusEnum(str, Enum):
#     PENDING = "PENDING"
#     CONFIRMED = "CONFIRMED"
#     COMPLETED = "COMPLETED"
#     CANCELLED = "CANCELLED"