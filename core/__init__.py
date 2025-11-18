# core/__init__.py

"""
APIron サービス群で共通利用するビジネスロジックパッケージ。

ここには Web フレームワークや AWS ランタイムに依存しない
純粋な Python ロジックのみを配置する。
"""

from .token_counter import TokenCountRequest, TokenCountResult, count_tokens

__all__ = [
    "TokenCountRequest",
    "TokenCountResult",
    "count_tokens",
]

