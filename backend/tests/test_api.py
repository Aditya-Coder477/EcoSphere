import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "Carbon Footprint Platform API"}

def test_metadata():
    response = client.get("/api/v1/metadata")
    assert response.status_code == 200
    assert "version" in response.json()

def test_create_user():
    payload = {
        "user_id": "test_user_01",
        "occupation": "student",
        "city_type": "urban",
        "budget_profile": "low",
        "is_vegetarian": True
    }
    response = client.post("/api/v1/users/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["user_id"] == "test_user_01"

def test_get_user():
    response = client.get("/api/v1/users/test_user_01")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["occupation"] == "student"

def test_calculate_carbon():
    payload = {
        "user_id": "test_user_01",
        "transport": [
            {"mode": "Car", "distance_km": 100}
        ],
        "electricity": {
            "country": "United States",
            "kwh_per_month": 300
        }
    }
    response = client.post("/api/v1/carbon/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "total_emissions_kg_co2e" in data["data"]
    assert "transport" in data["data"]["category_emissions"]

def test_recommendations():
    payload = {
        "user_id": "test_user_01",
        "category_emissions": {"transport": 1000.0, "electricity": 500.0},
        "total_emissions_kg_co2e": 1500.0,
        "dominant_emission_source": "transport",
        "occupation": "student",
        "city_type": "urban",
        "budget_profile": "low",
        "is_vegetarian": False,
        "synthetic_green_adoption_probability": 0.8
    }
    response = client.post("/api/v1/recommendations/?top_n=2", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["recommendations"]) <= 2

def test_llm_explain():
    payload = {
        "user_id": "test_user_01",
        "context_type": "footprint",
        "context_data": {"total_emissions_kg_co2e": 1500.0}
    }
    response = client.post("/api/v1/llm/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "1500.0" in data["data"]["explanation_text"]

def test_rag_query():
    payload = {
        "user_id": "test_user_01",
        "query": "Is public transit better?"
    }
    response = client.post("/api/v1/rag/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "public transit" in data["data"]["answer"]
