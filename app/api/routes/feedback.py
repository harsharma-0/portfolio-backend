from fastapi import APIRouter, HTTPException, Request
from app.schemas.common import success
from app.schemas.feedback import FeedbackRequest
from app.services.content_service import content_service
from app.services.email_service import EmailService
from app.api.routes.contact import limiter

router = APIRouter(tags=["Feedback"])

@router.post("/feedback")
@limiter.limit("5/10minutes")
async def feedback(request: Request, feedback: FeedbackRequest):
    if feedback.website.strip(): raise HTTPException(400, "Submission rejected")
    project = content_service.project(feedback.project_slug)
    if not project: raise HTTPException(404, "Project not found")
    try: mode = await EmailService(request.app.state.settings).send("feedback_email.html", f"Portfolio feedback: {project['title']}", {"feedback": feedback, "project": project}, str(feedback.email) if feedback.email else None)
    except RuntimeError: raise HTTPException(503, "Email service is temporarily unavailable")
    return success("Feedback accepted" if mode != "development" else "Feedback accepted in development mode", {"delivery": mode})
