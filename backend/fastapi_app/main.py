# backend/fastapi_app/main.py
from __future__ import annotations

import time
from typing import Callable

from fastapi import FastAPI, Request, Response

from .router import router
from .handlers import register_exception_handlers

app = FastAPI(
    title="Universal Token Counter API",
    version="0.1.0",
    description="High-precision multilingual token counting API.",
)


@app.middleware("http")
async def add_timing_and_context(
    request: Request,
    call_next: Callable[[Request], Response],
) -> Response:

    start = time.perf_counter()

    # Mangum が載せた event
    aws_event = request.scope.get("aws.event")
    lambda_ctx = None

    if aws_event:
        # 1. utcLambdaContext（eventレベル）
        ctx1 = aws_event.get("utcLambdaContext")
        # 2. utcRawContext（context情報）
        ctx2 = aws_event.get("utcRawContext")

        combined = {}
        if ctx1:
            combined.update(ctx1)
        if ctx2:
            combined.update(ctx2)

        lambda_ctx = combined if combined else None

    try:
        response = await call_next(request)
    finally:
        end = time.perf_counter()
        processing_ms = (end - start) * 1000.0

        if lambda_ctx is not None:
            if lambda_ctx.get("lambda_duration_ms") is None:
                lambda_ctx["lambda_duration_ms"] = processing_ms

        request.state.processing_time_ms = processing_ms
        request.state.lambda_context = lambda_ctx

    return response


# ルーター登録
app.include_router(router, prefix="/utc/v0")

# エラーハンドラ登録
register_exception_handlers(app)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

