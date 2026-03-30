import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.db_connection import get_db
from app.schemas.brand import BrandOut, BrandBase
from app.services.brand_service import brand_services

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/brand", tags=["brand"],
                    responses = {status.HTTP_404_NOT_FOUND: {"message": "brand no encontrado"}})
@router.get("/", response_model=List[BrandOut])
def get_brand(db: Session = Depends(get_db)):
    logger.debug("Fetching all brands")
    try:
        brand = brand_services.get_multi(db)

        if not brand:
            logger.info("No active brands found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No hay brand activas")

        return brand

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error fetching brands: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.get("/{id}", response_model=BrandOut)
def get_brand_by_id(id: UUID, db: Session = Depends(get_db)):
    logger.debug(f"Fetching brand with id: {id}")
    try:
        brand = brand_services.get(db, id)

        if brand is None:
            logger.warning(f"Brand not found with id: {id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No existe esta brand")

        return brand

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error fetching brand {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )


@router.post("/create", response_model=BrandOut, dependencies=[Depends(get_current_active_user)])
def create_brand(brand: BrandBase, db: Session = Depends(get_db)):
    logger.info(f"Creating new brand: {brand.name}")
    try:
        exist = brand_services.get_byname(db, brand.name)
        if not exist is None:
            logger.warning(f"Conflict: Brand with name {brand.name} already exists")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="brand existe")

        new_brand = brand_services.create(db,obj_in=brand)
        logger.info(f"Brand created with id: {new_brand.id}")
        return new_brand

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error creating brand: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )
@router.put("/update/{id}", response_model=BrandOut, dependencies=[Depends(get_current_active_user)])
def update_brand(brand: BrandBase, id: UUID, db: Session = Depends(get_db)):
    logger.info(f"Updating brand with id: {id}")
    try:
        brand_exist = brand_services.get(db, id)
        if brand_exist is None:
            logger.warning(f"Update failed: Brand {id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No existe esta garantia")

        updated_brand = brand_services.update(db,db_obj=brand_exist, obj_in=brand)
        logger.info(f"Brand {id} updated successfully")

        return updated_brand

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error updating brand {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )
@router.delete("/delete/{id}", response_model=BrandOut, dependencies=[Depends(get_current_active_user)])
def delete_brand(id: UUID, db: Session = Depends(get_db)):
    logger.info(f"Deleting brand with id: {id}")
    try:
        brand_exist = brand_services.get(db, id)
        if brand_exist is None:
            logger.warning(f"Delete failed: Brand {id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No existe esta brand")

        deleted_brand = brand_services.delete(db, id=id)
        logger.info(f"Brand {id} deleted successfully")

        return deleted_brand

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error deleting brand {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )