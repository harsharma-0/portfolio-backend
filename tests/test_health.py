async def test_health(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "healthy"
    assert response.json()["data"]["timestamp"].endswith("+00:00")
