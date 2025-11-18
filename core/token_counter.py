from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict

import langdetect
import tiktoken

# 対応モデルと encoding 名のマッピング（UTC v0.1仕様）
SUPPORTED_MODELS: Dict[str, str] = {
    "gpt-4o": "o200k_base",
    "gpt-4.1": "o200k_base",
    "gpt-4.1-mini": "o200k_base",
    "gpt-4-turbo": "o200k_base",
    "gpt-4": "cl100k_base",
    "gpt-3.5-turbo": "cl100k_base",
}

# 入力制限（UTC v0.1仕様）
MAX_CHAR_COUNT: int = 100_000
MAX_BYTES: int = 512 * 1024  # 512KB


class UtcErrorCode:
    """UTC 内部で利用するエラーコード（API レイヤーで JSON にマッピングする前段）"""

    INVALID_TYPE = "INVALID_TYPE"
    EMPTY_TEXT = "EMPTY_TEXT"
    UNSUPPORTED_MODEL = "UNSUPPORTED_MODEL"
    PAYLOAD_TOO_LARGE = "PAYLOAD_TOO_LARGE"


class UtcError(Exception):
    """UTC ドメインエラー。code で種別を識別し、API 層で HTTP / message / hint に変換する。"""

    def __init__(self, code: str, detail: str | None = None) -> None:
        self.code = code
        self.detail = detail or code
        super().__init__(self.detail)


def _detect_language(text: str) -> str:
    """langdetect を用いた言語判定。失敗した場合は 'unknown' を返す。"""
    try:
        return langdetect.detect(text)
    except Exception:
        return "unknown"


def count_tokens(model: str, text: str, *, version: str = "0.1.0") -> Dict[str, Any]:
    """
    UTC のコア処理。
    - モデルとテキストを受け取り
    - トークン数と各種メタ情報を計算し
    - UTC v0.1 仕様の result + meta 形式で返す

    エラー条件（バリデーション）は UtcError として送出される。
    """
    started_at = time.perf_counter()

    # 型チェック
    if not isinstance(model, str) or not isinstance(text, str):
        raise UtcError(UtcErrorCode.INVALID_TYPE, "model and text must be strings")

    # 空文字・空白のみチェック
    if text.strip() == "":
        raise UtcError(UtcErrorCode.EMPTY_TEXT, "text must not be empty")

    # モデル対応チェック
    encoding_name = SUPPORTED_MODELS.get(model)
    if encoding_name is None:
        raise UtcError(UtcErrorCode.UNSUPPORTED_MODEL, f"Unsupported model: {model}")

    # サイズチェック
    char_count = len(text)
    input_bytes = text.encode("utf-8")
    input_size_bytes = len(input_bytes)

    if char_count > MAX_CHAR_COUNT or input_size_bytes > MAX_BYTES:
        raise UtcError(
            UtcErrorCode.PAYLOAD_TOO_LARGE,
            f"Size exceeded (chars={char_count}, bytes={input_size_bytes})",
        )

    # トークナイズ
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)
    token_count = len(tokens)

    # 各種統計値
    token_per_char = token_count / char_count if char_count else 0.0
    token_density = token_count / input_size_bytes if input_size_bytes else 0.0
    input_language = _detect_language(text)

    processing_time_ms = (time.perf_counter() - started_at) * 1000.0
    utc_timestamp = datetime.now(timezone.utc).isoformat()

    result: Dict[str, Any] = {
        "model": model,
        "encoding": encoding_name,
        "char_count": char_count,
        "token_count": token_count,
        "token_per_char": token_per_char,
    }

    meta: Dict[str, Any] = {
        "input_language": input_language,
        "input_size_bytes": input_size_bytes,
        "token_density": token_density,
        "model_family": "openai",
        "processing_time_ms": processing_time_ms,
        "utc_timestamp": utc_timestamp,
        "version": version,
    }

    return {"result": result, "meta": meta}

