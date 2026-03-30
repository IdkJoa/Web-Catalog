import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.db_connection import get_db
from app.schemas.condition import ConditionOut, ConditionBase
from app.services.condition_service import condition_services

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/condition", tags=["Condition"],
                    responses = {status.HTTP_404_NOT_FOUND: {"message": "Condition no encontrado"}})

@router.get("/", response_model=List[ConditionOut])
def get_conditions(db: Session = Depends(get_db)):
    logger.debug("Fetching all conditions")
    try:
        conditions = condition_services.get_multi(db)

        if not conditions:
            logger.info("No active conditions found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No hay Conditions activas")

        return conditions

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error fetching conditions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.get("/{id}", response_model=ConditionOut, )
def get_condition_by_id(id: UUID, db: Session = Depends(get_db)):
    logger.debug(f"Fetching condition with id: {id}")
    try:
        condition = condition_services.get(db, id)

        if condition is None:
            logger.warning(f"Condition not found with id: {id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No existe esta condition")

        return condition

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error fetching condition {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )


@router.post("/create", response_model=ConditionOut, dependencies=[Depends(get_current_active_user)])
def create_condition(condition: ConditionBase, db: Session = Depends(get_db)):
    logger.info(f"Creating new condition: {condition.name}")
    try:
        exist = condition_services.get_byname(db, condition.name)
        if not exist is None:
            logger.warning(f"Conflict: Condition with name {condition.name} already exists")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="condition existe")

        new_condition = condition_services.create(db,obj_in=condition)
        logger.info(f"Condition created with id: {new_condition.id}")
        return new_condition

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error creating condition: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.put("/update/{id}", response_model=ConditionOut, dependencies=[Depends(get_current_active_user)])
def update_condition(condition: ConditionBase, id: UUID, db: Session = Depends(get_db)):
    logger.info(f"Updating condition with id: {id}")
    try:
        condition_exist = condition_services.get(db, id)
        if condition_exist is None:
            logger.warning(f"Update failed: Condition {id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No existe esta condition")

        updated_condition = condition_services.update(db,db_obj=condition_exist, obj_in=condition)
        logger.info(f"Condition {id} updated successfully")

        return updated_condition

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error updating condition {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )
@router.delete("/delete/{id}", response_model=ConditionOut, dependencies=[Depends(get_current_active_user)])
def delete_condition(id: UUID, db: Session = Depends(get_db)):
    logger.info(f"Deleting condition with id: {id}")
    try:
        condition_exist = condition_services.get(db, id)
        if condition_exist is None:
            logger.warning(f"Delete failed: Condition {id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No existe esta condition")

        deleted_condition = condition_services.delete(db, id=id)
        logger.info(f"Condition {id} deleted successfully")

        return deleted_condition

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error deleting condition {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )