# APIron Service Template

[![CI](https://github.com/APIron-lab/apiron-service-template/actions/workflows/ci.yml/badge.svg)](https://github.com/APIron-lab/apiron-service-template/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/APIron-lab/apiron-service-template/graph/badge.svg?token=LFHOO9akaC)](https://codecov.io/gh/APIron-lab/apiron-service-template)

---

## プレースホルダ版バッジ（テンプレート用）
```
[![CI](https://github.com/{GITHUB_USER}/{REPO}/actions/workflows/ci.yml/badge.svg)](https://github.com/{GITHUB_USER}/{REPO}/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/{GITHUB_USER}/{REPO}/branch/main/graph/badge.svg)](https://codecov.io/gh/{GITHUB_USER}/{REPO})
```

---

## プロジェクト構成
```
apiron-service-template/
├── core/
│   └── token_counter.py
├── backend/
│   ├── manage.py
│   ├── backend/
│   └── api/
├── lambda_http/
│   └── handler.py
├── tests/
│   └── test_token_counter.py
├── .github/workflows/ci.yml
├── requirements.txt
└── README.md
```

---

## 機能概要

- Core Logic（純粋 Python 関数）
- Django REST API（ローカル検証用）
- Lambda HTTP ラッパ（本番運用）
- pytest + coverage
- GitHub Actions + Codecov

---

## テスト実行
```
pytest
pytest --cov=core --cov-report=xml
```

---

## Lambda デプロイ例
```
zip -r lambda.zip handler.py ../core
```

---

## API 追加フロー

1. core にロジック追加  
2. Django 側に endpoint 追加  
3. Lambda handler 拡張  
4. pytest 作成  
5. push → CI → Codecov  
6. RapidAPI 登録  

---

