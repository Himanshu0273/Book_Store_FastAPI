from fastapi import APIRouter, HTTPException,status,Depends
from sqlalchemy.orm import Session
from app.models.user_model import User
from app.schemas import user_schema
from app.db.session import get_db
from app.config.logger_config import func_logger
from app.queries import user_queries, role_queries
from app.utils.hash_password import Hash
from app.exceptions import db_exception, user_exceptions

user_router = APIRouter(prefix='/user', tags=['User'])
@user_router.post("/add-user/", response_model=user_schema.ShowUser, status_code=status.HTTP_201_CREATED)
def create_user(req: user_schema.CreateUser, db: Session = Depends(get_db)):
    """
    Create a new user if email and role are valid.
    """
    func_logger.info("POST /admin - Create new Admin!")

    try:
        existing_email = user_queries.UserQueries.get_user_by_email(req.email, db).first()
        if existing_email:
            func_logger.error(f"Email already exists: {req.email}")
            raise user_exceptions.UserEmailAlreadyInUse()

        role_exists = role_queries.RoleQueries.get_role_by_id(req.role_id, db).first()
        if not role_exists:
            func_logger.error("Roles not found!!")
            raise user_exceptions.RoleDoesNotExist()

        user_data = req.model_dump()
        user_data["password"] = Hash.hash_password(req.password)
        new_user = User(**user_data)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except Exception as e:
        db.rollback()
        func_logger.exception(f"DB Error when creating user: {e}")
        raise db_exception.DBException(detail="DB Error while creating user")

        
@user_router.get("/", response_model=list[user_schema.ShowUser])
def get_all_users(db: Session = Depends(get_db)):
    func_logger.info("GET /user/ - Get all users")
    try:
        return user_queries.UserQueries.get_all_users(db)
    except Exception as e:
        func_logger.exception(F"DB Error while fetching all users: {e}")
        raise db_exception.DBException("DB Error while fetching all users")


@user_router.get("/{user_id}", response_model=user_schema.ShowUser)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    func_logger.info(f"GET /user/{user_id} - Get user by ID")
    try:
        user = user_queries.UserQueries.get_user_by_id(user_id, db).first()
        if not user:
            raise user_exceptions.UserNotFound(user_id)
        return user
    except Exception as e:
        func_logger.exception(f"DB Error while fetching user by ID: {e}")
        raise db_exception.DBException("DB Error while fetching user by ID")


@user_router.put("/{user_id}", response_model=user_schema.ShowUser)
def update_user(user_id: int, req: user_schema.UpdateUser, db: Session = Depends(get_db)):
    func_logger.info(f"PUT /user/{user_id} - Update user")
    try:
        user = user_queries.UserQueries.get_user_by_id(user_id, db).first()
        if not user:
            raise user_exceptions.UserNotFound(user_id)
        
        if req.email:
            email_taken = user_queries.UserQueries.check_if_same_email(req.email, user_id, db).first()
            if email_taken:
                raise user_exceptions.UserEmailAlreadyInUse()

        if req.role_id:
            role_exists = role_queries.RoleQueries.get_role_by_id(req.role_id, db).first()
            if not role_exists:
                raise user_exceptions.RoleDoesNotExist()

        update_data = req.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["password"] = Hash.hash_password(update_data["password"])

        for key, value in update_data.items():
            setattr(user, key, value)

        db.commit()
        db.refresh(user)
        return user

    except Exception as e:
        db.rollback()
        func_logger.exception(f"DB Error while updating user: {e}")
        raise db_exception.DBException("DB Error while updating user")


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    func_logger.info(f"DELETE /user/{user_id} - Delete user")
    try:
        user = user_queries.UserQueries.get_user_by_id(user_id, db).first()
        if not user:
            raise user_exceptions.UserNotFound(user_id)

        db.delete(user)
        db.commit()
        return "User Deleted Successfully!!"
    
    except Exception as e:
        db.rollback()
        func_logger.exception(f"DB Error while deleting user: {e}")
        raise db_exception.DBException("DB Error while deleting user")
