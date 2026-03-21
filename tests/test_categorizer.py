"""Testes para utils/categorizer.py."""

from pathlib import Path

import pytest

from codehealthanalyzer.utils.categorizer import Categorizer


@pytest.fixture
def cat():
    return Categorizer()


# ---------------------------------------------------------------------------
# categorize_file
# ---------------------------------------------------------------------------


def test_categorize_file_critical(cat):
    result = cat.categorize_file(Path("stock_updater_mlb.py"))
    assert result == "Arquivo Crítico"


def test_categorize_file_admin(cat):
    result = cat.categorize_file(Path("views/admin/panel.py"))
    assert result == "Views Admin"


def test_categorize_file_blueprint_integration(cat):
    result = cat.categorize_file(Path("blueprints/integrations/connector.py"))
    assert result == "Blueprint Crítico"


def test_categorize_file_blueprint_payment(cat):
    result = cat.categorize_file(Path("blueprints/payments/gateway.py"))
    assert result == "Blueprint Pagamentos"


def test_categorize_file_blueprint_generic(cat):
    result = cat.categorize_file(Path("blueprints/users/views.py"))
    assert result == "Blueprint"


def test_categorize_file_template_base(cat):
    result = cat.categorize_file(Path("templates/base.html"))
    assert result == "Template Base"


def test_categorize_file_template_admin(cat):
    # "admin" bate antes de "template" na lógica de categorize_file
    result = cat.categorize_file(Path("templates/admin/dashboard.html"))
    assert result == "Views Admin"


def test_categorize_file_template_generic(cat):
    result = cat.categorize_file(Path("templates/index.html"))
    assert result == "Template"


def test_categorize_file_default(cat):
    result = cat.categorize_file(Path("src/utils.py"))
    assert result == "Arquivo Padrão"


# ---------------------------------------------------------------------------
# categorize_template
# ---------------------------------------------------------------------------


def test_categorize_template_critical(cat):
    assert (
        cat.categorize_template(Path("manage_product_links.html")) == "Template Crítico"
    )


def test_categorize_template_base(cat):
    assert cat.categorize_template(Path("base.html")) == "Template Base"


def test_categorize_template_admin(cat):
    assert cat.categorize_template(Path("admin/settings.html")) == "Template Admin"


def test_categorize_template_interactive(cat):
    assert (
        cat.categorize_template(Path("clone_anuncios_progress.html"))
        == "Template Interativo"
    )


def test_categorize_template_products(cat):
    assert (
        cat.categorize_template(Path("bling_products_list.html"))
        == "Template de Produtos"
    )


def test_categorize_template_ml(cat):
    assert cat.categorize_template(Path("mercado_livre/listings.html")) == "Template ML"


def test_categorize_template_integration(cat):
    assert (
        cat.categorize_template(Path("integrations/webhooks.html"))
        == "Template de Integração"
    )


def test_categorize_template_generic(cat):
    assert cat.categorize_template(Path("contact.html")) == "Template"


# ---------------------------------------------------------------------------
# categorize_error
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "code,expected",
    [
        ("F401", "Erros de Importação"),
        ("F811", "Erros de Importação"),
        ("F821", "Erros de Importação"),
        ("F841", "Erros de Sintaxe"),
        ("E302", "Erros de Estilo"),
        ("W291", "Avisos"),
        ("C901", "Complexidade"),
        ("N802", "Nomenclatura"),
        ("XYZ99", "Outros"),
    ],
)
def test_categorize_error(cat, code, expected):
    assert cat.categorize_error(code) == expected


# ---------------------------------------------------------------------------
# determine_priority
# ---------------------------------------------------------------------------


def test_determine_priority_python_high(cat):
    assert cat.determine_priority("file", {"lines": 1001, "type": "python"}) == "high"


def test_determine_priority_python_medium(cat):
    assert cat.determine_priority("file", {"lines": 600, "type": "python"}) == "medium"


def test_determine_priority_python_low(cat):
    assert cat.determine_priority("file", {"lines": 100, "type": "python"}) == "low"


def test_determine_priority_html_high(cat):
    assert (
        cat.determine_priority("file", {"lines": 201, "type": "html template"})
        == "high"
    )


def test_determine_priority_html_medium(cat):
    assert (
        cat.determine_priority("file", {"lines": 160, "type": "html template"})
        == "medium"
    )


def test_determine_priority_template_high(cat):
    assert cat.determine_priority("template", {"css": 15000, "js": 10000}) == "high"


def test_determine_priority_template_medium(cat):
    assert cat.determine_priority("template", {"css": 8000, "js": 5000}) == "medium"


def test_determine_priority_template_low(cat):
    assert cat.determine_priority("template", {"css": 100, "js": 100}) == "low"


def test_determine_priority_error_high(cat):
    assert cat.determine_priority("error", {"code": "F821"}) == "high"


def test_determine_priority_error_medium(cat):
    assert cat.determine_priority("error", {"code": "F401"}) == "medium"


def test_determine_priority_error_low(cat):
    assert cat.determine_priority("error", {"code": "W291"}) == "low"


# ---------------------------------------------------------------------------
# sort_by_priority
# ---------------------------------------------------------------------------


def test_sort_by_priority_orders_correctly(cat):
    items = [
        {"name": "a", "priority": "low"},
        {"name": "b", "priority": "high"},
        {"name": "c", "priority": "medium"},
    ]
    result = cat.sort_by_priority(items)
    assert result[0]["priority"] == "high"
    assert result[1]["priority"] == "medium"
    assert result[2]["priority"] == "low"


# ---------------------------------------------------------------------------
# get_category_icon / get_priority_color
# ---------------------------------------------------------------------------


def test_get_category_icon_known(cat):
    assert cat.get_category_icon("Arquivo Crítico") == "🔥"


def test_get_category_icon_unknown(cat):
    assert cat.get_category_icon("Unknown Category") == "📁"


def test_get_priority_color_high(cat):
    assert cat.get_priority_color("high") == "#e74c3c"


def test_get_priority_color_unknown(cat):
    assert cat.get_priority_color("none") == "#95a5a6"


# ---------------------------------------------------------------------------
# Config customizado
# ---------------------------------------------------------------------------


def test_custom_config_overrides_rules():
    cat = Categorizer(
        config={
            "file_rules": {
                "critical_files": ["my_critical.py"],
                "admin_patterns": [],
                "blueprint_patterns": [],
                "template_patterns": [],
                "integration_patterns": [],
                "payment_patterns": [],
            }
        }
    )
    assert cat.categorize_file(Path("my_critical.py")) == "Arquivo Crítico"
    assert cat.categorize_file(Path("other.py")) == "Arquivo Padrão"
