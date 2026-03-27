import uuid

from fastapi import APIRouter
from fastapi import Depends, status, HTTPException
from app.core.security import get_current_active_user
from sqlalchemy.orm import Session

from app.db.db_connection import get_db
from app.schemas.social_network import SocialNetworkCreate, SocialNetworkUpdate, SocialNetworkOut
from app.services.social_network_service import social_network_service
from typing import List


router = APIRouter(prefix="/social-network", tags=["social network"])

@router.get("/social-network", response_model=List[SocialNetworkOut], status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_active_user)])
def get_social_network(
        skip: int = 0, limit: int = 100,
        db: Session = Depends(get_db)
):
    data = social_network_service.get_all_no_filtered(db=db, skip=skip, limit=limit)
    return data

@router.post("/social-network", response_model=SocialNetworkOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_active_user)])
def create_social_network(
        social_network_in: SocialNetworkCreate,
        db: Session = Depends(get_db)
):
    social_network = social_network_service.create(db=db, obj_in=social_network_in)
    return social_network

@router.put("/social-network{id}", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(get_current_active_user)])
def update_social_network(
        social_network_id: uuid.UUID,
        social_network: SocialNetworkUpdate,
        db: Session = Depends(get_db)
):
    social_network_existing =  social_network_service.get(db=db, id=social_network_id)

    if social_network_existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The social network does not exist")

    updated_social_network = social_network_service.update(db=db, obj_in=social_network, db_obj=social_network_existing)
    return updated_social_network


@router.delete("/social-network{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_active_user)])
def delete_social_network(
        social_network_id: uuid.UUID,
        db: Session = Depends(get_db)
):
    social_network_service.delete(db=db, id=social_network_id)
    return {"message": "Social network deleted successfully."}


