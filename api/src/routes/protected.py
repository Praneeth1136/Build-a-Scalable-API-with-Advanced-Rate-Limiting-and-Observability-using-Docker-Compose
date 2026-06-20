from fastapi import APIRouter, Depends, Request
from ..middleware.rate_limiter import rate_limiter

router = APIRouter()

@router.post("/protected-action")
async def protected_action(request: Request, _ = Depends(rate_limiter)):
    return {"message": "Success", "data": "Protected action executed"}
