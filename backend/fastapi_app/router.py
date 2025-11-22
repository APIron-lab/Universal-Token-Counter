# backend/fastapi_app/router.py
from fastapi import APIRouter, HTTPException

from core.token_counter import count_tokens, UtcError
from .schemas import TokenCountRequest, TokenCountSuccessResponse

# 追加：観測用ロガー
from backend.observability import (
    log_token_count_success,
    log_unhandled_error,
    log_logging_failure,
)

router = APIRouter()


@router.post("/token-count", response_model=TokenCountSuccessResponse)
async def token_count(req: TokenCountRequest) -> TokenCountSuccessResponse:
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
        #       ...
        #   }
        # }
        try:
            result_block = result.get("result", {}) if isinstance(result, dict) else {}
            meta_block = result.get("meta", {}) if isinstance(result, dict) else {}

            log_token_count_success(
                model=result_block.get("model", req.model),
                char_count=result_block.get("char_count", len(req.text)),
                token_count=result_block.get("token_count", 0),
                meta=meta_block,
            )
        except Exception as log_exc:
            # ログ出力に失敗しても API のレスポンスは壊さない
            log_logging_failure(log_exc)

        return result  # FastAPI が response_model に合わせてシリアライズ

    except UtcError as e:
        # UtcError は専用ハンドラに任せる
        raise e

    except Exception as exc:
        # 想定外のエラーは 500 でまとめ、内容はログに送る
        log_unhandled_error(exc)
        raise HTTPException(status_code=500, detail="Unhandled internal error.")

