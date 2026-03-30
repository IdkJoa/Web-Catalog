import logging
from fastapi import APIRouter
from fastapi import status, HTTPException
from fastapi.params import Depends

from typing import List
from uuid import UUID

from app.db.db_connection import get_db
from app.core.security import get_current_user, get_current_active_user
from sqlalchemy.orm import Session
from app.schemas.testimonial import TestimonialOut
from app.schemas import testimonial
from app.services.testimonial_service import testimonial_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/testimonial", tags=["Testimonial"])

"""
    PAGE VISITORS ENDPOINTS
"""
@router.post("/testimonial", response_model=TestimonialOut, status_code=status.HTTP_201_CREATED)
def create_testimonial(
    testimonial_in: testimonial.TestimonialCreate,
    db: Session = Depends(get_db)
):
    logger.info(f"Creating new testimonial from: {testimonial_in.name}")
    new_testimonial = testimonial_service.create(db=db, obj_in=testimonial_in)
    logger.info(f"Testimonial created with id: {new_testimonial.id}")
    return new_testimonial


@router.get("/testimonials", response_model=List[TestimonialOut])
def get_testimonials(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> TestimonialOut:
    logger.debug(f"Fetching active testimonials: skip={skip}, limit={limit}")
    data = testimonial_service.get_active_for_website(db=db, skip=skip, limit=limit)
    return data

"""
    ADMINS Endpoints
"""

@router.get("/admin", response_model=List[TestimonialOut], dependencies=[Depends(get_current_active_user)])
def get_all_testimonials_admin(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
):
    logger.debug(f"Admin fetching all testimonials: skip={skip}, limit={limit}")
    return testimonial_service.get_all_no_filtered(db=db, skip=skip, limit=limit)

@router.delete("/{id}", dependencies=[Depends(get_current_active_user)])
def delete_testimonial(
        id: UUID,
        db: Session = Depends(get_db)
):
    logger.info(f"Deleting testimonial with id: {id}")
    del_testimonial = testimonial_service.get(db=db, id=id)
    if not del_testimonial:
        logger.warning(f"Delete failed: Testimonial {id} not found")
        raise HTTPException(status_code=404, detail="Testimonial not found")

    testimonial_service.delete(db=db, id=id)
    logger.info(f"Testimonial {id} deleted successfully")
    return {"message": "Testimonial successfully removed."}
