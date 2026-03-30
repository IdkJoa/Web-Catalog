from typing import List
from uuid import UUID

from fastapi import APIRouter,status,Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.db_connection import get_db
from app.schemas.category import CategoryBase, CategoryOut
from app.services.category_service import category_service

router = APIRouter(prefix="/category", tags=["category"],
                    responses = {status.HTTP_404_NOT_FOUND: {"message": "category no encontrado"}})

@router.get("/", response_model=List[CategoryOut])
def get_category(db: Session = Depends(get_db)):
    try:
        category = category_service.get_multi(db)

        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No hay categories activas")

        return category

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.get("/{id}", response_model=CategoryOut)
def get_category(id: UUID, db: Session = Depends(get_db)):
    try:
        category = category_service.get(db, id)

        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No existe esta categoria")

        return category

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.post("/create", response_model=CategoryOut, dependencies=[Depends(get_current_active_user)])
def create_category(category: CategoryBase, db: Session = Depends(get_db)):
    try:
        exist = category_service.get_byname(db, category.name)
        if not exist is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Category existe")

        category = category_service.create(db,obj_in=category)
        return category

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )
@router.put("/update/{id}", response_model=CategoryOut, dependencies=[Depends(get_current_active_user)])
def update_category(category: CategoryBase, id: UUID, db: Session = Depends(get_db)):
    try:
        categoria_exist = category_service.get(db, id)
        if categoria_exist is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No existe esta categoria")

        category = category_service.update(db,db_obj=categoria_exist, obj_in=category)

        return category

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.delete("/delete/{id}", response_model=CategoryOut, dependencies=[Depends(get_current_active_user)])
def delete_category(id: UUID, db: Session = Depends(get_db)):
    try:
        categoria_exist = category_service.get(db, id)
        if categoria_exist is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No existe esta categoria")

        category = category_service.delete(db, id=id)

        return category

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )