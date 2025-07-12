from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.permissions import is_admin
from app.config.logger_config import func_logger
from app.db.session import get_db
from app.exceptions.db_exception import DBException
from app.exceptions.shipping_cost_exceptions import CountryNotFound
from app.models.shipping_cost_model import ShippingCost
from app.models.user_model import User
from app.queries.shipping_cost_queries import ShippingCostQueries
from app.schemas.shipping_cost_schema import (CreateShippingCost,
                                              ShowShippingCost,
                                              UpdateShippingCost)
from app.utils.response import build_response

shipping_router = APIRouter(prefix="/shipping-cost", tags=["Shipping Cost"])


# Add a country
@shipping_router.post("/add-cost", status_code=status.HTTP_201_CREATED)
def create_cost_row(
    request: CreateShippingCost,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin),
):
    func_logger.info("POST - /shipping-cost/add-cost")

    try:
        new_cost = ShippingCost(**request.model_dump())
        db.add(new_cost)
        db.commit()
        db.refresh(new_cost)
        return build_response(
            status_code=status.HTTP_201_CREATED,
            payload=new_cost,
            message="New cost for a country added!!",
        )

    except SQLAlchemyError as e:
        db.rollback()
        func_logger.error(f"DB error while creating shipping cost: {e}")
        raise DBException


# Get all countries
@shipping_router.get("/", status_code=status.HTTP_200_OK)
def get_all_countries(db: Session = Depends(get_db)):
    func_logger.info("GET - /shipping-cost/ | Fetching all countries")

    try:
        rows = ShippingCostQueries.get_all_rows(db=db)
        func_logger.info(f"Fetched {len(rows)} shipping cost rows successfully")

        return build_response(
            status_code=status.HTTP_200_OK,
            payload=rows,
            message="All the countries with shipping cost fetched successfully",
        )

    except Exception as e:
        func_logger.error(f"Error fetching all shipping cost rows: {e}")
        db.rollback()
        raise DBException()


# Get country by name
@shipping_router.get("/{country_name}", status_code=status.HTTP_200_OK)
def get_country_by_name(country_name: str, db: Session = Depends(get_db)):
    func_logger.info(f"GET - /shipping-cost/{country_name} | Fetching cost for country")

    try:
        cost = ShippingCostQueries.get_country_by_name(country_name=country_name, db=db)

        if not cost:
            func_logger.warning(f"Country not found: {country_name}")
            raise CountryNotFound(country=country_name)

        func_logger.info(f"Fetched shipping cost for country: {country_name}")

        return build_response(
            status_code=status.HTTP_200_OK,
            payload=cost,
            message=f"The cost for the country: {country_name} is fetched successfully!!",
        )

    except Exception as e:
        func_logger.error(f"Error fetching shipping cost for {country_name}: {e}")
        db.rollback()
        raise DBException()


# Update rows
@shipping_router.patch("/{id}", status_code=status.HTTP_202_ACCEPTED)
def update_row(
    id: int,
    request: UpdateShippingCost,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin),
):
    func_logger.info(f"PATCH - /shipping-cost/{id} | Attempting to update row")

    try:
        row = ShippingCostQueries.get_country_by_id(id=id, db=db)
        if not row:
            func_logger.warning(f"ShippingCost row not found for ID: {id}")
            raise CountryNotFound(country=id)

        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(row, key, value)

        db.commit()
        db.refresh(row)

        func_logger.info(f"ShippingCost row with ID {id} updated successfully")

        return build_response(
            status_code=status.HTTP_202_ACCEPTED,
            payload=row,
            message=f"Shipping cost for ID {id} updated successfully",
        )

    except CountryNotFound:
        raise
    except Exception as e:
        db.rollback()
        func_logger.error(f"Error updating shipping cost row {id}: {e}")
        raise DBException()


# Delete country
@shipping_router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_country(
    id: int, db: Session = Depends(get_db), current_user: User = Depends(is_admin)
):
    func_logger.info(f"DELETE - /shipping-cost/{id} | Attempting to delete row")

    try:
        row = ShippingCostQueries.get_country_by_id(id=id, db=db)
        if not row:
            func_logger.warning(f"ShippingCost row not found for ID: {id}")
            raise CountryNotFound(country=id)

        db.delete(row)
        db.commit()

        func_logger.info(f"ShippingCost row with ID {id} deleted successfully")

        return build_response(
            status_code=status.HTTP_200_OK,
            payload={"deleted_id": id},
            message=f"Shipping cost for ID {id} deleted successfully",
        )

    except Exception as e:
        db.rollback()
        func_logger.error(f"Error deleting shipping cost row {id}: {e}")
        raise DBException()
