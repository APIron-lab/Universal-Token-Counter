import pytest

import core.token_counter as tc
from core.token_counter import (
    MAX_BYTES,
    MAX_CHAR_COUNT,
    SUPPORTED_MODELS,
    UtcError,
    UtcErrorCode,
    count_tokens,
)


def test_count_tokens_basic_ja():
    """日本語テキストでの基本的な正常系の確認。"""
    model = "gpt-4o"
    text = "これはトークンカウンターのテストです。"

    data = count_tokens(model, text)

    assert "result" in data
    assert "meta" in data

    result = data["result"]
    meta = data["meta"]

    # result の検証
    assert result["model"] == model
    assert result["encoding"] == SUPPORTED_MODELS[model]
    assert result["char_count"] == len(text)
    assert isinstance(result["token_count"], int)
    assert result["token_count"] > 0
    assert result["token_per_char"] > 0

    # meta の検証
    assert meta["input_language"] in ("ja", "en", "unknown")
    assert meta["input_size_bytes"] >= result["char_count"]
    assert meta["token_density"] > 0
    assert meta["model_family"] == "openai"
    assert isinstance(meta["processing_time_ms"], float)
    assert meta["processing_time_ms"] >= 0
    assert isinstance(meta["utc_timestamp"], str)
    assert meta["version"] == "0.1.0"


def test_unsupported_model_raises_error():
    """未対応モデルを指定した場合は UtcError(UNSUPPORTED_MODEL) を送出する。"""
    with pytest.raises(UtcError) as exc:
        count_tokens("gpt-9x", "test")

    assert exc.value.code == UtcErrorCode.UNSUPPORTED_MODEL


def test_empty_text_raises_error():
    """空文字列・空白のみの text は UtcError(EMPTY_TEXT)。"""
    with pytest.raises(UtcError) as exc:
        count_tokens("gpt-4o", "   ")

    assert exc.value.code == UtcErrorCode.EMPTY_TEXT


def test_payload_too_large_by_char_count():
    """文字数上限を超えた場合は PAYLOAD_TOO_LARGE。"""
    large_text = "a" * (MAX_CHAR_COUNT + 1)

    with pytest.raises(UtcError) as exc:
        count_tokens("gpt-4o", large_text)

    assert exc.value.code == UtcErrorCode.PAYLOAD_TOO_LARGE


def test_payload_too_large_by_bytes():
    """バイトサイズ上限を超えた場合も PAYLOAD_TOO_LARGE。"""
    # "あ" は UTF-8 で3バイトなので、かなり少ない文字数で 512KB を超えられる
    large_text = "あ" * ((MAX_BYTES // 3) + 10)

    with pytest.raises(UtcError) as exc:
        count_tokens("gpt-4o", large_text)

    assert exc.value.code == UtcErrorCode.PAYLOAD_TOO_LARGE


def test_language_detection_failure_falls_back_to_unknown(monkeypatch):
    """langdetect.detect が例外を投げた場合に 'unknown' へフォールバックすることを確認。"""

    def fake_detect(_text: str) -> str:
        raise RuntimeError("langdetect failed")

    # core.token_counter モジュール内の langdetect.detect を差し替える
    monkeypatch.setattr(tc.langdetect, "detect", fake_detect)

    data = tc.count_tokens("gpt-4o", "language fallback test")

    meta = data["meta"]
    assert meta["input_language"] == "unknown"

