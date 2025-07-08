from enum import Enum


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
