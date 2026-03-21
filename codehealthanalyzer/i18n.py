"""Módulo de internacionalização para CodeHealthAnalyzer.

Este módulo fornece suporte para múltiplos idiomas na aplicação.
O estado de tradução é encapsulado em threading.local() para thread-safety.
"""

import gettext
import logging
import os
import threading
from pathlib import Path

# Idiomas suportados
SUPPORTED_LANGUAGES = {"pt_BR": "Português (Brasil)", "en": "English"}

# Idioma padrão
DEFAULT_LANGUAGE = "pt_BR"

# Estado encapsulado por thread — elimina variáveis globais mutáveis
_state = threading.local()


def _get_translation() -> gettext.NullTranslations:
    """Retorna o objeto de tradução da thread atual, inicializando se necessário."""
    if not hasattr(_state, "translation") or _state.translation is None:
        _state.language = DEFAULT_LANGUAGE
        _state.translation = _load_translation(DEFAULT_LANGUAGE)
    return _state.translation


def _load_translation(language: str) -> gettext.NullTranslations:
    """Carrega o objeto de tradução para o idioma dado, com fallback silencioso."""
    try:
        locale_dir = get_locale_dir()
        return gettext.translation(
            "codehealthanalyzer",
            localedir=str(locale_dir),
            languages=[language],
            fallback=True,
        )
    except Exception:
        return gettext.NullTranslations()


def get_locale_dir() -> Path:
    """Retorna o diretório de localização.

    Returns:
        Path: Caminho para o diretório locale
    """
    current_dir = Path(__file__).parent.parent
    locale_dir = current_dir / "locale"

    if not locale_dir.exists():
        import codehealthanalyzer

        package_dir = Path(codehealthanalyzer.__file__).parent.parent
        locale_dir = package_dir / "locale"

    return locale_dir


def set_language(language: str) -> bool:
    """Define o idioma da thread atual.

    Args:
        language (str): Código do idioma (ex: 'pt_BR', 'en')

    Returns:
        bool: True se o idioma foi definido com sucesso
    """
    if language not in SUPPORTED_LANGUAGES:
        return False

    try:
        translation = gettext.translation(
            "codehealthanalyzer",
            localedir=str(get_locale_dir()),
            languages=[language],
            fallback=True,
        )
        _state.translation = translation
        _state.language = language
        return True
    except Exception:
        _state.translation = gettext.NullTranslations()
        _state.language = language
        return False


def get_current_language() -> str:
    """Retorna o idioma atual da thread.

    Returns:
        str: Código do idioma atual
    """
    if not hasattr(_state, "language"):
        _get_translation()  # inicializa
    return _state.language


def get_supported_languages() -> dict:
    """Retorna os idiomas suportados.

    Returns:
        dict: Dicionário com códigos e nomes dos idiomas
    """
    return SUPPORTED_LANGUAGES.copy()


def _(message: str) -> str:
    """Traduz uma mensagem para o idioma da thread atual.

    Args:
        message (str): Mensagem a ser traduzida

    Returns:
        str: Mensagem traduzida
    """
    return _get_translation().gettext(message)


def ngettext(singular: str, plural: str, n: int) -> str:
    """Traduz uma mensagem com suporte a plural.

    Args:
        singular (str): Forma singular da mensagem
        plural (str): Forma plural da mensagem
        n (int): Número para determinar singular/plural

    Returns:
        str: Mensagem traduzida
    """
    return _get_translation().ngettext(singular, plural, n)


def detect_system_language() -> str:
    """Detecta o idioma do sistema.

    Returns:
        str: Código do idioma detectado ou padrão
    """
    import locale

    try:
        system_locale = locale.getdefaultlocale()[0]
        if system_locale:
            if system_locale.startswith("pt_BR") or system_locale.startswith("pt"):
                return "pt_BR"
            elif system_locale.startswith("en"):
                return "en"
    except Exception as e:
        logging.exception(f"Error loading translation: {e}")

    env_lang = os.environ.get("LANG", "")
    if "pt" in env_lang.lower():
        return "pt_BR"
    elif "en" in env_lang.lower():
        return "en"

    return DEFAULT_LANGUAGE


def auto_configure_language() -> str:
    """Configura automaticamente o idioma baseado no sistema.

    Returns:
        str: Idioma configurado
    """
    detected_lang = detect_system_language()
    set_language(detected_lang)
    return detected_lang
