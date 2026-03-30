import logging
from app.base.crud_base import CRUDBase
from app.models.models import Testimonial
from app.schemas.testimonial import TestimonialCreate, TestimonialUpdate
from app.models import models
from sqlalchemy.orm import Session
from sqlalchemy import select

logger = logging.getLogger(__name__)

class PostTestimonial(CRUDBase[Testimonial, TestimonialCreate, TestimonialUpdate]):
    pass

    def get_active_for_website(self, db: Session, skip: int = 0, limit: int = 100):
        logger.debug(f"Fetching active testimonials for website (skip={skip}, limit={limit})")
        stmt = select(self.model).where(self.model.is_active == True).order_by(self.model.sort_order).offset(
            skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

testimonial_service = PostTestimonial(models.Testimonial)