"""Tests for QtShadcn custom exception hierarchy."""

import pytest
from qtshadcn.common.renderer import _build_theme
from qtshadcn.exceptions import (
    QtBindingError,
    QtShadcnError,
    ThemeParseError,
    ThemeRenderError,
)
from qtshadcn.models import ShadcnThemeTokens


def test_exception_hierarchy():
    """Verify all custom exceptions inherit from QtShadcnError and standard built-ins."""
    assert issubclass(ThemeParseError, QtShadcnError)
    assert issubclass(ThemeParseError, ValueError)

    assert issubclass(ThemeRenderError, QtShadcnError)
    assert issubclass(ThemeRenderError, RuntimeError)

    assert issubclass(QtBindingError, QtShadcnError)
    assert issubclass(QtBindingError, ImportError)


def test_theme_render_error_raised():
    """Verify ThemeRenderError is raised on invalid Jinja template."""
    dummy_tokens = ShadcnThemeTokens(
        background="#ffffff",
        foreground="#000000",
        card="#ffffff",
        card_foreground="#000000",
        popover="#ffffff",
        popover_foreground="#000000",
        primary="#000000",
        primary_foreground="#ffffff",
        secondary="#f0f0f0",
        secondary_foreground="#000000",
        muted="#f0f0f0",
        muted_foreground="#888888",
        accent="#f0f0f0",
        accent_foreground="#000000",
        destructive="#ff0000",
        destructive_foreground="#ffffff",
        border="#cccccc",
        input="#cccccc",
        ring="#000000",
        spacing="4px",
        radius="0.5rem",
        font_family="Inter",
    )
    invalid_template = "{% if unclosed_tag %}"
    with pytest.raises(ThemeRenderError, match="Failed to render QSS theme template"):
        _build_theme(dummy_tokens, template=invalid_template)
