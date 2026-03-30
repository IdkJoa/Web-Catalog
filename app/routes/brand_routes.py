from opentelemetry import trace
from opentelemetry.sdk.resources import logger
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.db_connection import get_db
from app.schemas.brand import BrandOut, BrandBase
from app.services.brand_service import brand_services

tracer = trace.get_tracer(__name__)

router = APIRouter(
    prefix="/brand",
    tags=["brand"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "brand no encontrado"}},
)


@router.get("/", response_model=List[BrandOut])
def get_brands(db: Session = Depends(get_db)):
    with tracer.start_as_current_span("get_brands") as span:
        try:
            brands = brand_services.get_multi(db)

            if not brands:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No hay brand activas",
                )

            span.set_attribute("http.status_code", 200)
            span.set_attribute("brands.count", len(brands))
            logger.info("Brands devueltas con éxito")
            return brands

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en get_brands: {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en get_brands: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}",
            )


@router.get("/{id}", response_model=BrandOut)
def get_brand_by_id(id: UUID, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("get_brand_by_id") as span:
        try:
            span.set_attribute("brand.id", str(id))
            brand = brand_services.get(db, id)

            if brand is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No existe esta brand",
                )

            span.set_attribute("http.status_code", 200)
            logger.info(f"Brand {id} devuelta con éxito")
            return brand

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en get_brand_by_id (id={id}): {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en get_brand_by_id (id={id}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}",
            )


@router.post("/create", response_model=BrandOut, dependencies=[Depends(get_current_active_user)])
def create_brand(brand: BrandBase, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("create_brand") as span:
        try:
            span.set_attribute("brand.name", brand.name)
            exist = brand_services.get_byname(db, brand.name)

            if exist is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="brand existe",
                )

            new_brand = brand_services.create(db, obj_in=brand)

            span.set_attribute("http.status_code", 201)
            span.set_attribute("brand.id", str(new_brand.id))
            logger.info(f"Brand '{brand.name}' creada con éxito (id={new_brand.id})")
            return new_brand

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en create_brand (name={brand.name}): {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en create_brand (name={brand.name}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}",
            )


@router.put("/update/{id}", response_model=BrandOut, dependencies=[Depends(get_current_active_user)])
def update_brand(brand: BrandBase, id: UUID, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("update_brand") as span:
        try:
            span.set_attribute("brand.id", str(id))
            brand_exist = brand_services.get(db, id)

            if brand_exist is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No existe esta garantia",
                )

            updated = brand_services.update(db, db_obj=brand_exist, obj_in=brand)

            span.set_attribute("http.status_code", 200)
            logger.info(f"Brand {id} actualizada con éxito")
            return updated

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en update_brand (id={id}): {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en update_brand (id={id}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}",
            )


@router.delete("/delete/{id}", response_model=BrandOut, dependencies=[Depends(get_current_active_user)])
def delete_brand(id: UUID, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("delete_brand") as span:
        try:
            span.set_attribute("brand.id", str(id))
            brand_exist = brand_services.get(db, id)

            if brand_exist is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No existe esta brand",
                )

            deleted = brand_services.delete(db, id=id)

            span.set_attribute("http.status_code", 200)
            logger.info(f"Brand {id} eliminada con éxito")
            return deleted

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en delete_brand (id={id}): {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en delete_brand (id={id}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}",
            )