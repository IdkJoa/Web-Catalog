from opentelemetry import trace
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, logger
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from typing import List
from uuid import UUID
from fastapi import APIRouter,status,Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_active_user
from app.db.db_connection import get_db
from app.schemas.products import ProductCreate, ProductOut, ProductUpdate
from app.services.products_service import product_services

tracer = trace.get_tracer(__name__)

router = APIRouter(prefix="/products", tags=["products"],
                    responses = {status.HTTP_404_NOT_FOUND: {"message": "producto no encontrado"}})

@router.get("/", response_model=List[ProductOut])
def get_products(db: Session = Depends(get_db)):
    with tracer.start_as_current_span("get_products") as span:
     try:
        products = product_services.get_multi(db)

        if products is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No hay productos activos")
        with tracer.start_as_current_span("get_products") as span:
            span.set_attribute("status", 200)
            logger.info("productos devueltos con exito")
        return products

     except HTTPException as http_exc:
        span.record_exception(http_exc)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc)))
        logger.error(f"Error en get_products: {str(http_exc)}")
        raise http_exc
     except Exception as e:
        span.record_exception(e)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
        logger.error(f"Error en get_products: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=f"Error interno: {str(e)}"
        )
@router.get("/offers", response_model=List[ProductOut])
def get_offers(db: Session = Depends(get_db)):
    try:
        products = product_services.get_byoffer(db)
        return products
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

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


@router.get("/category/{category_id}", response_model=List[ProductOut])
def get_by_category(category_id: UUID, db: Session = Depends(get_db)):
    try:
        products = product_services.get_by_category(db, category_id)
        if not products:
            raise HTTPException(status_code=404, detail="No hay productos en esta categoria")
        return products
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/brand/{brand_id}", response_model=List[ProductOut])
def get_by_brand(brand_id: UUID, db: Session = Depends(get_db)):
    try:
        products = product_services.get_by_brand(db, brand_id)
        if not products:
            raise HTTPException(status_code=404, detail="No hay productos de esta marca")
        return products
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/create", response_model=ProductOut, dependencies=[Depends(get_current_active_user)])
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

@router.put("/update/{id}", response_model=ProductOut, dependencies=[Depends(get_current_active_user)])
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

@router.delete("/delete/{id}", response_model=ProductOut, dependencies=[Depends(get_current_active_user)])
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