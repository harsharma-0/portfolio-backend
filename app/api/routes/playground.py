from fastapi import APIRouter, HTTPException
from app.schemas.common import success
from app.schemas.playground import DataTransformRequest, JsonInspectorRequest, TextAnalysisRequest
from app.services.playground_service import analyze_text, inspect_json, transform_data

router = APIRouter(prefix="/playground", tags=["Playground"])

@router.post("/text-analysis")
async def text_analysis(body: TextAnalysisRequest): return success("Text analyzed", analyze_text(body.text))

@router.post("/json-inspector")
async def json_inspector(body: JsonInspectorRequest):
    try: result = inspect_json(body.payload)
    except ValueError as exc: raise HTTPException(413, str(exc))
    return success("JSON inspected", result)

@router.post("/data-transform")
async def data_transform(body: DataTransformRequest): return success("Data transformed", transform_data(body))
