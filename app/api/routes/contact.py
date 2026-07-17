from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.schemas.common import success
from app.schemas.contact import ContactRequest
from app.services.email_service import EmailService

router = APIRouter(tags=["Contact"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/contact")
@limiter.limit("5/10minutes")
async def contact(request: Request, inquiry: ContactRequest):
    if inquiry.website.strip(): raise HTTPException(400, "Submission rejected")
    try: mode = await EmailService(request.app.state.settings).send("contact_email.html", f"Portfolio inquiry: {inquiry.subject}", {"inquiry": inquiry}, str(inquiry.email))
    except RuntimeError: raise HTTPException(503, "Email service is temporarily unavailable")
    message = "Inquiry accepted in development mode" if mode == "development" else "Inquiry sent successfully"
    return success(message, {"delivery": mode})
