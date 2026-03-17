from fastapi.testclient import TestClient

from mental_wellbeing_api.main import app


def test_agent_runtime_smoke() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/agent-runtime/smoke",
        json={
            "user_input": "I feel overwhelmed and tired after work every day.",
            "provider": "mock",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["provider"] == "mock"
    assert "structured_input" in payload
    assert "reflective_response" in payload
    assert "final_response" in payload