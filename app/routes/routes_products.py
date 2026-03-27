
from typing import List
from uuid import UUID

from fastapi import APIRouter,status,Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.db_connection import get_db
from app.schemas.Products import ProductCreate, ProductOut, ProductUpdate
from app.services.ProductsServices import product_services

router = APIRouter(prefix="/products", tags=["products"],
                    responses = {status.HTTP_404_NOT_FOUND: {"message": "producto no encontrado"}})

@router.get("/", response_model=List[ProductOut])
def get_products(db: Session = Depends(get_db)):
    try:
        products = product_services.get_multi(db)

        if products is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No hay productos activos")

        return products

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:

        raise HTTPException(

            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=f"Error interno: {str(e)}"
        )

@router.get("/{id}", response_model=ProductOut)
def get_product( id: UUID, db: Session = Depends(get_db)):
    try:
        product = product_services.get(db, id=id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Producto no encontrado")
        return product
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )


@router.post("/create", response_model=ProductOut)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    try:
        exist = product_services.get_byname(db, product.model_name)

        if exist:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Producto existente")

        product = product_services.create(db=db, obj_in=product)

        return product

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=f"Error interno del servidor: {str(e)}"
        )

@router.put("/update/{id}", response_model=ProductOut)
def update_product(id: UUID, product: ProductUpdate, db: Session = Depends(get_db)):
    try:
        exist = product_services.get(db, id)

        if exist is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Producto no encontrado")

        product = product_services.update(db=db, obj_in=product, db_obj=exist)

        return product
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=f"Error interno del servidor: {str(e)}"
        )

@router.delete("/delete/{id}", response_model=ProductOut)
def delete_product(id: UUID, db: Session = Depends(get_db)):
    try:
        exist = product_services.get(db, id)

        if exist is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Producto no encontrado")

        product = product_services.delete(db=db, id=id)

        return product
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=f"Error interno del servidor: {str(e)}"
        )