import logging
from app.base.crud_base import CRUDBase
from app.models.models import SiteSetting
from app.schemas.site_settings import SiteSettingsCreate, SiteSettingsUpdate

logger = logging.getLogger(__name__)

class SiteSettingsService(CRUDBase[SiteSetting, SiteSettingsCreate, SiteSettingsUpdate]):
    pass

site_settings_service = SiteSettingsService(SiteSetting)