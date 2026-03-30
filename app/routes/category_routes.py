from opentelemetry import trace
from opentelemetry.sdk.resources import logger
from typing import List
from uuid import UUID

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.db_connection import get_db
from app.schemas.category import CategoryBase, CategoryOut
from app.services.category_service import category_service

tracer = trace.get_tracer(__name__)

router = APIRouter(
    prefix="/category",
    tags=["category"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "category no encontrado"}},
)


@router.get("/", response_model=List[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    with tracer.start_as_current_span("get_categories") as span:
        try:
            categories = category_service.get_multi(db)

            if categories == []:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No hay categories activas",
                )

            span.set_attribute("http.status_code", 200)
            span.set_attribute("categories.count", len(categories))
            logger.info("Categorías devueltas con éxito")
            return categories

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en get_categories: {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en get_categories: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}",
            )


@router.get("/{id}", response_model=CategoryOut)
def get_category_by_id(id: UUID, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("get_category_by_id") as span:
        try:
            span.set_attribute("category.id", str(id))
            category = category_service.get(db, id)

            if category is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No existe esta categoria",
                )

            span.set_attribute("http.status_code", 200)
            logger.info(f"Categoría {id} devuelta con éxito")
            return category

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en get_category_by_id (id={id}): {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en get_category_by_id (id={id}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}",
            )


@router.post("/create", response_model=CategoryOut, dependencies=[Depends(get_current_active_user)])
def create_category(category: CategoryBase, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("create_category") as span:
        try:
            span.set_attribute("category.name", category.name)
            exist = category_service.get_byname(db, category.name)

            if exist is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Category existe",
                )

            new_category = category_service.create(db, obj_in=category)

            span.set_attribute("http.status_code", 201)
            span.set_attribute("category.id", str(new_category.id))
            logger.info(f"Categoría '{category.name}' creada con éxito (id={new_category.id})")
            return new_category

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en create_category (name={category.name}): {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en create_category (name={category.name}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}",
            )


@router.put("/update/{id}", response_model=CategoryOut, dependencies=[Depends(get_current_active_user)])
def update_category(category: CategoryBase, id: UUID, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("update_category") as span:
        try:
            span.set_attribute("category.id", str(id))
            categoria_exist = category_service.get(db, id)

            if categoria_exist is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No existe esta categoria",
                )

            updated = category_service.update(db, db_obj=categoria_exist, obj_in=category)

            span.set_attribute("http.status_code", 200)
            logger.info(f"Categoría {id} actualizada con éxito")
            return updated

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en update_category (id={id}): {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en update_category (id={id}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}",
            )


@router.delete("/delete/{id}", response_model=CategoryOut, dependencies=[Depends(get_current_active_user)])
def delete_category(id: UUID, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("delete_category") as span:
        try:
            span.set_attribute("category.id", str(id))
            categoria_exist = category_service.get(db, id)

            if categoria_exist is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No existe esta categoria",
                )

            deleted = category_service.delete(db, id=id)

            span.set_attribute("http.status_code", 200)
            logger.info(f"Categoría {id} eliminada con éxito")
            return deleted

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en delete_category (id={id}): {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en delete_category (id={id}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}",
            )