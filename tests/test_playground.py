async def test_text_analysis(client):
    data = (await client.post("/api/v1/playground/text-analysis", json={"text":"Hello hello. FastAPI 2!"})).json()["data"]
    assert data["word_count"] == 4 and data["unique_word_count"] == 3 and data["digit_count"] == 1

async def test_json_inspector(client):
    data = (await client.post("/api/v1/playground/json-inspector", json={"payload":{"items":[{"active":True,"value":None}]}})).json()["data"]
    assert data["objects"] == 2 and data["arrays"] == 1 and data["booleans"] == 1 and data["nulls"] == 1

async def test_data_transform(client):
    payload = {"items":[{"name":"FastAPI","category":"Backend","score":95},{"name":"Angular","category":"Frontend","score":90},{"name":"Python","category":"Backend","score":99}],"category":"Backend","sort_by":"score","sort_order":"desc","page":1,"page_size":1}
    data = (await client.post("/api/v1/playground/data-transform", json=payload)).json()["data"]
    assert data["items"][0]["name"] == "Python" and data["pagination"]["total_items"] == 2 and data["pagination"]["total_pages"] == 2
