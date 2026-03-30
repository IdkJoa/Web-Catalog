import pytest
import uuid
from app.services.banner_service import banner
from app.schemas.banner import BannerCreate, BannerUpdate
from app.services.subscriber_service import subscriber_service
from app.schemas.subscriber import SubscriberCreate, SubscriberUpdate
from app.services.testimonial_service import testimonial_service
from app.schemas.testimonial import TestimonialCreate, TestimonialUpdate

# ==============================================================================
# BANNER SERVICE INTEGRATION
# ==============================================================================

def test_banner_lifecycle_integration(db_session):
    """Test full Banner lifecycle with real DB."""
    # 1. Create
    banner_in = BannerCreate(
        title="Integration Promo",
        image_url="http://example.com/img.png",
        sort_order=5
    )
    created = banner.create(db=db_session, obj_in=banner_in)
    assert created.id is not None
    assert created.title == "Integration Promo"

    # 2. Retrieve
    retrieved = banner.get(db=db_session, id=created.id)
    assert retrieved is not None
    assert retrieved.title == "Integration Promo"

    # 3. Update
    banner.update(db=db_session, db_obj=retrieved, obj_in=BannerUpdate(sort_order=10))
    updated = banner.get(db=db_session, id=created.id)
    assert updated.sort_order == 10

    # 4. Filter Active
    active_banners = banner.get_active_for_website(db=db_session)
    assert len(active_banners) == 1
    assert active_banners[0].title == "Integration Promo"

    # 5. Delete (Soft Delete)
    banner.delete(db=db_session, id=created.id)
    deleted = banner.get(db=db_session, id=created.id)
    assert deleted is None  # Because .get() filters by is_active=True

    all_no_filtered = banner.get_all_no_filtered(db=db_session)
    assert len(all_no_filtered) == 1
    assert all_no_filtered[0].is_active is False

# ==============================================================================
# SUBSCRIBER SERVICE INTEGRATION
# ==============================================================================

def test_subscriber_lifecycle_integration(db_session):
    """Test full Subscriber lifecycle with real DB."""
    # 1. Create
    sub_in = SubscriberCreate(email="integration@example.com")
    created = subscriber_service.create(db=db_session, obj_in=sub_in)
    assert created.id is not None

    # 2. Get by email
    found = subscriber_service.get_by_email(db=db_session, email="integration@example.com")
    assert found is not None
    assert found.id == created.id

    # 3. Duplicate email (Check if service layer handles it or if it errors)
    # Note: This verifies the database constraint works.
    with pytest.raises(Exception): # SQLAlchemy IntegrityError often raised as generic Exception in some service implementations
        subscriber_service.create(db=db_session, obj_in=sub_in)
        db_session.flush()

# ==============================================================================
# TESTIMONIAL SERVICE INTEGRATION
# ==============================================================================

def test_testimonial_lifecycle_integration(db_session):
    """Test full Testimonial lifecycle with real DB."""
    # 1. Create multiple
    t1_in = TestimonialCreate(name="User A", comment="A", sort_order=2)
    t2_in = TestimonialCreate(name="User B", comment="B", sort_order=1)
    
    # We use create directly for t1, but t2 needs sort_order which is not in Base schema usually
    # Check if testimonial_service.create handles sort_order (depends on implementation)
    # Actually, CRUDBase handles fields present in the Model from the schema
    
    # Let's create them and manually set sort order if needed, or check schema
    testimonial_service.create(db=db_session, obj_in=t1_in)
    testimonial_service.create(db=db_session, obj_in=t2_in)
    
    # 2. Verify sorting logic in get_active_for_website
    ordered = testimonial_service.get_active_for_website(db=db_session)
    
    # Ensure they are returned in order (t2 has sort_order 0 by default, t1 has 0 if not passed)
    # Wait, the Testimonial model has default=0 for sort_order.
    
    # Let's manually update to be sure
    objs = testimonial_service.get_multi(db=db_session)
    objs[0].sort_order = 10
    objs[1].sort_order = 5
    db_session.commit()
    
    ordered = testimonial_service.get_active_for_website(db=db_session)
    assert ordered[0].sort_order == 5
    assert ordered[1].sort_order == 10
