"""Testes para codehealthanalyzer.exceptions."""

import pytest

from codehealthanalyzer.exceptions import (
    AnalyzerExecutionError,
    CodeHealthAnalyzerError,
    ConfigurationError,
)


def test_base_exception_is_exception():
    assert issubclass(CodeHealthAnalyzerError, Exception)


def test_configuration_error_inherits_base():
    assert issubclass(ConfigurationError, CodeHealthAnalyzerError)


def test_analyzer_execution_error_inherits_base():
    assert issubclass(AnalyzerExecutionError, CodeHealthAnalyzerError)


def test_can_catch_subclasses_as_base():
    with pytest.raises(CodeHealthAnalyzerError):
        raise ConfigurationError("bad config")

    with pytest.raises(CodeHealthAnalyzerError):
        raise AnalyzerExecutionError("ruff failed")


def test_message_preserved():
    exc = ConfigurationError("templates_dir inválido")
    assert "templates_dir inválido" in str(exc)
