[![CI](https://github.com/APIron-lab/Universal-Token-Counter/actions/workflows/ci.yml/badge.svg)](https://github.com/APIron-lab/Universal-Token-Counter/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/APIron-lab/Universal-Token-Counter/graph/badge.svg?token=J5TxfxeKRu)](https://codecov.io/gh/APIron-lab/Universal-Token-Counter)
# 🔢 Universal Token Counter (UTC)

High-precision token counting API for multilingual text, powered by OpenAI-compatible encodings.

**🇯🇵 日本語での説明は本ページ下部の「Japanese Overview」セクションにあります。**

---

## 🚀 Features
- Accurate token counting using OpenAI-compatible encodings (`tiktoken`)
- Language detection (`langdetect`)
- Unified result + meta response format (UTC Spec v0.1)
- Detailed domain errors (INVALID_TYPE, EMPTY_TEXT, etc.)
- Fully tested with pytest
- Lightweight core-first architecture for easy integration into any API system

---

## 🧱 Architecture (APIron Core-first)

```
universal-token-counter/
├── core/                 # UTC core logic
│   ├── token_counter.py
│   └── __init__.py
├── backend/              # Web API layer (Django/FastAPI)
├── lambda_http/          # AWS Lambda handler
├── tests/                # pytest
├── .github/workflows/    # CI
├── requirements.txt
└── README.md
```

---

## 📦 Installation

### Clone the repository
```bash
git clone https://github.com/APIron-lab/Universal-Token-Counter.git
cd Universal-Token-Counter
```

### Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🧪 Testing

```bash
pytest
```

All tests should pass:

```
5 passed in X.XXs
```

---

## 🧩 Example Usage (Python)

```python
from core.token_counter import count_tokens

model = "gpt-4o"
text = "Hello, world!"

data = count_tokens(model, text)

print(data["result"])
print(data["meta"])
```

---

## 📘 Supported Models

| Model            | Encoding       |
|------------------|----------------|
| gpt-4o           | o200k_base     |
| gpt-4.1          | o200k_base     |
| gpt-4.1-mini     | o200k_base     |
| gpt-4-turbo      | o200k_base     |
| gpt-4            | cl100k_base    |
| gpt-3.5-turbo    | cl100k_base    |

---

## 🧮 Success Response (UTC Spec v0.1)

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
    "utc_timestamp": "2025-01-01T00:00:00+00:00",
    "version": "0.1.0"
  }
}
```

---

## ❌ Error Response (Unified APIron Error Spec)

```json
{
  "error": {
    "code": "EMPTY_TEXT",
    "message": "入力テキストが空です。",
    "hint": "Text must not be empty."
  },
  "meta": {
    "version": "0.1.0",
    "utc_timestamp": "2025-01-01T00:00:00+00:00",
    "processing_time_ms": 0.52
  }
}
```

### Error Codes

| Code                | Description                      |
|---------------------|----------------------------------|
| INVALID_JSON        | Invalid JSON format              |
| MISSING_FIELD       | Required fields missing          |
| INVALID_TYPE        | Wrong input type                 |
| EMPTY_TEXT          | Text is empty or whitespace only |
| UNSUPPORTED_MODEL   | Unsupported model name           |
| PAYLOAD_TOO_LARGE   | Input exceeds size constraints   |
| INTERNAL_ERROR      | Unexpected internal exception    |

---

## ☁ Roadmap (Universal Token Series)
- UTC Efficiency Mode (高速計測)
- Batch Counter
- Model Comparison Tool
- RapidAPI distribution (Free → Pro)

---

## 📝 License
MIT License

---

# 🇯🇵 Japanese Overview（日本語による説明）

## 概要
Universal Token Counter (UTC) は、任意のテキストを OpenAI 互換エンコーディングで  
**高精度にトークン数を算出するツール**です。

結果は **`result` + `meta` の2階層構造**で返されます。

## 特徴
- OpenAI モデルに対応したトークン数の計測
- 日本語・英語など多言語テキストの判定
- 文字数・トークン密度・バイト数を統計として返却
- APIron の統一エラーレスポンス仕様に準拠

## 使い方（Python）

```python
from core.token_counter import count_tokens
data = count_tokens("gpt-4o", "これはテストです。")
```

## 正常レスポンス（概要）
- `result`: モデル・文字数・トークン数  
- `meta`: 言語判定・処理時間・バイト数・UTCタイムスタンプ

## エラー仕様
APIron Error Spec に準拠：

- INVALID_TYPE（型不正）
- EMPTY_TEXT（テキストが空）
- UNSUPPORTED_MODEL（未対応モデル）
- PAYLOAD_TOO_LARGE（上限超過）

---

## Maintainer
APIron-lab  
https://github.com/APIron-lab

