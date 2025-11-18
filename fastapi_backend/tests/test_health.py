def test_health_root_ok(app_client):
    res = app_client.get("/")
    assert res.status_code == 200
    data = res.json()
    # The app's health returns a message field according to src.api.main
    assert "message" in data
    assert data["message"] == "Healthy"
