import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter,status,Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.db_connection import get_db
from app.schemas.category import CategoryBase, CategoryOut
from app.services.category_service import category_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/category", tags=["category"],
                    responses = {status.HTTP_404_NOT_FOUND: {"message": "category no encontrado"}})

@router.get("/", response_model=List[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    logger.debug("Fetching all categories")
    try:
        category = category_service.get_multi(db)

        if category is None:
            logger.info("No active categories found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No hay categories activas")

        return category

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.get("/{id}", response_model=CategoryOut)
def get_category_by_id(id: UUID, db: Session = Depends(get_db)):
    logger.debug(f"Fetching category with id: {id}")
    try:
        category = category_service.get(db, id)

        if category is None:
            logger.warning(f"Category not found with id: {id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No existe esta categoria")

        return category

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error fetching category {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.post("/create", response_model=CategoryOut, dependencies=[Depends(get_current_active_user)])
def create_category(category: CategoryBase, db: Session = Depends(get_db)):
    logger.info(f"Creating new category: {category.name}")
    try:
        exist = category_service.get_byname(db, category.name)
        if not exist is None:
            logger.warning(f"Conflict: Category with name {category.name} already exists")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Category existe")

        new_category = category_service.create(db,obj_in=category)
        logger.info(f"Category created with id: {new_category.id}")
        return new_category

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error creating category: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )
@router.put("/update/{id}", response_model=CategoryOut, dependencies=[Depends(get_current_active_user)])
def update_category(category: CategoryBase, id: UUID, db: Session = Depends(get_db)):
    logger.info(f"Updating category with id: {id}")
    try:
        categoria_exist = category_service.get(db, id)
        if categoria_exist is None:
            logger.warning(f"Update failed: Category {id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No existe esta categoria")

        updated_category = category_service.update(db,db_obj=categoria_exist, obj_in=category)
        logger.info(f"Category {id} updated successfully")

        return updated_category

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error updating category {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.delete("/delete/{id}", response_model=CategoryOut, dependencies=[Depends(get_current_active_user)])
def delete_category(id: UUID, db: Session = Depends(get_db)):
    logger.info(f"Deleting category with id: {id}")
    try:
        categoria_exist = category_service.get(db, id)
        if categoria_exist is None:
            logger.warning(f"Delete failed: Category {id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No existe esta categoria")

        deleted_category = category_service.delete(db, id=id)
        logger.info(f"Category {id} deleted successfully")

        return deleted_category

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error deleting category {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )