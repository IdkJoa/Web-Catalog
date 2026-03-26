from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.db_connection import get_db
from app.schemas.Brand import BrandOut, BrandBase
from app.services.Brandservices import brand_services

router = APIRouter(prefix="/brand", tags=["brand"],
                    responses = {status.HTTP_404_NOT_FOUND: {"message": "brand no encontrado"}})
@router.get("/", response_model=List[BrandOut])
def get_brand(db: Session = Depends(get_db)):
    try:
        brand = brand_services.get_multi(db)

        if brand is []:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No hay brand activas")

        return brand

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.get("/{id}", response_model=BrandOut)
def get_brand(id: UUID, db: Session = Depends(get_db)):
    try:
        brand = brand_services.get(db, id)

        if brand is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No existe esta brand")

        return brand

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )


@router.post("/create", response_model=BrandOut)
def create_brand(brand: BrandBase, db: Session = Depends(get_db)):
    try:
        exist = brand_services.get_byname(db, brand.name)
        if not exist is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="brand existe")

        brand = brand_services.create(db,obj_in=brand)
        return brand

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )
@router.put("/update", response_model=BrandOut)
def update_brand(brand: BrandBase, id: UUID, db: Session = Depends(get_db)):
    try:
        brand_exist = brand_services.get(db, id)
        if brand_exist is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No existe esta garantia")

        brand = brand_services.update(db,db_obj=brand_exist, obj_in=brand)

        return brand

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )
@router.delete("/delete", response_model=BrandOut)
def delete_brand(id: UUID, db: Session = Depends(get_db)):
    try:
        brand_exist = brand_services.get(db, id)
        if brand_exist is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No existe esta brand")

        brand = brand_services.delete(db, id=id)

        return brand

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )