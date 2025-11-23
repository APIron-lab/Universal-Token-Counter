# backend/fastapi_app/router.py
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Request

from core.token_counter import count_tokens, UtcError
from .schemas import TokenCountRequest, TokenCountSuccessResponse

from backend.observability import (
    log_token_count_success,
    log_unhandled_error,
    log_logging_failure,
    log_utc_access,
)


router = APIRouter()


@router.post("/token-count", response_model=TokenCountSuccessResponse)
async def token_count(
    req: TokenCountRequest,
    request: Request,
) -> TokenCountSuccessResponse:
    try:
        # コアロジック呼び出し（成功時は UTC v0.1 形式の dict が返る）
        result = count_tokens(req.model, req.text)

        # result は以下のような dict を想定：
        # {
        #   "result": {
        #       "model": ...,
        #       "encoding": ...,
        #       "char_count": ...,
        #       "token_count": ...,
        #       "token_per_char": ...
        #   },
        #   "meta": {
        #       "input_language": ...,
        #       "input_size_bytes": ...,
        #       "token_density": ...,
        #       "processing_time_ms": ...
        #   }
        # }
        try:
            result_block: Dict[str, Any] = (
                result.get("result", {}) if isinstance(result, dict) else {}
            )
            meta_block: Dict[str, Any] = (
                result.get("meta", {}) if isinstance(result, dict) else {}
            )

            # 従来のイベントログ（そのまま維持）
            log_token_count_success(
                model=result_block.get("model", req.model),
                char_count=result_block.get("char_count", len(req.text)),
                token_count=result_block.get("token_count", 0),
                meta=meta_block,
            )

            # 新: UTC 構造化アクセスログ
            _emit_utc_structured_log_success(
                request=request,
                req=req,
                result_block=result_block,
                meta_block=meta_block,
            )

        except Exception as log_exc:
            # ログ出力に失敗しても API のレスポンスは壊さない
            log_logging_failure(log_exc)

        return result  # FastAPI が response_model に合わせてシリアライズ

    except UtcError as e:
        # UtcError は専用ハンドラ（handlers.py）に任せる
        # 将来的に構造化ログを追加する場合は、ハンドラ側で log_utc_access を呼ぶ実装に拡張
        raise e

    except Exception as exc:
        # 想定外のエラーは 500 でまとめ、内容はログに送る
        log_unhandled_error(exc)

        try:
            _emit_utc_structured_log_error(
                request=request,
                req=req,
                error=exc,
            )
        except Exception as log_exc:
            log_logging_failure(log_exc)

        raise HTTPException(status_code=500, detail="Unhandled internal error.")


def _extract_lambda_context(request: Request) -> Dict[str, Any]:
    """
    middleware で仕込んだ request.state.lambda_context から
    request_id / source / cold_start / lambda_duration_ms を取り出す。
    """
    lambda_context = getattr(request.state, "lambda_context", None)
    if not lambda_context:
        return {
            "request_id": None,
            "source": None,
            "cold_start": None,
            "lambda_duration_ms": None,
        }

    return {
        "request_id": lambda_context.get("request_id"),
        "source": lambda_context.get("source"),
        "cold_start": lambda_context.get("cold_start"),
        "lambda_duration_ms": lambda_context.get("lambda_duration_ms"),
    }


def _get_processing_time_ms(request: Request) -> Optional[float]:
    return getattr(request.state, "processing_time_ms", None)


def _emit_utc_structured_log_success(
    *,
    request: Request,
    req: TokenCountRequest,
    result_block: Dict[str, Any],
    meta_block: Dict[str, Any],
) -> None:
    """
    正常終了時の UTC 構造化アクセスログ出力。
    """
    endpoint = str(request.url.path)
    ctx = _extract_lambda_context(request)
    processing_time_ms = meta_block.get("processing_time_ms") or _get_processing_time_ms(
        request
    )

    model: Optional[str] = result_block.get("model", req.model)
    char_count: Optional[int] = result_block.get("char_count")
    token_count: Optional[int] = result_block.get("token_count")
    token_per_char: Optional[float] = result_block.get("token_per_char")

    token_density: Optional[float] = meta_block.get("token_density") or token_per_char
    input_language: Optional[str] = meta_block.get("input_language")
    input_size_bytes: Optional[int] = meta_block.get("input_size_bytes")

    log_utc_access(
        request_id=ctx["request_id"],
        source=ctx["source"],
        endpoint=endpoint,
        status="ok",
        http_status=200,
        lambda_duration_ms=ctx["lambda_duration_ms"],
        cold_start=ctx["cold_start"],
        model=model,
        char_count=char_count,
        input_size_bytes=input_size_bytes,
        token_count=token_count,
        token_density=token_density,
        input_language=input_language,
        processing_time_ms=processing_time_ms,
        error_code=None,
        error_message=None,
        extra=None,
    )


def _emit_utc_structured_log_error(
    *,
    request: Request,
    req: TokenCountRequest,
    error: Exception,
) -> None:
    """
    想定外エラー時の UTC 構造化アクセスログ出力。
    UtcError は専用ハンドラで処理する前提のため、ここでは扱わない。
    """
    endpoint = str(request.url.path)
    ctx = _extract_lambda_context(request)
    processing_time_ms = _get_processing_time_ms(request)

    # 可能な範囲で入力規模だけは入れておく
    input_size_bytes: Optional[int] = None
    try:
        input_size_bytes = len(req.text.encode("utf-8"))
    except Exception:
        input_size_bytes = None

    log_utc_access(
        request_id=ctx["request_id"],
        source=ctx["source"],
        endpoint=endpoint,
        status="error",
        http_status=500,
        lambda_duration_ms=ctx["lambda_duration_ms"],
        cold_start=ctx["cold_start"],
        model=req.model,
        char_count=None,
        input_size_bytes=input_size_bytes,
        token_count=None,
        token_density=None,
        input_language=None,
        processing_time_ms=processing_time_ms,
        error_code="INTERNAL_ERROR",
        error_message=str(error),
        extra=None,
    )

