from tenable_sc_mcp.catalog import API_RESOURCES, catalog_as_dict


def test_catalog_has_expected_shape() -> None:
    resources = catalog_as_dict()
    assert resources
    first = resources[0]
    assert "name" in first
    assert "path" in first
    assert "rest_path" in first
    assert first["rest_path"].startswith("/rest/")


def test_catalog_paths_are_unique() -> None:
    paths = [resource.path for resource in API_RESOURCES]
    assert len(paths) == len(set(paths))
