"""QtShadcn QSS stylesheet renderer."""

import logging
from pathlib import Path

import jinja2

from ..exceptions import ThemeRenderError
from ..models import ShadcnThemeTokens
from ..tokens import colors, radius, scale, typography
from .helpers import _add_fonts
from .icon import ThemedIconManager

logger = logging.getLogger(__name__)

TEMPLATE_FILE = str(Path(__file__).resolve().parents[1] / "styles" / "shadcn.jinja")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _render_template(source: str, context: dict) -> str:
    """Render a Jinja template from a file path or inline string."""
    try:
        source_path = Path(source)
        if source_path.exists():
            env = jinja2.Environment(
                autoescape=False,
                loader=jinja2.FileSystemLoader(str(source_path.parent)),
            )
            tpl = env.get_template(source_path.name)
        else:
            env = jinja2.Environment(autoescape=False, loader=jinja2.BaseLoader())
            tpl = env.from_string(source)

        return tpl.render(**context)
    except jinja2.TemplateSyntaxError as e:
        raise ThemeRenderError(f"Failed to render template syntax: {e}") from e
    except jinja2.TemplateError as e:
        raise ThemeRenderError(f"Failed to render template: {e}") from e


def _render_custom_snippet(custom: str, context: dict) -> str:
    """Render an inline custom QSS Jinja snippet."""
    return _render_template(custom, context)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def _build_theme(
    tokens: ShadcnThemeTokens,
    template: str = TEMPLATE_FILE,
    *,
    is_dark: bool = False,
    additional_qss: str | None = None,
) -> str:
    """Render the base QSS stylesheet from resolved tokens.

    ``additional_qss`` is an inline Jinja/QSS string appended to the base
    stylesheet.
    """
    try:
        _add_fonts()
    except Exception as e:
        logger.warning("Error loading fonts: %s", e)

    render_context = {
        "tokens": tokens,
        "Colors": colors,
        "Icons": ThemedIconManager(),
        "Radius": radius,
        "Scale": scale,
        "Typography": typography,
        "is_dark": is_dark,
    }

    try:
        stylesheet = _render_template(template, render_context)
    except ThemeRenderError as e:
        raise ThemeRenderError(f"Failed to render QSS theme template: {e}") from e

    if additional_qss:
        stylesheet += "\n" + _render_custom_snippet(additional_qss, render_context)

    return stylesheet
