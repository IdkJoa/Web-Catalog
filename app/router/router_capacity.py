from typing import List
from uuid import UUID

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.db_connection import get_db
from app.schemas.Capacity import CapacityOut, CapacityCreate, CapacityBase
from app.services.Capacityservices import capacity_services

router = APIRouter(prefix="/capacity", tags=["capacity"],
                    responses = {status.HTTP_404_NOT_FOUND: {"message": "producto no encontrado"}})

@router.get("/", response_model=List[CapacityOut])
def get_capacity(db: Session = Depends(get_db)):
    try:
        capacity = capacity_services.get_multi(db)

        if capacity is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No hay capacidades activas")

        return capacity

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:

        raise HTTPException(

            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=f"Error interno: {str(e)}"
        )

@router.get("/{id}", response_model=CapacityOut)
def get_capacity(id: UUID, db: Session = Depends(get_db)):
    try:
        capacity = capacity_services.get(db, id=id)

        if capacity is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="capacidad no encontrado")
        return capacity

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )


@router.post("/create", response_model=CapacityOut)
def create_capacity(capacity: CapacityCreate, db: Session = Depends(get_db)):
    try:
        exist = capacity_services.get_byname(db, capacity.capacity)

        if exist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="capacity existente")

        capacity = capacity_services.create(db=db, obj_in=capacity)

        return capacity
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=f"Error interno del servidor: {str(e)}"
        )

@router.put("/update", response_model=CapacityOut)
def update_capacity(id: UUID, capacity: CapacityBase, db: Session = Depends(get_db)):
    try:
        exist = capacity_services.get(db, id)

        if exist is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="capacity no encontrado")

        capacity = capacity_services.update(db=db, obj_in=capacity, db_obj=exist)

        return capacity
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=f"Error interno del servidor: {str(e)}"
        )

@router.delete("/delete", response_model=CapacityOut)
def create_capacity(id: UUID, db: Session = Depends(get_db)):
    try:
        exist = capacity_services.get(db, id)

        if exist is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="capacity no encontrado")

        capacity = capacity_services.delete(db=db, id=id)

        return capacity
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=f"Error interno del servidor: {str(e)}"
        )