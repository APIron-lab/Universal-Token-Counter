# lambda_http/main.py
from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict

from mangum import Mangum
from backend.fastapi_app.main import app

# ============================================================================
# ロガー設定（Lambda エッジ用の構造化ログ）
# ============================================================================

LOG_LEVEL = os.getenv("UTC_LAMBDA_LOG_LEVEL", "INFO").upper()
SERVICE_NAME = os.getenv("UTC_SERVICE_NAME", "utc")
SERVICE_VERSION = os.getenv("UTC_SERVICE_VERSION", "0.1.0")

logger = logging.getLogger("utc_lambda")

if not logger.handlers:
    logger.setLevel(LOG_LEVEL)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s\t%(levelname)s\t%(message)s",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def _log_edge(payload: Dict[str, Any]) -> None:
    """Lambda エッジでの統一的な構造化ログ出力"""
    base = {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
    }
    base.update(payload)
    logger.info(json.dumps(base, ensure_ascii=False))


# ============================================================================
# Mangum ハンドラ生成（ステージ名に応じて base path を動的切り替え）
# ============================================================================

def _create_mangum_handler(event: Dict[str, Any]) -> Mangum:
    """
    API Gateway / Lambda URL からの event からステージ名を判定し、
    /dev, /prod, /$default などに応じて api_gateway_base_path を設定した Mangum を生成する。
    """
    request_context = event.get("requestContext", {}) or {}

    # HTTP API / REST API / Lambda URL いずれにもそこそこ対応できるように汎用取得
    stage = request_context.get("stage")

    # $default や None の場合はステージ prefix なし
    if stage and stage != "$default":
        base_path = f"/{stage}"
    else:
        base_path = ""

    # base_path が空文字の場合は None を渡す（Mangum に任せる）
    api_gateway_base_path = base_path or None

    return Mangum(app, api_gateway_base_path=api_gateway_base_path)


# ============================================================================
# AWS Lambda エントリポイント
# ============================================================================

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    - リクエストごとに Mangum ハンドラを生成（ステージに応じた base path を設定）
    - FastAPI を実行
    - 結果を API Gateway / Lambda URL 形式で返却
    - ついでに Lambda エッジの構造化ログを出力
    """
    start = time.perf_counter()

    mangum_handler = _create_mangum_handler(event)
    response = mangum_handler(event, context)

    duration_ms = (time.perf_counter() - start) * 1000.0

    # event からメタ情報を抽出
    request_context = event.get("requestContext", {}) or {}
    http_info = request_context.get("http", {}) or {}

    stage = request_context.get("stage")
    method = http_info.get("method") or event.get("requestContext", {}).get("httpMethod")
    raw_path = event.get("rawPath") or http_info.get("path")
    source_ip = http_info.get("sourceIp") or request_context.get("identity", {}).get("sourceIp")

    status_code = None
    try:
        status_code = int(response.get("statusCode"))  # type: ignore[arg-type]
    except Exception:
        # 念のため安全側に倒す
        status_code = None

    # ログ出力（CloudWatch Logs 用）
    _log_edge(
        {
            "request_id": getattr(context, "aws_request_id", None),
            "source": "apigw" if stage is not None else "lambda_url",
            "stage": stage,
            "endpoint": raw_path,
            "http_method": method,
            "status": "ok" if (status_code and 200 <= status_code < 500) else "error",
            "http_status": status_code,
            "lambda_duration_ms": round(duration_ms, 3),
            "cold_start": getattr(context, "get_remaining_time_in_millis", None) is not None,
            "source_ip": source_ip,
            "error_code": None,
            "error_message": None,
        }
    )

    return response

