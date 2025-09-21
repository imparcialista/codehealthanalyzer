"""Módulo de internacionalização para CodeHealthAnalyzer.

Este módulo fornece suporte para múltiplos idiomas na aplicação.
"""

import gettext
import os
from pathlib import Path

# Idiomas suportados
SUPPORTED_LANGUAGES = {"pt_BR": "Português (Brasil)", "en": "English"}

# Idioma padrão
DEFAULT_LANGUAGE = "pt_BR"

# Variável global para o objeto de tradução atual
_current_translation = None
_current_language = DEFAULT_LANGUAGE


def get_locale_dir() -> Path:
    """Retorna o diretório de localização.

    Returns:
        Path: Caminho para o diretório locale
    """
    # Diretório locale na raiz do projeto
    current_dir = Path(__file__).parent.parent
    locale_dir = current_dir / "locale"

    # Se não encontrar, tentar no diretório de instalação
    if not locale_dir.exists():
        import codehealthanalyzer

        package_dir = Path(codehealthanalyzer.__file__).parent.parent
        locale_dir = package_dir / "locale"

    return locale_dir


def set_language(language: str) -> bool:
    """Define o idioma da aplicação.

    Args:
        language (str): Código do idioma (ex: 'pt_BR', 'en')

    Returns:
        bool: True se o idioma foi definido com sucesso
    """
    global _current_translation, _current_language

    if language not in SUPPORTED_LANGUAGES:
        return False

    try:
        locale_dir = get_locale_dir()
        translation = gettext.translation(
            "codehealthanalyzer",
            localedir=str(locale_dir),
            languages=[language],
            fallback=True,
        )

        _current_translation = translation
        _current_language = language
        return True

    except Exception:
        # Em caso de erro, usar tradução padrão
        _current_translation = gettext.NullTranslations()
        return False


def get_current_language() -> str:
    """Retorna o idioma atual.

    Returns:
        str: Código do idioma atual
    """
    return _current_language


def get_supported_languages() -> dict:
    """Retorna os idiomas suportados.

    Returns:
        dict: Dicionário com códigos e nomes dos idiomas
    """
    return SUPPORTED_LANGUAGES.copy()


def _(message: str) -> str:
    """Traduz uma mensagem para o idioma atual.

    Args:
        message (str): Mensagem a ser traduzida

    Returns:
        str: Mensagem traduzida
    """
    global _current_translation

    if _current_translation is None:
        # Inicializar com idioma padrão se não foi configurado
        set_language(DEFAULT_LANGUAGE)

    return _current_translation.gettext(message)


def ngettext(singular: str, plural: str, n: int) -> str:
    """Traduz uma mensagem com suporte a plural.

    Args:
        singular (str): Forma singular da mensagem
        plural (str): Forma plural da mensagem
        n (int): Número para determinar singular/plural

    Returns:
        str: Mensagem traduzida
    """
    global _current_translation

    if _current_translation is None:
        set_language(DEFAULT_LANGUAGE)

    return _current_translation.ngettext(singular, plural, n)


def detect_system_language() -> str:
    """Detecta o idioma do sistema.

    Returns:
        str: Código do idioma detectado ou padrão
    """
    import locale

    try:
        # Tentar detectar o idioma do sistema
        system_locale = locale.getdefaultlocale()[0]

        if system_locale:
            # Mapear locales comuns
            if system_locale.startswith("pt_BR") or system_locale.startswith("pt"):
                return "pt_BR"
            elif system_locale.startswith("en"):
                return "en"

    except Exception:
        pass

    # Verificar variáveis de ambiente
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


# Inicializar com idioma padrão
set_language(DEFAULT_LANGUAGE)
