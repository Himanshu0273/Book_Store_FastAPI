from sqlalchemy.orm import Session
from app.models.roles_model import Roles

class RoleQueries:
    
    @staticmethod
    def get_role_by_id(id: int, db: Session)->Roles | None:
        return db.query(Roles).filter(Roles.id == id)
    
    @staticmethod
    def get_role_by_role_name(role_name: str, db: Session)->Roles | None:
        return db.query(Roles).filter(Roles.role_name == role_name)
    
    @staticmethod
    def check_if_role_is_same(id: int, role_name: str, db: Session)->Roles | None:
        return db.query(Roles).filter(Roles.role_name == role_name, Roles.id != id)
    
    
    
    