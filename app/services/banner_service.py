from sqlalchemy.orm import Session
from sqlalchemy import select
from app.base.crud_base import CRUDBase
from app.models.models import Banner
from app.schemas.banner import BannerCreate, BannerUpdate

class BannerService(CRUDBase[Banner, BannerCreate, BannerUpdate]):

    def get_active_for_website(self, db: Session, skip: int = 0, limit: int = 100):
        stmt = (select(self.model)
                .where(self.model.is_active == True)
                .order_by(self.model.sort_order)
                .offset(skip).
                limit(limit))
        return list(db.execute(stmt).scalars().all())

banner = BannerService(Banner)