from sqlalchemy.orm import Session
from app.models.user_model import User

class UserQueries:
    
    @staticmethod
    def get_user_by_id(id: int, db: Session) -> User | None:
        return db.query(User).filter(User.id == id)
    
    @staticmethod
    def get_user_by_email(email: str, db: Session) -> User | None:
        return db.query(User).filter(User.email == email)
    
    @staticmethod
    def check_if_same_email(updated_email: str, id: int, db: Session) -> User | None:
        return db.query(User).filter(User.email == updated_email, User.id != id)
    
    @staticmethod
    def get_all_users(db: Session) -> User | None:
        return db.query(User).all()