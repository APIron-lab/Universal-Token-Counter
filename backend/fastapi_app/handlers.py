from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from core.token_counter import (
    UtcErrorCode,
    UtcError
)

def register_exception_handlers(app: FastAPI):

    @app.exception_handler(UtcError)
    async def utc_error_handler(_, exc: UtcError):
        return JSONResponse(
            status_code=exc.http_status,
            content={
                "error": {
                    "code": exc.code.name,
                    "message": exc.message,
                    "hint": exc.hint
                },
                "meta": exc.meta
            }
        )

def http_error_response(exc: Exception):
    if isinstance(exc, UtcError):
        raise exc
    raise HTTPException(
        status_code=500,
        detail="Unhandled internal error."
    )

