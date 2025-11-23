
# Universal Token Counter (UTC)

High-precision multilingual token counting API with OpenAI-compatible encodings and a clean Core-first architecture.

[![CI](https://github.com/APIron-lab/Universal-Token-Counter/actions/workflows/ci.yml/badge.svg)](https://github.com/APIron-lab/Universal-Token-Counter/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/APIron-lab/Universal-Token-Counter/graph/badge.svg?token=J5TxfxeKRu)](https://codecov.io/gh/APIron-lab/Universal-Token-Counter)

## 🌐 Official Hosted API (Free Plan Available)

Universal Token Counter (UTC) is also available as a hosted API on RapidAPI.

Use the hosted version here:  
https://rapidapi.com/APIronlab/api/universal-token-counter-utc


## 🇯🇵 Japanese Overview（日本語版は後半に掲載）

本 README の後半に日本語版の包括的な解説があります。

---

## 🚀 Features
- Accurate token counting (OpenAI / tiktoken encoding)
- FastAPI HTTP API endpoint (`/utc/v0/token-count`)
- Python Core API usage (`core.token_counter`)
- Unified `result + meta` response (UTC Spec v0.1)
- Structured error responses (APIron Error Spec)
- Language detection
- High test coverage (pytest + Codecov)
- Core-first architecture for easy extension
- Production-ready packaging for AWS Lambda

This repository is the open-core implementation of APIron “Universal Token Series”.
Commercial versions (RapidAPI) will include extended features.

---

## 🧱 Project Architecture (APIron Core-first Standard)

```
universal-token-counter/
├── core/                     # Core token counting logic
│   ├── token_counter.py
│   └── __init__.py
├── backend/
│   └── fastapi_app/          # HTTP API (FastAPI)
│        ├── main.py
│        ├── router.py
│        ├── handlers.py
│        └── schemas.py
├── tests/                    # pytest unit tests
├── .github/workflows/        # CI
├── requirements.txt
└── README.md
```

---

# ⚡ HTTP API (FastAPI)

## Start API locally

```
python -m backend.fastapi_app.main
```

Server starts at:

```
http://127.0.0.1:8000
```

## Endpoint

```
POST /utc/v0/token-count
```

### Request Example (curl)

```bash
curl -X POST "http://127.0.0.1:8000/utc/v0/token-count"   -H "Content-Type: application/json"   -d '{"model":"gpt-4o","text":"これはテストです"}'
```

---

# 🧩 Python Core Usage

```python
from core.token_counter import count_tokens

data = count_tokens("gpt-4o", "Hello world!")
print(data["result"])
print(data["meta"])
```

---

# 🌐 Node.js Example (fetch)

```js
const res = await fetch("http://127.0.0.1:8000/utc/v0/token-count", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ model: "gpt-4o", text: "Hello world!" })
});
console.log(await res.json());
```

---

# 📘 Supported Models

| Model          | Encoding     |
|----------------|--------------|
| gpt-4o         | o200k_base   |
| gpt-4.1        | o200k_base   |
| gpt-4.1-mini   | o200k_base   |
| gpt-4-turbo    | o200k_base   |
| gpt-4          | cl100k_base  |
| gpt-3.5-turbo  | cl100k_base  |

---

# 🧮 Success Response (UTC Spec v0.1)

```json
{
  "result": {
    "model": "gpt-4o",
    "encoding": "o200k_base",
    "char_count": 12,
    "token_count": 9,
    "token_per_char": 0.75
  },
  "meta": {
    "input_language": "en",
    "input_size_bytes": 36,
    "token_density": 0.25,
    "model_family": "openai",
    "processing_time_ms": 1.42,
    "utc_timestamp": "2025-01-01T00:00:00Z",
    "version": "0.1.0"
  }
}
```

---

# ❌ Error Response (APIron Error Spec)

```json
{
  "error": {
    "code": "EMPTY_TEXT",
    "message": "入力テキストが空です。",
    "hint": "Provide non-empty text (not only whitespace)."
  },
  "meta": {
    "version": "0.1.0",
    "utc_timestamp": "2025-01-01T00:00:00Z"
  }
}
```

### Error Codes

| Code              | Meaning                     | HTTP |
|-------------------|-----------------------------|------|
| INVALID_TYPE      | Wrong input type            | 400  |
| EMPTY_TEXT        | Text is empty or spaces     | 422  |
| UNSUPPORTED_MODEL | Model not supported         | 400  |
| PAYLOAD_TOO_LARGE | Input too large             | 413  |

---

# ☁ Roadmap (Universal Token Series)

- UTC v1 (Pro Edition)
- UTC Efficiency Mode
- Universal Token Batch (UTB)
- Model Comparison Tool
- Universal Token Series productization
- RapidAPI release (Free → Pro upgrade)

---

# 🇯🇵 日本語版 README

## 概要
Universal Token Counter (UTC) は、OpenAI 互換エンコーディングで  
テキストのトークン数を高精度に算出する **軽量・高精度 API** です。

- Core ロジックは純粋関数として実装
- FastAPI により HTTP API として利用可能
- 結果は `result + meta` の 2 階層で返却
- APIron Error Spec に準拠
- AWS Lambda 上での運用に最適化可能

このリポジトリはオープンソース版であり、  
商用 RapidAPI 版では追加機能が提供される予定です。

## 🌐 公開API（無料プランあり）

Universal Token Counter (UTC) は RapidAPI からも利用できます。

ホスト版はこちら：  
https://rapidapi.com/APIronlab/api/universal-token-counter-utc

---

## FastAPI エンドポイント

```
POST /utc/v0/token-count
```

curl 例：

```bash
curl -X POST http://127.0.0.1:8000/utc/v0/token-count   -H "Content-Type: application/json"   -d '{"model":"gpt-4o","text":"これはテストです"}'
```

---

## エラー仕様（日本語）

| エラーコード         | 内容                     |
|----------------------|---------------------------|
| INVALID_TYPE         | 型が不正です             |
| EMPTY_TEXT           | 空文字または空白のみ     |
| UNSUPPORTED_MODEL    | 未対応のモデルです       |
| PAYLOAD_TOO_LARGE    | 入力サイズが大きすぎます |

---

## 今後の拡張

- 高速化バージョン（Pro版）
- バッチ処理 API
- モデル比較ツール
- 「Universal Token Series」シリーズ化

---

Maintainer  
APIron-lab  
https://github.com/APIron-lab


