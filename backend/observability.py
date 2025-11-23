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


# === サービス共通メタ情報 =====================================================

SERVICE_NAME = os.getenv("UTC_SERVICE_NAME", "utc")
SERVICE_VERSION = os.getenv("UTC_VERSION", "0.1.0")
DEFAULT_SOURCE = os.getenv("UTC_SOURCE", "lambda_url")


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


# === 既存ドメイン別ログ関数（従来のまま残す） ==============================

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


# === UTC 構造化アクセスログ (v0.1) ==========================================

def build_utc_log_record(
    *,
    request_id: Optional[str],
    source: Optional[str],
    endpoint: str,
    status: str,
    http_status: int,
    # Lambda 側メトリクス
    lambda_duration_ms: Optional[float],
    cold_start: Optional[bool],
    # core 側メトリクス（成功時）
    model: Optional[str] = None,
    char_count: Optional[int] = None,
    input_size_bytes: Optional[int] = None,
    token_count: Optional[int] = None,
    token_density: Optional[float] = None,
    input_language: Optional[str] = None,
    processing_time_ms: Optional[float] = None,
    # エラー情報
    error_code: Optional[str] = None,
    error_message: Optional[str] = None,
    # 拡張フィールド
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    UTC Logging Requirements v0.1 に準拠した構造化ログレコードを組み立てる。

    注意:
      - テキスト本文などの PII はここに渡さないこと。
      - 1 リクエストにつき 1 レコード。
    """
    record: Dict[str, Any] = {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "request_id": request_id,
        "source": source or DEFAULT_SOURCE,
        "endpoint": endpoint,
        "status": status,
        "http_status": http_status,
        "lambda_duration_ms": lambda_duration_ms,
        "cold_start": cold_start,
        # core メトリクス
        "model": model,
        "char_count": char_count,
        "input_size_bytes": input_size_bytes,
        "token_count": token_count,
        "token_density": token_density,
        "input_language": input_language,
        "processing_time_ms": processing_time_ms,
        # エラー情報
        "error_code": error_code,
        "error_message": error_message,
    }

    if extra:
        record.update(extra)

    return record


def log_utc_access(
    *,
    request_id: Optional[str],
    source: Optional[str],
    endpoint: str,
    status: str,
    http_status: int,
    lambda_duration_ms: Optional[float],
    cold_start: Optional[bool],
    model: Optional[str],
    char_count: Optional[int],
    input_size_bytes: Optional[int],
    token_count: Optional[int],
    token_density: Optional[float],
    input_language: Optional[str],
    processing_time_ms: Optional[float],
    error_code: Optional[str] = None,
    error_message: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """
    UTC v0.1 アクセスログ 1 レコードを出力する。
    """
    record = build_utc_log_record(
        request_id=request_id,
        source=source,
        endpoint=endpoint,
        status=status,
        http_status=http_status,
        lambda_duration_ms=lambda_duration_ms,
        cold_start=cold_start,
        model=model,
        char_count=char_count,
        input_size_bytes=input_size_bytes,
        token_count=token_count,
        token_density=token_density,
        input_language=input_language,
        processing_time_ms=processing_time_ms,
        error_code=error_code,
        error_message=error_message,
        extra=extra,
    )

    level = "INFO" if status == "ok" else "ERROR"
    _log_json(level, record)

