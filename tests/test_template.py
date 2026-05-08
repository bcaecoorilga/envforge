"""Tests for envforge.template."""
import pytest
from envforge.template import (
    TemplateError,
    create_template,
    fill_template,
    list_unfilled,
)


# ---------------------------------------------------------------------------
# create_template
# ---------------------------------------------------------------------------

def test_create_template_returns_dict():
    t = create_template("dev", ["DB_HOST", "DB_PORT"])
    assert isinstance(t, dict)


def test_create_template_sets_label():
    t = create_template("dev", ["DB_HOST"])
    assert t["label"] == "dev"


def test_create_template_sets_is_template_flag():
    t = create_template("dev", ["DB_HOST"])
    assert t["is_template"] is True


def test_create_template_uses_placeholder_for_missing_defaults():
    t = create_template("dev", ["DB_HOST"])
    assert t["variables"]["DB_HOST"] == "<required>"


def test_create_template_uses_provided_default():
    t = create_template("dev", ["DB_PORT"], defaults={"DB_PORT": "5432"})
    assert t["variables"]["DB_PORT"] == "5432"


def test_create_template_custom_placeholder():
    t = create_template("dev", ["SECRET"], placeholder="CHANGEME")
    assert t["variables"]["SECRET"] == "CHANGEME"


def test_create_template_raises_on_empty_label():
    with pytest.raises(TemplateError, match="label"):
        create_template("", ["KEY"])


def test_create_template_raises_on_invalid_keys():
    with pytest.raises(TemplateError):
        create_template("dev", "not-a-list")  # type: ignore


def test_create_template_raises_on_empty_key_name():
    with pytest.raises(TemplateError):
        create_template("dev", [""])


# ---------------------------------------------------------------------------
# fill_template
# ---------------------------------------------------------------------------

def _make_template():
    return create_template(
        "dev",
        ["DB_HOST", "DB_PORT", "SECRET_KEY"],
        defaults={"DB_PORT": "5432"},
    )


def test_fill_template_replaces_placeholder():
    t = _make_template()
    filled = fill_template(t, {"DB_HOST": "localhost", "SECRET_KEY": "abc"})
    assert filled["variables"]["DB_HOST"] == "localhost"


def test_fill_template_preserves_default_value():
    t = _make_template()
    filled = fill_template(t, {"DB_HOST": "localhost", "SECRET_KEY": "abc"})
    assert filled["variables"]["DB_PORT"] == "5432"


def test_fill_template_clears_is_template_flag():
    t = _make_template()
    filled = fill_template(t, {"DB_HOST": "localhost", "SECRET_KEY": "abc"})
    assert filled["is_template"] is False


def test_fill_template_sets_checksum():
    t = _make_template()
    filled = fill_template(t, {"DB_HOST": "localhost", "SECRET_KEY": "abc"})
    assert filled["checksum"] is not None


def test_fill_template_raises_on_missing_required():
    t = _make_template()
    with pytest.raises(TemplateError, match="SECRET_KEY"):
        fill_template(t, {"DB_HOST": "localhost"})


def test_fill_template_allow_missing_does_not_raise():
    t = _make_template()
    filled = fill_template(t, {"DB_HOST": "localhost"}, allow_missing=True)
    assert "SECRET_KEY" in filled["variables"]


def test_fill_template_raises_on_non_template():
    with pytest.raises(TemplateError, match="not a template"):
        fill_template({"label": "x", "variables": {}, "is_template": False}, {})


# ---------------------------------------------------------------------------
# list_unfilled
# ---------------------------------------------------------------------------

def test_list_unfilled_returns_placeholder_keys():
    t = _make_template()
    unfilled = list_unfilled(t)
    assert "DB_HOST" in unfilled
    assert "SECRET_KEY" in unfilled


def test_list_unfilled_excludes_defaulted_keys():
    t = _make_template()
    unfilled = list_unfilled(t)
    assert "DB_PORT" not in unfilled


def test_list_unfilled_empty_when_all_defaults_set():
    t = create_template("dev", ["A"], defaults={"A": "val"})
    assert list_unfilled(t) == []


def test_list_unfilled_raises_on_non_template():
    with pytest.raises(TemplateError):
        list_unfilled({"is_template": False, "variables": {}})
