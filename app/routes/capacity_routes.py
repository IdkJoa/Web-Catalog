from opentelemetry import trace
from opentelemetry.sdk.resources import logger
from typing import List
from uuid import UUID

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.db_connection import get_db
from app.schemas.capacity import CapacityOut, CapacityCreate, CapacityBase
from app.services.capacity_service import capacity_services

tracer = trace.get_tracer(__name__)

router = APIRouter(
    prefix="/capacity",
    tags=["capacity"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "producto no encontrado"}},
)


@router.get("/", response_model=List[CapacityOut])
def get_capacities(db: Session = Depends(get_db)):
    with tracer.start_as_current_span("get_capacities") as span:
        try:
            capacities = capacity_services.get_multi(db)

            if capacities == []:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No hay capacidades activas",
                )

            span.set_attribute("http.status_code", 200)
            span.set_attribute("capacities.count", len(capacities))
            logger.info("Capacidades devueltas con éxito")
            return capacities

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en get_capacities: {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en get_capacities: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}",
            )


@router.get("/{id}", response_model=CapacityOut)
def get_capacity_by_id(id: UUID, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("get_capacity_by_id") as span:
        try:
            span.set_attribute("capacity.id", str(id))
            capacity = capacity_services.get(db, id=id)

            if capacity is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Capacidad no encontrada",
                )

            span.set_attribute("http.status_code", 200)
            logger.info(f"Capacidad {id} devuelta con éxito")
            return capacity

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en get_capacity_by_id (id={id}): {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en get_capacity_by_id (id={id}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}",
            )


@router.post("/create", response_model=CapacityOut)
def create_capacity(capacity: CapacityCreate, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("create_capacity") as span:
        try:
            span.set_attribute("capacity.value", str(capacity.capacity))
            exist = capacity_services.get_byprodutcsid(db, capacity.product_id, capacity.capacity)

            if exist:
                if exist.is_active:
                 raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                     detail="capacity existente",
                 )

            new_capacity = capacity_services.create(db=db, obj_in=capacity)

            span.set_attribute("http.status_code", 201)
            span.set_attribute("capacity.id", str(new_capacity.id))
            logger.info(f"Capacidad '{capacity.capacity}' creada con éxito (id={new_capacity.id})")
            return new_capacity

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en create_capacity (value={capacity.capacity}): {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en create_capacity (value={capacity.capacity}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno del servidor: {str(e)}",
            )


@router.put("/update/{id}", response_model=CapacityOut)
def update_capacity(id: UUID, capacity: CapacityBase, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("update_capacity") as span:
        try:
            span.set_attribute("capacity.id", str(id))
            exist = capacity_services.get(db, id)

            if exist is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="capacity no encontrado",
                )

            updated = capacity_services.update(db=db, obj_in=capacity, db_obj=exist)

            span.set_attribute("http.status_code", 200)
            logger.info(f"Capacidad {id} actualizada con éxito")
            return updated

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en update_capacity (id={id}): {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en update_capacity (id={id}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno del servidor: {str(e)}",
            )


@router.delete("/delete/{id}", response_model=CapacityOut)
def delete_capacity(id: UUID, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("delete_capacity") as span:
        try:
            span.set_attribute("capacity.id", str(id))
            exist = capacity_services.get(db, id)

            if exist is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="capacity no encontrado",
                )

            deleted = capacity_services.delete(db=db, id=id)

            span.set_attribute("http.status_code", 200)
            logger.info(f"Capacidad {id} eliminada con éxito")
            return deleted

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en delete_capacity (id={id}): {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en delete_capacity (id={id}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno del servidor: {str(e)}",
            )