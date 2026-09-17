from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app


def test_client_case_flow():
    client = TestClient(app)
    email = f"e2e-{uuid4().hex}@example.test"
    auth = client.post("/api/auth/register", json={"email": email, "password": "LocalE2E123!"})
    assert auth.status_code == 200
    headers = {"Authorization": f"Bearer {auth.json()['token']}"}

    created = client.post("/api/cases", headers=headers, json={
        "case_type": "Online scam",
        "description": "E2E test report describing a suspicious payment request from a scammer.",
    })
    assert created.status_code == 200
    case_id = created.json()["id"]

    evidence = client.post(f"/api/cases/{case_id}/evidence", headers=headers, json={
        "kind": "user_note", "label": "E2E evidence", "content": "Suspicious message preserved for investigation."
    })
    assert evidence.status_code == 200

    investigation = client.post(f"/api/cases/{case_id}/investigate", headers=headers)
    assert investigation.status_code == 200
    assert investigation.json()["status"] in {"completed", "completed_with_fallback"}

    detail = client.get(f"/api/cases/{case_id}", headers=headers)
    assert detail.status_code == 200
    assert len(detail.json()["evidence"]) == 1
    assert len(detail.json()["findings"]) >= 1


def test_case_isolation():
    client = TestClient(app)
    one = client.post("/api/auth/register", json={"email": f"a-{uuid4().hex}@example.test", "password": "LocalE2E123!"})
    two = client.post("/api/auth/register", json={"email": f"b-{uuid4().hex}@example.test", "password": "LocalE2E123!"})
    h1 = {"Authorization": f"Bearer {one.json()['token']}"}
    h2 = {"Authorization": f"Bearer {two.json()['token']}"}
    created = client.post("/api/cases", headers=h1, json={"case_type":"Payment fraud","description":"Private case belonging to the first account."})
    case_id = created.json()["id"]
    assert client.get(f"/api/cases/{case_id}", headers=h2).status_code == 404
