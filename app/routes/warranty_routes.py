import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter,status,Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.db_connection import get_db
from app.schemas.warranty import WarrantyBase, WarrantyOut
from app.services.warranty_service import warranty_services

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/warranty", tags=["warranty"],
                    responses = {status.HTTP_404_NOT_FOUND: {"message": "warrranty no encontrado"}})
@router.get("/", response_model=List[WarrantyOut])
def get_warranties(db: Session = Depends(get_db)):
    logger.debug("Fetching all warranties")
    try:
        warranty = warranty_services.get_multi(db)

        if not warranty:
            logger.info("No active warranties found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No hay warranty activas")
        return warranty

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error fetching warranties: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )
@router.get("/{id}", response_model=WarrantyOut)
def get_warranty_by_id(id: UUID, db: Session = Depends(get_db)):
    logger.debug(f"Fetching warranty with id: {id}")
    try:
        warranty = warranty_services.get(db, id)

        if warranty is None:
            logger.warning(f"Warranty not found with id: {id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No existe esta garantia")

        return warranty

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error fetching warranty {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )


@router.post("/create", response_model=WarrantyOut, dependencies=[Depends(get_current_active_user)])
def create_warranty(warranty: WarrantyBase, db: Session = Depends(get_db)):
    logger.info(f"Creating new warranty with duration: {warranty.duration}")
    try:
        exist = warranty_services.get_byduration(db, warranty.duration)
        if not exist is None:
            logger.warning(f"Conflict: Warranty with duration {warranty.duration} already exists")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Warranty existe")

        new_warranty = warranty_services.create(db,obj_in=warranty)
        logger.info(f"Warranty created with id: {new_warranty.id}")
        return new_warranty

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error creating warranty: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )
@router.put("/update/{id}", response_model=WarrantyOut, dependencies=[Depends(get_current_active_user)])
def update_warranty(warranty: WarrantyBase, id: UUID, db: Session = Depends(get_db)):
    logger.info(f"Updating warranty with id: {id}")
    try:
        warranty_exist = warranty_services.get(db, id)
        if warranty_exist is None:
            logger.warning(f"Update failed: Warranty {id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No existe esta garantia")

        updated_warranty = warranty_services.update(db,db_obj=warranty_exist, obj_in=warranty)
        logger.info(f"Warranty {id} updated successfully")

        return updated_warranty

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error updating warranty {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

