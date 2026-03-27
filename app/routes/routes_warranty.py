from typing import List
from uuid import UUID

from fastapi import APIRouter,status,Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.db_connection import get_db
from app.schemas.Warranty import WarrantyBase, WarrantyOut
from app.services.Warrantyservices import warranty_services

router = APIRouter(prefix="/warranty", tags=["warranty"],
                    responses = {status.HTTP_404_NOT_FOUND: {"message": "warrranty no encontrado"}})
@router.get("/", response_model=List[WarrantyOut])
def get_warranty(db: Session = Depends(get_db)):
    try:
        warranty = warranty_services.get_multi(db)

        if warranty is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No hay warranty activas")

        return warranty

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )
@router.get("/{id}", response_model=WarrantyOut)
def get_warranty(id: UUID, db: Session = Depends(get_db)):
    try:
        warranty = warranty_services.get(db, id)

        if warranty is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No existe esta garantia")

        return warranty

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )


@router.post("/create", response_model=WarrantyOut)
def create_warranty(warranty: WarrantyBase, db: Session = Depends(get_db)):
    try:
        exist = warranty_services.get_byduration(db, warranty.duration)
        if not exist is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Warranty existe")

        warranty = warranty_services.create(db,obj_in=warranty)
        return warranty

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )
@router.put("/update/{id}", response_model=WarrantyOut)
def update_warranty(warranty: WarrantyBase, id: UUID, db: Session = Depends(get_db)):
    try:
        warranty_exist = warranty_services.get(db, id)
        if warranty_exist is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No existe esta garantia")

        warranty = warranty_services.update(db,db_obj=warranty_exist, obj_in=warranty)

        return warranty

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

