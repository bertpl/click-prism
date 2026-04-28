from __future__ import annotations

from click_prism._tree.params import ParamInfo


def test_param_info_placeholder_shape() -> None:
    # --- arrange / act ----------------
    p = ParamInfo(name="foo", param_type="option")
    # --- assert -----------------------
    assert p.declarations == []
    assert p.required is False
