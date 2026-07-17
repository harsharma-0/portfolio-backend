async def test_feedback_validation(client):
    response = await client.post("/api/v1/feedback", json={"name":"A","project_slug":"bad slug","feedback_type":"wrong","message":"short"})
    assert response.status_code == 422

async def test_invalid_project_feedback(client):
    response = await client.post("/api/v1/feedback", json={"name":"Test User","project_slug":"missing-project","feedback_type":"comment","message":"This is thoughtful project feedback."})
    assert response.status_code == 404

async def test_feedback_development_success(client):
    response = await client.post("/api/v1/feedback", json={"name":"Test User","email":"test@example.com","project_slug":"aws-cost-calculator","feedback_type":"appreciation","message":"The cost-estimation architecture is thoughtfully presented."})
    assert response.status_code == 200
