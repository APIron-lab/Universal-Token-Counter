from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from core.token_counter import UtcError, UtcErrorCode, count_tokens


API_VERSION = "0.1.0"

app = FastAPI(
    title="Universal Token Counter API",
    version=API_VERSION,
    description="HTTP API wrapper for Universal Token Counter (UTC).",
)


# ======== Pydantic Models ========


class TokenCountRequest(BaseModel):
    """UTC v0.1 request payload for token counting."""

    model: str = Field(..., description="Target model name, e.g. 'gpt-4o'.")
    text: str = Field(..., description="Input text to be tokenized.")
    # 将来的に version をクライアント指定にする場合のために残しておく
    # version: str | None = Field(default=None, description="UTC spec version (optional).")


class ErrorBody(BaseModel):
    code: str
    message: str
    hint: str


class ErrorResponse(BaseModel):
    error: ErrorBody
    meta: Dict[str, Any]


# ======== Error message / hint mapping (APIron Error Spec 準拠の簡易版) ========

ERROR_MESSAGES: Dict[UtcErrorCode, str] = {
    UtcErrorCode.INVALID_TYPE: "型が不正です。",
    UtcErrorCode.EMPTY_TEXT: "入力テキストが空です。",
    UtcErrorCode.UNSUPPORTED_MODEL: "サポートされていないモデルです。",
    UtcErrorCode.PAYLOAD_TOO_LARGE: "入力サイズが上限を超えています。",
}

ERROR_HINTS: Dict[UtcErrorCode, str] = {
    UtcErrorCode.INVALID_TYPE: "Check that 'model' and 'text' are strings.",
    UtcErrorCode.EMPTY_TEXT: "Provide non-empty text (not only whitespace).",
    UtcErrorCode.UNSUPPORTED_MODEL: "Use one of the supported model names.",
    UtcErrorCode.PAYLOAD_TOO_LARGE: "Reduce input size under UTC limits.",
}

ERROR_HTTP_STATUS: Dict[UtcErrorCode, int] = {
    UtcErrorCode.INVALID_TYPE: 400,
    UtcErrorCode.EMPTY_TEXT: 400,
    UtcErrorCode.UNSUPPORTED_MODEL: 400,
    UtcErrorCode.PAYLOAD_TOO_LARGE: 413,
}


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_error_response(err: UtcError, started_at: float) -> JSONResponse:
    code = err.code

    message = ERROR_MESSAGES.get(code, "エラーが発生しました。")
    hint = ERROR_HINTS.get(code, "Check your request and try again.")
    status = ERROR_HTTP_STATUS.get(code, 500)

    body = {
        "error": {
            "code": str(code),
            "message": message,
            "hint": hint,
        },
        "meta": {
            "version": API_VERSION,
            "utc_timestamp": _now_utc_iso(),
            "processing_time_ms": (time.perf_counter() - started_at) * 1000.0,
        },
    }
    return JSONResponse(status_code=status, content=body)


# ======== FastAPI validation error → UTC Error Spec へ統一 ========


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """FastAPI/Pydantic のバリデーションエラーも UTC 統一エラー形式に変換する。"""
    started_at = time.perf_counter()

    # ここでは「型不正」として一律に扱う（必要なら detail から分岐も可能）
    err = UtcError(
        UtcErrorCode.INVALID_TYPE,
        "model/text フィールドの型が不正です。",
    )
    return _build_error_response(err, started_at)


# ======== Routes ========


@app.post("/utc/v0/token-count")
async def token_count_endpoint(req: TokenCountRequest) -> Dict[str, Any]:
    """Count tokens for given model and text.

    Returns UTC v0.1 unified response:
      - success: { "result": ..., "meta": ... }
      - error:   { "error": ..., "meta": ... }
    """
    started_at = time.perf_counter()

    try:
        data = count_tokens(req.model, req.text)
        # core.count_tokens はすでに result + meta を含む dict を返却する想定
        # ここでは processing_time_ms と utc_timestamp を上書きする
        meta = data.get("meta", {})
        meta.update(
            {
                "utc_timestamp": _now_utc_iso(),
                "processing_time_ms": (time.perf_counter() - started_at) * 1000.0,
                "version": API_VERSION,
            }
        )
        data["meta"] = meta
        return data

    except UtcError as err:
        # ドメインエラーは UTC 統一エラー形式に変換
        return _build_error_response(err, started_at)


# ======== (Optional) health check ========


@app.get("/health")
async def health() -> Dict[str, str]:
    return {
        "status": "ok",
        "service": "universal-token-counter",
        "version": API_VERSION,
        "timestamp": _now_utc_iso(),
    }

