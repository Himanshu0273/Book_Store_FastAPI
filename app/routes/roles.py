from fastapi import APIRouter, HTTPException, status, Depends
from app.db.session import get_db
from app.models.roles_model import Roles
from app.schemas import role_schema
from app.config.logger_config import func_logger
from sqlalchemy.orm import Session
from app.queries.role_queries import RoleQueries
from typing import List
from app.exceptions import db_exception

roles_router = APIRouter(prefix='/roles', tags=['Role'])

@roles_router.post('/create-role/', status_code=status.HTTP_201_CREATED,response_model=role_schema.ShowRoles)
def create_role(
    request: role_schema.CreateRoles,
    db: Session=Depends(get_db)
):
    func_logger.info("POST /roles/create-role - Create new role!!")
    
    try:
        existing_role = RoleQueries.get_role_by_role_name(request.role_name, db).first()
        
        if existing_role:
            func_logger.error("Role already exists!!")
            raise HTTPException(
                detail="Role exists",
                status_code= status.HTTP_400_BAD_REQUEST
            )
        
        role_data = request.model_dump()
        new_role = Roles(**role_data)
        db.add(new_role)
        db.commit()
        db.refresh(new_role)
        return new_role
    
    except Exception as e:
        db.rollback()
        func_logger.exception("Unexpected error while creating role") 
        raise db_exception.DBException(
            detail="DB Error when creating role!!"
        )
                
@roles_router.get('/get-all-roles/', status_code=status.HTTP_200_OK, response_model=List[role_schema.ShowRoles])
def get_all_roles(db: Session=Depends(get_db)):
    func_logger.info("GET /role/get-all-roles/ - Get list of all roles!")
    roles = db.query(Roles).all()
    return roles
  
@roles_router.get('/get-role-by-id/{id}', status_code=status.HTTP_200_OK)
def get_role_by_id(id: int, db: Session=Depends(get_db)):
    func_logger.info("GET /role/get-role-by-id/{id} - Get list of all roles!")
    role = RoleQueries.get_role_by_id(id, db).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The given ID not found!"
        )
    
    return role

@roles_router.put('/update-role/{id}', status_code=status.HTTP_202_ACCEPTED)
def update_role(id: int, request: role_schema.RolesUpdate, db:Session=Depends(get_db)):

    role = RoleQueries.get_role_by_id(id, db).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The role was not found!"
        )
            
    try:
        update_role = request.model_dump(exclude_unset=True)
        for key, value in update_role.items():
            setattr(role, key, value)
        
        db.commit()
        db.refresh(role)
         
    except Exception as e:
        db.rollback()
        func_logger.error("DB Error when updating role")
        raise db_exception.DBException(detail="DB Error while updating role")
    
    return "Role Updated Successfully!"
    
@roles_router.delete('/delete-role/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_role(id: int, db: Session = Depends(get_db)):
    func_logger.info(f"DELETE /role/delete-role/{id} - Attempting to delete role")

    role = RoleQueries.get_role_by_id(id, db).first()

    if not role:
        func_logger.warning(f"Role with ID {id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The role was not found!"
        )

    try:
        db.delete(role)
        db.commit()
        func_logger.info(f"Role with ID {id} deleted successfully.")
    except Exception as e:
        db.rollback()
        func_logger.error(f"Error deleting role ID {id}: {str(e)}")
        raise db_exception.DBException(detail="DB Error while deleting role")
        
    return "Role Deleted Successfully!!"