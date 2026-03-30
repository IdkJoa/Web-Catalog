import logging
from app.base.crud_base import CRUDBase
from app.models.models import SocialNetwork
from app.schemas.social_network import SocialNetworkCreate, SocialNetworkUpdate

logger = logging.getLogger(__name__)

class SocialNetworkService(CRUDBase[SocialNetwork, SocialNetworkCreate, SocialNetworkUpdate]):
    pass

social_network_service = SocialNetworkService(SocialNetwork)