from src.config.themes import THEME_CONFIG


def test_theme_config_has_three_days():
    assert len(THEME_CONFIG) == 3


def test_each_theme_has_required_fields():
    for theme in THEME_CONFIG:
        assert theme.day
        assert theme.theme_name
        assert theme.content_focus
