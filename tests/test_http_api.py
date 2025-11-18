from fastapi.testclient import TestClient

from backend.fastapi_app.main import app

client = TestClient(app)


def test_token_count_success():
    payload = {"model": "gpt-4o", "text": "これはテストです"}
    resp = client.post("/utc/v0/token-count", json=payload)

    assert resp.status_code == 200

    data = resp.json()
    assert "result" in data
    assert "meta" in data

    result = data["result"]
    meta = data["meta"]

    # result の基本項目
    assert result["model"] == "gpt-4o"
    assert isinstance(result["encoding"], str)
    assert isinstance(result["char_count"], int)
    assert isinstance(result["token_count"], int)
    assert isinstance(result["token_per_char"], float)

    # meta の基本項目
    assert "input_language" in meta
    assert "input_size_bytes" in meta
    assert "token_density" in meta
    assert "model_family" in meta
    assert "processing_time_ms" in meta
    assert "utc_timestamp" in meta
    assert "version" in meta


def test_token_count_empty_text_error():
    # スペースのみ → EMPTY_TEXT エラーになる想定
    payload = {"model": "gpt-4o", "text": "   "}
    resp = client.post("/utc/v0/token-count", json=payload)

    # 4xx 系で返ってくることだけを保証（400/422 など）
    assert 400 <= resp.status_code < 500

    data = resp.json()
    assert "error" in data
    assert "meta" in data

    err = data["error"]

    # UTC / APIron Error Spec 準拠の error 形式
    assert err["code"] == "EMPTY_TEXT"
    assert isinstance(err["message"], str)
    assert isinstance(err["hint"], str)

