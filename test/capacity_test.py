"""Tests para /capacity"""
import uuid
from app.models.models import Capacity


class TestGetCapacities:
    def test_returns_active_capacities(self, client, db, product):
        db.add(Capacity(id=uuid.uuid4(), product_id=product.id, capacity="256GB", is_active=True))
        db.commit()
        response = client.get("/capacity/")
        assert response.status_code == 200
        assert response.json()[0]["capacity"] == "256GB"

    def test_excludes_inactive_capacities(self, client, db, product):
        db.add(Capacity(id=uuid.uuid4(), product_id=product.id, capacity="512GB", is_active=False))
        db.commit()
        response = client.get("/capacity/")
        assert response.status_code == 404

    def test_returns_404_when_no_capacities(self, client):
        response = client.get("/capacity/")
        assert response.status_code == 404

    def test_response_contains_expected_fields(self, client, db, product):
        db.add(Capacity(id=uuid.uuid4(), product_id=product.id, capacity="128GB", is_active=True))
        db.commit()
        response = client.get("/capacity/")
        item = response.json()[0]
        for field in ("id", "capacity", "product_id", "is_active"):
            assert field in item


class TestGetCapacityById:
    def test_returns_capacity_by_id(self, client, db, product):
        cap = Capacity(id=uuid.uuid4(), product_id=product.id, capacity="1TB", is_active=True)
        db.add(cap)
        db.commit()
        response = client.get(f"/capacity/{cap.id}")
        assert response.status_code == 200
        assert response.json()["capacity"] == "1TB"

    def test_returns_404_for_unknown_id(self, client):
        response = client.get(f"/capacity/{uuid.uuid4()}")
        assert response.status_code == 404

    def test_returns_404_for_inactive_capacity(self, client, db, product):
        cap = Capacity(id=uuid.uuid4(), product_id=product.id, capacity="Old", is_active=False)
        db.add(cap)
        db.commit()
        response = client.get(f"/capacity/{cap.id}")
        assert response.status_code == 404

    def test_returns_422_for_invalid_uuid(self, client):
        response = client.get("/capacity/not-a-uuid")
        assert response.status_code == 422


class TestCreateCapacity:
    def test_creates_capacity_successfully(self, client, product):
        payload = {"capacity": "512GB", "product_id": str(product.id), "is_active": True}
        response = client.post("/capacity/create", json=payload)
        assert response.status_code == 200
        assert response.json()["capacity"] == "512GB"
        assert response.json()["product_id"] == str(product.id)

    def test_returns_409_for_duplicate_capacity(self, client, db, product):
        db.add(Capacity(id=uuid.uuid4(), product_id=product.id, capacity="256GB", is_active=True))
        db.commit()
        payload = {"capacity": "256GB", "product_id": str(product.id), "is_active": True}
        response = client.post("/capacity/create", json=payload)
        assert response.status_code == 409

    def test_returns_422_when_capacity_too_short(self, client, product):
        payload = {"capacity": "AB", "product_id": str(product.id), "is_active": True}
        response = client.post("/capacity/create", json=payload)
        assert response.status_code == 422

    def test_returns_422_when_missing_product_id(self, client):
        payload = {"capacity": "128GB", "is_active": True}
        response = client.post("/capacity/create", json=payload)
        assert response.status_code == 422

    def test_returns_422_when_missing_all_fields(self, client):
        response = client.post("/capacity/create", json={})
        assert response.status_code == 422

    def test_requires_authentication(self, client_no_auth, product):
        payload = {"capacity": "64GB", "product_id": str(product.id), "is_active": True}
        response = client_no_auth.post("/capacity/create", json=payload)
        assert response.status_code == 401


class TestUpdateCapacity:
    def test_updates_capacity_successfully(self, client, db, product):
        cap = Capacity(id=uuid.uuid4(), product_id=product.id, capacity="128GB", is_active=True)
        db.add(cap)
        db.commit()
        payload = {"capacity": "256GB", "is_active": True}
        response = client.put(f"/capacity/update/{cap.id}", json=payload)
        assert response.status_code == 200
        assert response.json()["capacity"] == "256GB"

    def test_returns_404_for_unknown_id(self, client):
        payload = {"capacity": "512GB", "is_active": True}
        response = client.put(f"/capacity/update/{uuid.uuid4()}", json=payload)
        assert response.status_code == 404

    def test_requires_authentication(self, client_no_auth, db, product):
        cap = Capacity(id=uuid.uuid4(), product_id=product.id, capacity="64GB", is_active=True)
        db.add(cap)
        db.commit()
        payload = {"capacity": "128GB", "is_active": True}
        response = client_no_auth.put(f"/capacity/update/{cap.id}", json=payload)
        assert response.status_code == 401

    def test_can_deactivate_capacity(self, client, db, product):
        cap = Capacity(id=uuid.uuid4(), product_id=product.id, capacity="32GB", is_active=True)
        db.add(cap)
        db.commit()
        payload = {"capacity": "32GB", "is_active": False}
        response = client.put(f"/capacity/update/{cap.id}", json=payload)
        assert response.status_code == 200
        db.refresh(cap)
        assert cap.is_active is False


class TestDeleteCapacity:
    def test_soft_deletes_capacity(self, client, db, product):
        cap = Capacity(id=uuid.uuid4(), product_id=product.id, capacity="16GB", is_active=True)
        db.add(cap)
        db.commit()
        response = client.delete(f"/capacity/delete/{cap.id}")
        assert response.status_code == 200
        db.refresh(cap)
        assert cap.is_active is False

    def test_deleted_capacity_not_in_list(self, client, db, product):
        cap = Capacity(id=uuid.uuid4(), product_id=product.id, capacity="8GB", is_active=True)
        db.add(cap)
        db.commit()
        client.delete(f"/capacity/delete/{cap.id}")
        response = client.get("/capacity/")
        assert response.status_code == 404

    def test_returns_404_for_unknown_id(self, client):
        response = client.delete(f"/capacity/delete/{uuid.uuid4()}")
        assert response.status_code == 404

    def test_requires_authentication(self, client_no_auth, db, product):
        cap = Capacity(id=uuid.uuid4(), product_id=product.id, capacity="4GB", is_active=True)
        db.add(cap)
        db.commit()
        response = client_no_auth.delete(f"/capacity/delete/{cap.id}")
        assert response.status_code == 401