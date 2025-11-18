from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.token_counter import count_tokens
from .schemas import TokenCountRequest, TokenCountSuccessResponse
from .handlers import http_error_response

router = APIRouter()

@router.post("/token-count", response_model=TokenCountSuccessResponse)
async def token_count(req: TokenCountRequest):
    try:
        result = count_tokens(req.model, req.text)
        return result
    except Exception as e:
        raise http_error_response(e)

