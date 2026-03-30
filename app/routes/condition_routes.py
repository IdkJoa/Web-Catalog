from typing import List
from uuid import UUID

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.db_connection import get_db
from app.schemas.condition import ConditionOut, ConditionBase
from app.services.condition_service import condition_services

router = APIRouter(prefix="/condition", tags=["Condition"],
                    responses = {status.HTTP_404_NOT_FOUND: {"message": "Condition no encontrado"}})

@router.get("/", response_model=List[ConditionOut])
def get_condition(db: Session = Depends(get_db)):
    try:
        conditions = condition_services.get_multi(db)

        if not conditions:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No hay Conditions activas")

        return conditions

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.get("/{id}", response_model=ConditionOut, )
def get_condition(id: UUID, db: Session = Depends(get_db)):
    try:
        condition = condition_services.get(db, id)

        if condition is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No existe esta condition")

        return condition

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )


@router.post("/create", response_model=ConditionOut, dependencies=[Depends(get_current_active_user)])
def create_condition(condition: ConditionBase, db: Session = Depends(get_db)):
    try:
        exist = condition_services.get_byname(db, condition.name)
        if not exist is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="condition existe")

        condition = condition_services.create(db,obj_in=condition)
        return condition

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.put("/update/{id}", response_model=ConditionOut, dependencies=[Depends(get_current_active_user)])
def update_condition(condition: ConditionBase, id: UUID, db: Session = Depends(get_db)):
    try:
        condition_exist = condition_services.get(db, id)
        if condition_exist is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No existe esta condition")

        condition = condition_services.update(db,db_obj=condition_exist, obj_in=condition)

        return condition

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )
@router.delete("/delete/{id}", response_model=ConditionOut, dependencies=[Depends(get_current_active_user)])
def delete_condition(id: UUID, db: Session = Depends(get_db)):
    try:
        condition_exist = condition_services.get(db, id)
        if condition_exist is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No existe esta condition")

        condition = condition_services.delete(db, id=id)

        return condition

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )