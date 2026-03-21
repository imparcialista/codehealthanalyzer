"""Testes para codehealthanalyzer.config."""

import pytest

from codehealthanalyzer.config import DEFAULT_TEMPLATE_DIRS, normalize_config
from codehealthanalyzer.exceptions import ConfigurationError


def test_none_returns_defaults():
    cfg = normalize_config(None)
    assert cfg["templates_dir"] == DEFAULT_TEMPLATE_DIRS
    assert cfg["exclude_dirs"] == []
    assert cfg["target_dir"] == "."
    assert cfg["no_default_excludes"] is False
    assert cfg["ruff_fix"] is False


def test_empty_dict_returns_defaults():
    cfg = normalize_config({})
    assert cfg["templates_dir"] == DEFAULT_TEMPLATE_DIRS


def test_partial_config_merges_correctly():
    cfg = normalize_config({"target_dir": "src"})
    assert cfg["target_dir"] == "src"
    assert cfg["templates_dir"] == DEFAULT_TEMPLATE_DIRS
    assert cfg["no_default_excludes"] is False


def test_templates_dir_string_becomes_list():
    cfg = normalize_config({"templates_dir": "myapp/templates"})
    assert cfg["templates_dir"] == ["myapp/templates"]


def test_templates_dir_list_preserved():
    dirs = ["a/templates", "b/templates"]
    cfg = normalize_config({"templates_dir": dirs})
    assert cfg["templates_dir"] == dirs


def test_templates_dir_invalid_type_raises():
    with pytest.raises(ConfigurationError):
        normalize_config({"templates_dir": 42})


def test_exclude_dirs_string_becomes_list():
    cfg = normalize_config({"exclude_dirs": "vendor"})
    assert cfg["exclude_dirs"] == ["vendor"]


def test_exclude_dirs_invalid_type_raises():
    with pytest.raises(ConfigurationError):
        normalize_config({"exclude_dirs": 123})


def test_target_dir_invalid_type_raises():
    with pytest.raises(ConfigurationError):
        normalize_config({"target_dir": ["not", "a", "string"]})


def test_no_default_excludes_coerced_to_bool():
    assert normalize_config({"no_default_excludes": 1})["no_default_excludes"] is True
    assert normalize_config({"no_default_excludes": 0})["no_default_excludes"] is False


def test_ruff_fix_coerced_to_bool():
    assert normalize_config({"ruff_fix": "yes"})["ruff_fix"] is True
    assert normalize_config({"ruff_fix": ""})["ruff_fix"] is False
