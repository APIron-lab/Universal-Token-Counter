from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from core.token_counter import UtcError

API_VERSION = "0.1.0"


# エラーコード（文字列表現） → 日本語メッセージ
ERROR_MESSAGES = {
    "INVALID_TYPE": "型が不正です。",
    "EMPTY_TEXT": "入力テキストが空です。",
    "UNSUPPORTED_MODEL": "未対応のモデルです。",
    "PAYLOAD_TOO_LARGE": "入力サイズが大きすぎます。",
}

# エラーコード（文字列表現） → 英語ヒント
ERROR_HINTS = {
    "INVALID_TYPE": "Check that 'model' and 'text' are strings.",
    "EMPTY_TEXT": "Provide non-empty text (not only whitespace).",
    "UNSUPPORTED_MODEL": "Use a supported model name for this API.",
    "PAYLOAD_TOO_LARGE": "Reduce the input size or split the request.",
}

# エラーコード（文字列表現） → HTTPステータス
ERROR_HTTP_STATUS = {
    "INVALID_TYPE": 400,
    "EMPTY_TEXT": 422,
    "UNSUPPORTED_MODEL": 400,
    "PAYLOAD_TOO_LARGE": 413,
}


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(UtcError)
    async def utc_error_handler(_, exc: UtcError) -> JSONResponse:
        # UtcError 側では code は既に "EMPTY_TEXT" などの文字列になっている想定
        code_str = str(exc.code)

        status = ERROR_HTTP_STATUS.get(code_str, 500)
        message = ERROR_MESSAGES.get(code_str, str(exc))
        hint = ERROR_HINTS.get(code_str, "Check your request and try again.")

        body = {
            "error": {
                "code": code_str,    # そのまま "EMPTY_TEXT" 等を返す
                "message": message,  # 日本語メッセージ
                "hint": hint,        # 英語ヒント
            },
            "meta": {
                "version": API_VERSION,
                "utc_timestamp": _now_utc_iso(),
            },
        }
        return JSONResponse(status_code=status, content=body)

