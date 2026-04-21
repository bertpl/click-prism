def test_import(pyproject) -> None:
    import click_prism

    assert click_prism.__version__ == pyproject["project"]["version"]
