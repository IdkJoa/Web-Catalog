from opentelemetry import trace
from opentelemetry.sdk.resources import logger
from typing import List
from uuid import UUID

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.db_connection import get_db
from app.schemas.condition import ConditionOut, ConditionBase
from app.services.condition_service import condition_services

tracer = trace.get_tracer(__name__)

router = APIRouter(
    prefix="/condition",
    tags=["Condition"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "Condition no encontrado"}},
)


@router.get("/", response_model=List[ConditionOut])
def get_conditions(db: Session = Depends(get_db)):
    with tracer.start_as_current_span("get_conditions") as span:
        try:
            conditions = condition_services.get_multi(db)

            if not conditions:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No hay Conditions activas",
                )

            span.set_attribute("http.status_code", 200)
            span.set_attribute("conditions.count", len(conditions))
            logger.info("Conditions devueltas con éxito")
            return conditions

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en get_conditions: {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en get_conditions: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}",
            )


@router.get("/{id}", response_model=ConditionOut)
def get_condition_by_id(id: UUID, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("get_condition_by_id") as span:
        try:
            span.set_attribute("condition.id", str(id))
            condition = condition_services.get(db, id)

            if condition is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No existe esta condition",
                )

            span.set_attribute("http.status_code", 200)
            logger.info(f"Condition {id} devuelta con éxito")
            return condition

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en get_condition_by_id (id={id}): {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en get_condition_by_id (id={id}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}",
            )


@router.post("/create", response_model=ConditionOut)
def create_condition(condition: ConditionBase, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("create_condition") as span:
        try:
            span.set_attribute("condition.name", condition.name)
            exist = condition_services.get_byname(db, condition.name)

            if exist is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="condition existe",
                )

            new_condition = condition_services.create(db, obj_in=condition)

            span.set_attribute("http.status_code", 201)
            span.set_attribute("condition.id", str(new_condition.id))
            logger.info(f"Condition '{condition.name}' creada con éxito (id={new_condition.id})")
            return new_condition

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en create_condition (name={condition.name}): {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en create_condition (name={condition.name}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}",
            )


@router.put("/update/{id}", response_model=ConditionOut)
def update_condition(condition: ConditionBase, id: UUID, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("update_condition") as span:
        try:
            span.set_attribute("condition.id", str(id))
            condition_exist = condition_services.get(db, id)

            if condition_exist is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No existe esta condition",
                )

            updated = condition_services.update(db, db_obj=condition_exist, obj_in=condition)

            span.set_attribute("http.status_code", 200)
            logger.info(f"Condition {id} actualizada con éxito")
            return updated

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en update_condition (id={id}): {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en update_condition (id={id}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}",
            )


@router.delete("/delete/{id}", response_model=ConditionOut)
def delete_condition(id: UUID, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("delete_condition") as span:
        try:
            span.set_attribute("condition.id", str(id))
            condition_exist = condition_services.get(db, id)

            if condition_exist is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No existe esta condition",
                )

            deleted = condition_services.delete(db, id=id)

            span.set_attribute("http.status_code", 200)
            logger.info(f"Condition {id} eliminada con éxito")
            return deleted

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en delete_condition (id={id}): {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en delete_condition (id={id}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}",
            )