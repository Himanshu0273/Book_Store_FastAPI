from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.oauth2 import get_current_user
from app.auth.token import AccessToken
from app.config.load_config import api_settings
from app.config.logger_config import func_logger
from app.db.session import get_db
from app.exceptions.auth_exceptions import (InvalidCredentialsException,
                                            TokenCreationError)
from app.exceptions.db_exception import DBException
from app.models.user_model import User
from app.queries.user_queries import UserQueries
from app.schemas.user_schema import ShowUser
from app.utils.hash_password import Hash
from app.utils.response import build_response

user_router = APIRouter(prefix="/me", tags=["User"])
login_router = APIRouter(prefix="/auth/login", tags=["Auth"])


@user_router.get("/", response_model=ShowUser)
def show_user_details(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):

    func_logger.info(f"Fetching info for user: {current_user.id}")
    if not current_user.created_at:
        current_user.created_at = None

    return build_response(
        status_code=status.HTTP_200_OK,
        payload=current_user,
        message="Details for the current user fetched successfully!!",
    )


@login_router.post("/")
def login(
    request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    email = request.username
    password = request.password

    func_logger.info(f"Login attempt for email: {email}")

    try:
        user = UserQueries.get_user_by_email(email, db).first()

        if not user:
            func_logger.warning("No user with the given email found!!")
            raise InvalidCredentialsException()

        if not Hash.verify_password(password, user.password):
            func_logger.warning(f"Login failed — incorrect password for: {email}")
            raise InvalidCredentialsException()
        try:
            tokenobj = AccessToken(
                time_expire=30,
                secret_key=api_settings.SECRET_KEY,
                algorithm=api_settings.ALGORITHM,
            )
            access_token = tokenobj.create_access_token(data={"sub": str(user.id)})
            func_logger.info(f"Token generated for user ID: {user.id}")
            return {"access_token": access_token, "token_type": "bearer"}

        except Exception as e:
            func_logger.error(f"Token creation failed for user ID {user.id}: {e}")
            raise TokenCreationError()

    except SQLAlchemyError as e:
        func_logger.error(f"Database error during login for {email}: {e}")
        raise DBException(detail=f"Database error during login: {e}")
