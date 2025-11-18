from fastapi import APIRouter, HTTPException

from core.token_counter import count_tokens, UtcError
from .schemas import TokenCountRequest, TokenCountSuccessResponse

router = APIRouter()


@router.post("/token-count", response_model=TokenCountSuccessResponse)
async def token_count(req: TokenCountRequest) -> TokenCountSuccessResponse:
    try:
        # コアロジック呼び出し（成功時は UTC v0.1 形式の dict が返る）
        result = count_tokens(req.model, req.text)
        return result  # FastAPI が response_model に合わせてシリアライズ
    except UtcError as e:
        # UtcError は専用ハンドラに任せる
        raise e
    except Exception:
        # 想定外のエラーは 500 でまとめる（詳細はログ側で扱う想定）
        raise HTTPException(status_code=500, detail="Unhandled internal error.")

