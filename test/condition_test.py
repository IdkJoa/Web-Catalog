"""Tests para /condition"""
import uuid
from app.models.models import Condition


class TestGetConditions:
    def test_returns_active_conditions(self, client, condition):
        response = client.get("/condition/")
        assert response.status_code == 200
        assert response.json()[0]["name"] == "Nuevo"

    def test_excludes_inactive_conditions(self, client, db):
        db.add(Condition(id=uuid.uuid4(), name="Inactiva", sort_order=1, is_active=False))
        db.commit()
        response = client.get("/condition/")
        assert response.status_code == 404

    def test_returns_404_when_no_conditions(self, client):
        response = client.get("/condition/")
        assert response.status_code == 404

    def test_returns_multiple_conditions(self, client, db, condition):
        db.add(Condition(id=uuid.uuid4(), name="Reacondicionado", sort_order=2, is_active=True))
        db.commit()
        response = client.get("/condition/")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_response_contains_expected_fields(self, client, condition):
        response = client.get("/condition/")
        item = response.json()[0]
        for field in ("id", "name", "is_active", "sort_order"):
            assert field in item


class TestGetConditionById:
    def test_returns_condition_by_id(self, client, condition):
        response = client.get(f"/condition/{condition.id}")
        assert response.status_code == 200
        assert response.json()["id"] == str(condition.id)

    def test_returns_404_for_unknown_id(self, client):
        response = client.get(f"/condition/{uuid.uuid4()}")
        assert response.status_code == 404

    def test_returns_404_for_inactive_condition(self, client, db):
        c = Condition(id=uuid.uuid4(), name="Antigua", sort_order=1, is_active=False)
        db.add(c)
        db.commit()
        response = client.get(f"/condition/{c.id}")
        assert response.status_code == 404

    def test_returns_422_for_invalid_uuid(self, client):
        response = client.get("/condition/not-a-valid-uuid")
        assert response.status_code == 422


class TestCreateCondition:
    def test_creates_condition_successfully(self, client):
        payload = {"name": "Usado", "description": "Buen estado", "sort_order": 2, "is_active": True}
        response = client.post("/condition/create", json=payload)
        assert response.status_code == 200
        assert response.json()["name"] == "Usado"

    def test_returns_409_for_duplicate_name(self, client, condition):
        payload = {
            "name": "Nuevo",
            "description": "El artículo se encuentra en su empaque original y nunca ha sido utilizado.",
            "sort_order": 1,
            "is_active": True
        }
        response = client.post("/condition/create", json=payload)
        assert response.status_code == 409

    def test_returns_422_when_name_too_short(self, client):
        response = client.post("/condition/create", json={"name": "AB", "sort_order": 1})
        assert response.status_code == 422

    def test_returns_422_when_missing_fields(self, client):
        response = client.post("/condition/create", json={})
        assert response.status_code == 422

    def test_requires_authentication(self, client_no_auth):
        payload = {"name": "Demo", "sort_order": 1, "is_active": True}
        response = client_no_auth.post("/condition/create", json=payload)
        assert response.status_code == 401

    def test_optional_description_is_accepted(self, client):
        payload = {"name": "Con descripcion", "description": "Una descripcion", "sort_order": 1, "is_active": True}
        response = client.post("/condition/create", json=payload)
        assert response.status_code == 200
        assert response.json()["description"] == "Una descripcion"


class TestUpdateCondition:
    def test_updates_condition_successfully(self, client, condition):
        # ConditionBase requiere name, description, sort_order, is_active
        payload = {"name": "Nuevo Actualizado", "description": "Actualizado", "sort_order": 5, "is_active": True}
        response = client.put(f"/condition/update/{condition.id}", json=payload)
        assert response.status_code == 200
        assert response.json()["name"] == "Nuevo Actualizado"
        assert response.json()["sort_order"] == 5

    def test_returns_404_for_unknown_id(self, client):
        payload = {
            "name": "Nuevo",
            "description": "El artículo se encuentra en su empaque original y nunca ha sido utilizado.",
            "sort_order": 1,
            "is_active": True
        }
        response = client.put(f"/condition/update/{uuid.uuid4()}", json=payload)
        assert response.status_code == 404

    def test_requires_authentication(self, client_no_auth, condition):
        payload = {"name": "Y cond", "sort_order": 1, "is_active": True}
        response = client_no_auth.put(f"/condition/update/{condition.id}", json=payload)
        assert response.status_code == 401


class TestDeleteCondition:
    def test_soft_deletes_condition(self, client, db, condition):
        response = client.delete(f"/condition/delete/{condition.id}")
        assert response.status_code == 200
        db.refresh(condition)
        assert condition.is_active is False

    def test_deleted_condition_not_returned_in_list(self, client, db, condition):
        client.delete(f"/condition/delete/{condition.id}")
        response = client.get("/condition/")
        assert response.status_code == 404

    def test_returns_404_for_unknown_id(self, client):
        response = client.delete(f"/condition/delete/{uuid.uuid4()}")
        assert response.status_code == 404

    def test_requires_authentication(self, client_no_auth, condition):
        response = client_no_auth.delete(f"/condition/delete/{condition.id}")
        assert response.status_code == 401