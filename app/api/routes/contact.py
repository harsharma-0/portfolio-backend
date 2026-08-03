from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.schemas.common import success
from app.schemas.contact import ContactRequest
from app.services.email_service import EmailService
from app.core.exceptions import EmailConfigurationError, EmailDeliveryError

router = APIRouter(tags=["Contact"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/contact")
@limiter.limit("5/10minutes")
async def contact(request: Request, inquiry: ContactRequest):
    if inquiry.website.strip(): raise HTTPException(400, "Submission rejected")
    try:
        result = await EmailService(request.app.state.settings).send(
            "contact_email.html", f"Portfolio inquiry from {inquiry.name}: {inquiry.subject}",
            {"inquiry": inquiry}, str(inquiry.email),
        )
    except EmailConfigurationError:
        raise HTTPException(503, "Email service is not configured.")
    except EmailDeliveryError:
        raise HTTPException(503, "Email service is temporarily unavailable.")
    return success("Your inquiry was sent successfully.", result)
