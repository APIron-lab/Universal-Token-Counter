# backend/observability.py
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional


# === ロガー初期化 ============================================================

LOG_LEVEL = os.getenv("UTC_LOG_LEVEL", "INFO").upper()
LOGGER_NAME = "utc"


logger = logging.getLogger(LOGGER_NAME)

# Lambda 環境で二重ハンドラを避けるためのチェック
if not logger.handlers:
    logger.setLevel(LOG_LEVEL)

    handler = logging.StreamHandler()
    # CloudWatch Logs で扱いやすいよう、タブ区切り + 1行 JSON に寄せる
    formatter = logging.Formatter(
        fmt="%(asctime)s\t%(levelname)s\t%(message)s",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# === 共通ユーティリティ =====================================================

def _log_json(level: str, payload: Dict[str, Any]) -> None:
    """
    すべてのアプリケーションログを 1行JSON で出力する。
    """
    text = json.dumps(payload, ensure_ascii=False)

    if level == "INFO":
        logger.info(text)
    elif level == "WARNING":
        logger.warning(text)
    elif level == "ERROR":
        logger.error(text)
    else:
        logger.debug(text)


# === ドメイン別ログ関数 =====================================================

def log_token_count_success(
    *,
    model: str,
    char_count: int,
    token_count: int,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    """
    正常終了時のトークンカウント結果をログ出力する。
    CloudWatch Logs 上では filter pattern を
        { $.event = "token_count_success" }
    などで拾えるようにしておく想定。
    """
    payload: Dict[str, Any] = {
        "event": "token_count_success",
        "model": model,
        "char_count": char_count,
        "token_count": token_count,
    }
    if meta is not None:
        payload["meta"] = meta

    _log_json("INFO", payload)


def log_unhandled_error(exc: Exception) -> None:
    """
    想定外エラーを 500 にまとめる前にログ出力する。
    """
    payload = {
        "event": "unhandled_error",
        "error_type": type(exc).__name__,
        "error_message": str(exc),
    }
    _log_json("ERROR", payload)


def log_logging_failure(exc: Exception) -> None:
    """
    ログ出力自体に失敗した場合の保険。
    アプリの動作を止めないために簡素なエラーログのみ出す。
    """
    logger.error("logging_failure: %s: %s", type(exc).__name__, str(exc))

