from fastapi import Depends

from app.auth.oauth2 import get_current_user
from app.config.logger_config import func_logger
from app.exceptions.auth_exceptions import ForbiddenAccess
from app.models.user_model import User


def is_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.role or current_user.role.role_name.lower() != "admin":
        func_logger.warning(f"Unauthorized role access: {current_user.role.role_name}")
        raise ForbiddenAccess()

    return current_user


def is_customer(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.role or current_user.role.role_name.lower() != "customer":
        func_logger.warning(f"Unauthorized role access: {current_user.role.role_name}")
        raise ForbiddenAccess()

    return current_user
