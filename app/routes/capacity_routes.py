import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.db_connection import get_db
from app.schemas.capacity import CapacityOut, CapacityCreate, CapacityBase
from app.services.capacity_service import capacity_services

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/capacity", tags=["capacity"],
                    responses = {status.HTTP_404_NOT_FOUND: {"message": "producto no encontrado"}})

@router.get("/", response_model=List[CapacityOut])
def get_capacities(db: Session = Depends(get_db)):
    logger.debug("Fetching all capacities")
    try:
        capacity = capacity_services.get_multi(db)

        if capacity is None:
            logger.info("No active capacities found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No hay capacidades activas")

        return capacity

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error fetching capacities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.get("/{id}", response_model=CapacityOut)
def get_capacity_by_id(id: UUID, db: Session = Depends(get_db)):
    logger.debug(f"Fetching capacity with id: {id}")
    try:
        capacity = capacity_services.get(db, id=id)

        if capacity is None:
            logger.warning(f"Capacity not found with id: {id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="capacidad no encontrado")
        return capacity

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error fetching capacity {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )


@router.post("/create", response_model=CapacityOut, dependencies=[Depends(get_current_active_user)])
def create_capacity(capacity: CapacityCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating new capacity for product: {capacity.product_id}")
    try:
        exist = capacity_services.get_byname(db, capacity.capacity)

        if exist:
            logger.warning(f"Conflict: Capacity {capacity.capacity} already exists")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="capacity existente")

        new_capacity = capacity_services.create(db=db, obj_in=capacity)
        logger.info(f"Capacity created with id: {new_capacity.id}")

        return new_capacity
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error creating capacity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.put("/update/{id}", response_model=CapacityOut, dependencies=[Depends(get_current_active_user)])
def update_capacity(id: UUID, capacity: CapacityBase, db: Session = Depends(get_db)):
    logger.info(f"Updating capacity with id: {id}")
    try:
        exist = capacity_services.get(db, id)

        if exist is None:
            logger.warning(f"Update failed: Capacity {id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="capacity no encontrado")

        updated_capacity = capacity_services.update(db=db, obj_in=capacity, db_obj=exist)
        logger.info(f"Capacity {id} updated successfully")

        return updated_capacity
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error updating capacity {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.delete("/delete/{id}", response_model=CapacityOut, dependencies=[Depends(get_current_active_user)])
def delete_capacity(id: UUID, db: Session = Depends(get_db)):
    logger.info(f"Deleting capacity with id: {id}")
    try:
        exist = capacity_services.get(db, id)

        if exist is None:
            logger.warning(f"Delete failed: Capacity {id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="capacity no encontrado")

        deleted_capacity = capacity_services.delete(db=db, id=id)
        logger.info(f"Capacity {id} deleted successfully")

        return deleted_capacity
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error deleting capacity {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )