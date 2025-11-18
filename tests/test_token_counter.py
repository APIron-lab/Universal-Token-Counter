from core import TokenCountRequest, count_tokens


def test_count_tokens_basic():
    req = TokenCountRequest(text="Hello APIron world", model="gpt-4", language="en")
    result = count_tokens(req)

    assert result.model == "gpt-4"
    assert result.language == "en"
    assert result.text_length == len("Hello APIron world")
    # ダミー実装ではスペース区切りで 3 トークン
    assert result.token_count == 3


def test_count_tokens_empty_text():
    req = TokenCountRequest(text="", model="gpt-4")
    result = count_tokens(req)

    assert result.token_count == 0
    assert result.text_length == 0

