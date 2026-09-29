"""
Tests for lead CRUD operations and permissions.
"""
import pytest


def _create_lead(client, headers, **overrides):
    payload = {
        "first_name": "Test",
        "last_name": "Lead",
        "email": "test.lead@example.com",
        "company": "Test Corp",
        "job_title": "CTO",
        "source": "WEBSITE",
        "industry": "Technology",
        "company_size": "51-200",
        "estimated_value": 50000,
        "status": "NEW",
        "priority": "MEDIUM",
    }
    payload.update(overrides)
    return client.post("/api/leads", json=payload, headers=headers)


def test_create_lead(client, sales_headers):
    """Test creating a new lead."""
    response = _create_lead(client, sales_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Test"
    assert data["last_name"] == "Lead"
    assert data["status"] == "NEW"
    assert data["id"] is not None


def test_get_leads_list(client, sales_headers):
    """Test fetching lead list with pagination."""
    # Create 3 leads
    for i in range(3):
        _create_lead(client, sales_headers, first_name=f"Lead{i}", email=f"lead{i}@test.com")

    response = client.get("/api/leads?page=1&page_size=10", headers=sales_headers)
    assert response.status_code == 200
    data = response.json()
    assert "leads" in data
    assert "total" in data
    assert "total_pages" in data
    assert len(data["leads"]) == 3


def test_get_lead_by_id(client, sales_headers):
    """Test fetching a single lead by ID."""
    create_resp = _create_lead(client, sales_headers)
    lead_id = create_resp.json()["id"]

    response = client.get(f"/api/leads/{lead_id}", headers=sales_headers)
    assert response.status_code == 200
    assert response.json()["id"] == lead_id


def test_get_nonexistent_lead(client, sales_headers):
    """Test 404 on nonexistent lead."""
    response = client.get("/api/leads/nonexistent-id-123", headers=sales_headers)
    assert response.status_code == 404


def test_update_lead(client, sales_headers):
    """Test updating lead fields."""
    lead_id = _create_lead(client, sales_headers).json()["id"]

    response = client.put(
        f"/api/leads/{lead_id}",
        json={"status": "CONTACTED", "priority": "HIGH"},
        headers=sales_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CONTACTED"
    assert data["priority"] == "HIGH"


def test_delete_lead(client, sales_headers):
    """Test deleting a lead."""
    lead_id = _create_lead(client, sales_headers).json()["id"]

    delete_resp = client.delete(f"/api/leads/{lead_id}", headers=sales_headers)
    assert delete_resp.status_code == 204

    # Verify it's gone
    get_resp = client.get(f"/api/leads/{lead_id}", headers=sales_headers)
    assert get_resp.status_code == 404


def test_lead_search(client, sales_headers):
    """Test lead search by name."""
    _create_lead(client, sales_headers, first_name="Alice", last_name="Smith", email="alice@test.com")
    _create_lead(client, sales_headers, first_name="Bob", last_name="Jones", email="bob@test.com")

    response = client.get("/api/leads?search=Alice", headers=sales_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["leads"][0]["first_name"] == "Alice"


def test_lead_filter_by_status(client, sales_headers):
    """Test filtering leads by status."""
    _create_lead(client, sales_headers, email="new1@test.com", status="NEW")
    _create_lead(client, sales_headers, email="new2@test.com", status="NEW")
    _create_lead(client, sales_headers, email="qual@test.com", status="QUALIFIED")

    response = client.get("/api/leads?status=NEW", headers=sales_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    for lead in data["leads"]:
        assert lead["status"] == "NEW"


def test_create_lead_activity(client, sales_headers):
    """Test recording an activity on a lead."""
    lead_id = _create_lead(client, sales_headers).json()["id"]

    response = client.post(
        f"/api/leads/{lead_id}/activities",
        json={
            "type": "CALL",
            "title": "Initial discovery call",
            "description": "Discussed pain points",
            "outcome": "Very interested, requested proposal",
        },
        headers=sales_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "CALL"
    assert data["lead_id"] == lead_id


def test_create_lead_note(client, sales_headers):
    """Test adding a note to a lead."""
    lead_id = _create_lead(client, sales_headers).json()["id"]

    response = client.post(
        f"/api/leads/{lead_id}/notes",
        json={"content": "Important note about budget constraints"},
        headers=sales_headers,
    )
    assert response.status_code == 201
    assert response.json()["content"] == "Important note about budget constraints"
