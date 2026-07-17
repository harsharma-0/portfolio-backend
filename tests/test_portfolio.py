EXPECTED_SLUGS = [
    "amazon-q-cost-analytics-assistant",
    "distributed-multi-drone-ai-tracking",
    "documentation-module",
    "aws-native-services-platform",
    "aws-cost-calculator",
    "air-pollution-prediction",
]

async def test_portfolio_collections(client):
    for path in ("profile", "projects", "skills", "experience", "services", "achievements", "testimonials"):
        response = await client.get(f"/api/v1/{path}")
        assert response.status_code == 200 and response.json()["success"]

async def test_exact_project_catalog_order_and_featured_flags(client):
    projects = (await client.get("/api/v1/projects")).json()["data"]
    assert [project["slug"] for project in projects] == EXPECTED_SLUGS
    assert len(projects) == 6
    assert [project["slug"] for project in projects if project["featured"]] == EXPECTED_SLUGS[:2]

async def test_all_project_slugs_resolve(client):
    for slug in EXPECTED_SLUGS:
        response = await client.get(f"/api/v1/projects/{slug}")
        assert response.status_code == 200
        assert response.json()["data"]["slug"] == slug

async def test_project_filtering(client):
    response = await client.get("/api/v1/projects", params={"technology": "FastAPI", "featured": True})
    projects = response.json()["data"]
    assert projects and all("FastAPI" in project["technologies"] and project["featured"] for project in projects)

async def test_project_alias_search(client):
    projects = (await client.get("/api/v1/projects", params={"search": "what-if analysis"})).json()["data"]
    assert [project["slug"] for project in projects] == ["aws-cost-calculator"]

async def test_project_not_found_and_deleted_slugs(client):
    for slug in ("does-not-exist", "interactive-developer-portfolio", "air-quality-prediction-platform", "library-management-desktop-app"):
        response = await client.get(f"/api/v1/projects/{slug}")
        assert response.status_code == 404 and not response.json()["success"]

async def test_full_portfolio(client):
    data = (await client.get("/api/v1/portfolio")).json()["data"]
    assert {"profile", "projects", "skills", "experience", "services", "achievements", "testimonials"} <= data.keys()
    assert [project["slug"] for project in data["projects"]] == EXPECTED_SLUGS
