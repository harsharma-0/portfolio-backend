from fastapi import APIRouter, HTTPException, Query
from app.schemas.common import success
from app.services.content_service import content_service

router = APIRouter(tags=["Portfolio"])

@router.get("/profile")
async def profile(): return success("Profile retrieved", content_service.load("profile"))

@router.get("/projects")
async def projects(category: str | None = Query(None, max_length=80), technology: str | None = Query(None, max_length=80), featured: bool | None = None, search: str | None = Query(None, max_length=120)):
    return success("Projects retrieved", content_service.projects(category, technology, featured, search))

@router.get("/projects/{slug}")
async def project(slug: str):
    item = content_service.project(slug)
    if not item: raise HTTPException(404, "Project not found")
    return success("Project retrieved", item)

def collection_route(name: str):
    async def endpoint(): return success(f"{name.title()} retrieved", content_service.load(name))
    return endpoint

for collection in ("skills", "experience", "services", "achievements", "testimonials"):
    router.add_api_route(f"/{collection}", collection_route(collection), methods=["GET"], name=f"get_{collection}")

@router.get("/portfolio")
async def portfolio(): return success("Complete portfolio retrieved", content_service.portfolio())
