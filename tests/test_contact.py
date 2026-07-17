def valid_contact():
    return {"name":"Test Client","email":"client@example.com","service":"FastAPI REST API development","budget":"1000-2500","timeline":"2-4-weeks","subject":"API project inquiry","message":"I would like to discuss a well-scoped API development project.","website":"","consent":True}

async def test_contact_validation(client):
    body = valid_contact(); body["consent"] = False
    assert (await client.post("/api/v1/contact", json=body)).status_code == 422

async def test_contact_honeypot(client):
    body = valid_contact(); body["website"] = "spam.example"
    assert (await client.post("/api/v1/contact", json=body)).status_code == 400

async def test_contact_development_success(client):
    response = await client.post("/api/v1/contact", json=valid_contact())
    assert response.status_code == 200 and response.json()["data"]["delivery"] == "development"

async def test_contact_rejects_non_http_attachment(client):
    body = valid_contact(); body["attachment_link"] = "javascript:alert(1)"
    assert (await client.post("/api/v1/contact", json=body)).status_code == 422
