import pytest

from apis_externas_4.challenges.legislative_activity.application.ranking import resolve_theme
from apis_externas_4.challenges.legislative_activity.domain.models import Theme


def test_resolve_theme_ignores_case_and_accents():
    theme = resolve_theme([Theme(1, "Saúde")], "saude")
    assert theme.code == 1


def test_resolve_theme_rejects_ambiguous_query():
    themes = [Theme(1, "Saúde Pública"), Theme(2, "Saúde Animal")]
    with pytest.raises(ValueError, match="ambíguo"):
        resolve_theme(themes, "saude")


def test_resolve_theme_accepts_code():
    assert resolve_theme([Theme(4, "Educação")], "4").name == "Educação"
