"""Testes para utils/helpers.py."""

import json

from codehealthanalyzer.utils.helpers import (
    ColorHelper,
    DataHelper,
    FileHelper,
    TimeHelper,
)

# ---------------------------------------------------------------------------
# FileHelper
# ---------------------------------------------------------------------------


def test_write_json_creates_file(tmp_path):
    out = tmp_path / "out.json"
    assert FileHelper.write_json({"key": "value"}, str(out)) is True
    assert out.exists()


def test_write_json_content_is_valid(tmp_path):
    out = tmp_path / "out.json"
    data = {"a": 1, "b": [1, 2, 3]}
    FileHelper.write_json(data, str(out))
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded == data


def test_write_json_creates_parent_dirs(tmp_path):
    out = tmp_path / "deep" / "nested" / "out.json"
    assert FileHelper.write_json({}, str(out)) is True
    assert out.exists()


def test_write_json_returns_false_on_error(tmp_path):
    # Passar objeto não serializável
    result = FileHelper.write_json({"k": object()}, str(tmp_path / "x.json"))
    assert result is False


def test_read_json_returns_dict(tmp_path):
    f = tmp_path / "data.json"
    f.write_text('{"x": 42}', encoding="utf-8")
    result = FileHelper.read_json(str(f))
    assert result == {"x": 42}


def test_read_json_returns_none_on_missing_file(tmp_path):
    result = FileHelper.read_json(str(tmp_path / "missing.json"))
    assert result is None


def test_read_json_returns_none_on_invalid_json(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text("not json", encoding="utf-8")
    result = FileHelper.read_json(str(f))
    assert result is None


def test_read_text_returns_content(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("hello world", encoding="utf-8")
    assert FileHelper.read_text(str(f)) == "hello world"


def test_read_text_returns_none_on_missing(tmp_path):
    assert FileHelper.read_text(str(tmp_path / "missing.txt")) is None


def test_write_text_creates_file(tmp_path):
    out = tmp_path / "out.txt"
    assert FileHelper.write_text("content", str(out)) is True
    assert out.read_text(encoding="utf-8") == "content"


def test_get_file_size_returns_bytes(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("abc", encoding="utf-8")
    assert FileHelper.get_file_size(str(f)) == 3


def test_get_file_size_returns_zero_on_missing(tmp_path):
    assert FileHelper.get_file_size(str(tmp_path / "missing.txt")) == 0


def test_get_file_lines_counts_lines(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("a\nb\nc\n", encoding="utf-8")
    assert FileHelper.get_file_lines(str(f)) == 3


def test_get_file_lines_returns_zero_on_missing(tmp_path):
    assert FileHelper.get_file_lines(str(tmp_path / "missing.txt")) == 0


def test_find_files_returns_matching(tmp_path):
    (tmp_path / "a.py").write_text("")
    (tmp_path / "b.py").write_text("")
    (tmp_path / "c.txt").write_text("")
    found = FileHelper.find_files(tmp_path, "*.py")
    names = {f.name for f in found}
    assert "a.py" in names and "b.py" in names and "c.txt" not in names


def test_find_files_returns_empty_on_bad_dir():
    assert FileHelper.find_files("/nonexistent/path") == []


# ---------------------------------------------------------------------------
# DataHelper
# ---------------------------------------------------------------------------


def test_format_bytes_bytes():
    assert FileHelper  # import sanity
    assert DataHelper.format_bytes(512) == "512.0 B"


def test_format_bytes_kilobytes():
    assert "KB" in DataHelper.format_bytes(2048)


def test_format_bytes_megabytes():
    assert "MB" in DataHelper.format_bytes(2 * 1024 * 1024)


def test_calculate_percentage_normal():
    assert DataHelper.calculate_percentage(1, 4) == 25.0


def test_calculate_percentage_zero_total():
    assert DataHelper.calculate_percentage(5, 0) == 0.0


def test_merge_dicts_shallow():
    result = DataHelper.merge_dicts({"a": 1}, {"b": 2})
    assert result == {"a": 1, "b": 2}


def test_merge_dicts_deep():
    d1 = {"a": {"x": 1}}
    d2 = {"a": {"y": 2}}
    result = DataHelper.merge_dicts(d1, d2)
    assert result["a"] == {"x": 1, "y": 2}


def test_flatten_list():
    assert DataHelper.flatten_list([1, [2, [3]]]) == [1, 2, 3]


def test_group_by():
    items = [{"type": "a"}, {"type": "b"}, {"type": "a"}]
    grouped = DataHelper.group_by(items, "type")
    assert len(grouped["a"]) == 2
    assert len(grouped["b"]) == 1


def test_sort_by_key():
    items = [{"n": 3}, {"n": 1}, {"n": 2}]
    sorted_items = DataHelper.sort_by_key(items, "n")
    assert [i["n"] for i in sorted_items] == [1, 2, 3]


def test_sort_by_key_reverse():
    items = [{"n": 1}, {"n": 3}, {"n": 2}]
    sorted_items = DataHelper.sort_by_key(items, "n", reverse=True)
    assert sorted_items[0]["n"] == 3


# ---------------------------------------------------------------------------
# TimeHelper
# ---------------------------------------------------------------------------


def test_now_iso_is_string():
    ts = TimeHelper.now_iso()
    assert isinstance(ts, str)
    assert "T" in ts


def test_format_duration_milliseconds():
    assert "ms" in TimeHelper.format_duration(0.5)


def test_format_duration_seconds():
    assert "s" in TimeHelper.format_duration(5.0)


def test_format_duration_minutes():
    assert "min" in TimeHelper.format_duration(120)


def test_format_duration_hours():
    assert "h" in TimeHelper.format_duration(7200)


def test_parse_iso_date_valid():
    dt = TimeHelper.parse_iso_date("2024-01-01T00:00:00")
    assert dt is not None
    assert dt.year == 2024


def test_parse_iso_date_invalid():
    assert TimeHelper.parse_iso_date("not-a-date") is None


# ---------------------------------------------------------------------------
# ColorHelper
# ---------------------------------------------------------------------------


def test_colorize_adds_ansi(capsys):
    result = ColorHelper.colorize("test", "red")
    assert "test" in result
    assert "\033[" in result


def test_colorize_unknown_color_returns_plain():
    result = ColorHelper.colorize("test", "neon_purple")
    assert result == "test"


def test_success_contains_ok():
    assert "[OK]" in ColorHelper.success("done")


def test_warning_contains_warn():
    assert "[WARN]" in ColorHelper.warning("careful")


def test_error_contains_error():
    assert "[ERROR]" in ColorHelper.error("boom")


def test_info_contains_info():
    assert "[INFO]" in ColorHelper.info("note")
