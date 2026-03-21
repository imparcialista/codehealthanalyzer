"""Testes para utils/validators.py."""


from codehealthanalyzer.utils.validators import (
    ConfigValidator,
    DataValidator,
    PathValidator,
)

# ---------------------------------------------------------------------------
# PathValidator
# ---------------------------------------------------------------------------


def test_is_valid_directory_true(tmp_path):
    assert PathValidator.is_valid_directory(str(tmp_path)) is True


def test_is_valid_directory_false_on_file(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("")
    assert PathValidator.is_valid_directory(str(f)) is False


def test_is_valid_directory_false_on_missing():
    assert PathValidator.is_valid_directory("/nonexistent/path/xyz") is False


def test_is_valid_file_true(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("content")
    assert PathValidator.is_valid_file(str(f)) is True


def test_is_valid_file_false_on_dir(tmp_path):
    assert PathValidator.is_valid_file(str(tmp_path)) is False


def test_is_python_project_with_setup_py(tmp_path):
    (tmp_path / "setup.py").write_text("")
    assert PathValidator.is_python_project(str(tmp_path)) is True


def test_is_python_project_with_py_files(tmp_path):
    (tmp_path / "module.py").write_text("x = 1")
    assert PathValidator.is_python_project(str(tmp_path)) is True


def test_is_python_project_with_pyproject_toml(tmp_path):
    (tmp_path / "pyproject.toml").write_text("")
    assert PathValidator.is_python_project(str(tmp_path)) is True


def test_is_python_project_false_on_empty_dir(tmp_path):
    assert PathValidator.is_python_project(str(tmp_path)) is False


def test_has_templates_true(tmp_path):
    (tmp_path / "index.html").write_text("<html></html>")
    assert PathValidator.has_templates(str(tmp_path)) is True


def test_has_templates_false(tmp_path):
    assert PathValidator.has_templates(str(tmp_path)) is False


def test_get_project_info_valid(tmp_path):
    (tmp_path / "module.py").write_text("x = 1")
    info = PathValidator.get_project_info(str(tmp_path))
    assert info["valid"] is True
    assert info["python_files"] >= 1
    assert "name" in info
    assert "path" in info


def test_get_project_info_invalid():
    info = PathValidator.get_project_info("/nonexistent/path/xyz")
    assert info["valid"] is False
    assert "error" in info


def test_get_project_info_counts_html(tmp_path):
    (tmp_path / "index.html").write_text("<html></html>")
    info = PathValidator.get_project_info(str(tmp_path))
    assert info["html_files"] >= 1
    assert info["has_templates"] is True


def test_should_skip_path_venv(tmp_path):
    venv_path = tmp_path / ".venv" / "lib" / "file.py"
    assert PathValidator.should_skip_path(venv_path) is True


def test_should_skip_path_normal(tmp_path):
    normal = tmp_path / "src" / "module.py"
    assert PathValidator.should_skip_path(normal) is False


# ---------------------------------------------------------------------------
# ConfigValidator
# ---------------------------------------------------------------------------

VALID_LIMITS = {
    "python_function": {"yellow": 30, "red": 50},
    "python_class": {"yellow": 300, "red": 500},
    "python_module": {"yellow": 500, "red": 1000},
    "html_template": {"yellow": 150, "red": 200},
    "test_file": {"yellow": 400, "red": 600},
}


def test_validate_limits_valid():
    result = ConfigValidator.validate_limits(VALID_LIMITS)
    assert result["valid"] is True
    assert result["errors"] == []


def test_validate_limits_missing_key():
    limits = {k: v for k, v in VALID_LIMITS.items() if k != "python_function"}
    result = ConfigValidator.validate_limits(limits)
    assert result["valid"] is False
    assert any("python_function" in e for e in result["errors"])


def test_validate_limits_yellow_gte_red():
    bad = dict(VALID_LIMITS)
    bad["python_function"] = {"yellow": 50, "red": 30}
    result = ConfigValidator.validate_limits(bad)
    assert len(result["warnings"]) > 0


def test_validate_limits_non_int_values():
    bad = dict(VALID_LIMITS)
    bad["python_function"] = {"yellow": "thirty", "red": 50}
    result = ConfigValidator.validate_limits(bad)
    assert result["valid"] is False


def test_validate_config_empty():
    result = ConfigValidator.validate_config({})
    assert result["valid"] is True


def test_validate_config_with_valid_limits():
    result = ConfigValidator.validate_config({"limits": VALID_LIMITS})
    assert result["valid"] is True


def test_validate_config_invalid_target_dir():
    result = ConfigValidator.validate_config({"target_dir": 123})
    assert result["valid"] is False


# ---------------------------------------------------------------------------
# DataValidator
# ---------------------------------------------------------------------------


def test_validate_report_data_violations_valid():
    data = {
        "metadata": {"generated_at": "2024-01-01"},
        "violations": [],
        "statistics": {},
    }
    result = DataValidator.validate_report_data(data, "violations")
    assert result["valid"] is True


def test_validate_report_data_missing_metadata():
    result = DataValidator.validate_report_data({"violations": []}, "violations")
    assert result["valid"] is False
    assert any("metadata" in e for e in result["errors"])


def test_validate_report_data_templates_missing_templates():
    data = {"metadata": {"generated_at": ""}}
    result = DataValidator.validate_report_data(data, "templates")
    assert result["valid"] is False


def test_validate_report_data_errors_missing_errors():
    data = {"metadata": {"generated_at": ""}}
    result = DataValidator.validate_report_data(data, "errors")
    assert result["valid"] is False


def test_sanitize_file_path_normalizes_backslashes():
    result = DataValidator.sanitize_file_path("foo\\bar\\file.py")
    assert "\\" not in result
    assert "foo/bar/file.py" == result


def test_sanitize_file_path_removes_leading_slash():
    result = DataValidator.sanitize_file_path("/absolute/path.py")
    assert not result.startswith("/")
