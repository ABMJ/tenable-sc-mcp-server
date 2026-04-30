from tenable_sc_mcp.server import _query_params, _select_response_path, tsc_resource_docs


def test_query_params_merge_fields_expand_and_editable() -> None:
    merged = _query_params(
        params={"foo": "bar"},
        fields=["id", "name"],
        expand=["assets"],
        editable=True,
    )
    assert merged["foo"] == "bar"
    assert merged["fields"] == "id,name"
    assert merged["expand"] == "assets"
    assert "editable" in merged


def test_select_response_path_handles_nested_dicts_and_lists() -> None:
    payload = {"response": {"items": [{"id": 7}, {"id": 8}]}}
    value = _select_response_path(payload, "response.items.1.id")
    assert value == 8


def test_resource_docs_unknown_returns_error() -> None:
    result = tsc_resource_docs("not-a-resource")
    assert result["ok"] is False
    assert "possible_matches" in result
