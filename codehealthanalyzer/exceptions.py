"""Excecoes publicas do pacote."""


class CodeHealthAnalyzerError(Exception):
    """Erro base do pacote."""


class ConfigurationError(CodeHealthAnalyzerError):
    """Configuracao invalida fornecida pelo usuario."""


class AnalyzerExecutionError(CodeHealthAnalyzerError):
    """Falha na execucao de um analyzer ou dependencia externa."""
