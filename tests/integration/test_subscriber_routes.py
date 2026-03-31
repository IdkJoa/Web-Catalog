import pytest
import uuid

def test_subscribe_new_email(client):
    """Test public endpoint: Successful subscription of a new email."""
    response = client.post(
        "/subscribers/subscribe",
        json={"email": "new_user@example.com"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new_user@example.com"
    assert data["is_active"] is True
    assert "id" in data

def test_subscribe_existing_inactive_user(client):
    """Test public endpoint: Resubscribing an existing inactive user."""
    # 1. Create a user and then unsubscribe them
    res = client.post("/subscribers/subscribe", json={"email": "resub@example.com"})
    sub_id = res.json()["id"]
    client.get(f"/subscribers/unsubscribe/{sub_id}")

    # 2. Resubscribe
    response = client.post("/subscribers/subscribe", json={"email": "resub@example.com"})
    assert response.status_code == 201 # Or 200 depending on implementation, but 201 is current
    data = response.json()
    assert data["is_active"] is True
    assert data["id"] == sub_id

def test_unsubscribe_success(client):
    """Test public endpoint: Successful unsubscription via ID."""
    # 1. Subscribe
    res = client.post("/subscribers/subscribe", json={"email": "unsub@example.com"})
    sub_id = res.json()["id"]

    # 2. Unsubscribe
    response = client.get(f"/subscribers/unsubscribe/{sub_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "You have been successfully unsubscribed."

def test_unsubscribe_not_found(client):
    """Test public endpoint: 404 for non-existent ID."""
    random_id = str(uuid.uuid4())
    response = client.get(f"/subscribers/unsubscribe/{random_id}")
    assert response.status_code == 404

def test_get_subscribers_admin_unauthorized(client):
    """Test security: Admin endpoint should return 401/403 without token."""
    response = client.get("/subscribers/subscribers")
    # It should fail because dependencies=[Depends(get_current_active_user)] is set
    assert response.status_code in [401, 403]
