from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session, joinedload

from app.auth.token import AccessToken
from app.config.load_config import api_settings
from app.config.logger_config import func_logger
from app.db.session import get_db
from app.exceptions.auth_exceptions import CredentialsException
from app.models.user_model import User
from app.utils.response import build_response

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    try:
        func_logger.info("Get Current User function...")

        tokenobj = AccessToken(
            api_settings.ALGORITHM, time_expire=30, secret_key=api_settings.SECRET_KEY
        )
        token_data = tokenobj.verify_access_token(
            token=token, credentials_exception=CredentialsException
        )
        # user=db.query(User).filter(token_data.user_id == User.id).first()
        user = (
            db.query(User)
            .options(joinedload(User.role))
            .filter(token_data.user_id == User.id)
            .first()
        )

        if not user:
            func_logger.exception("User not found during Authentication!!")
            raise CredentialsException

        return user

    except JWTError as e:
        func_logger.exception(f"A JWTError occured while fetching user: {e}")
        raise CredentialsException
