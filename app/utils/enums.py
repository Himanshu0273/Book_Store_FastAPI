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
    ACTIVE = "active"
    ORDERED = "ordered"
    CANCELLED = "cancelled"


class PaymentsEnum(str, Enum):
    PENDING = "PENDING"
    SUCCESSFUL = "SUCCESSFULL"
    FAILED = "FAILED"
