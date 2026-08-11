"""QtShadcn QSS stylesheet renderer."""

import logging
from pathlib import Path

import jinja2

from ..exceptions import ThemeRenderError
from ..models import ShadcnThemeTokens
from ..tokens import colors, radius, scale
from .helpers import _add_fonts
from .icon import ThemedIconManager

logger = logging.getLogger(__name__)

TEMPLATE_FILE = str(Path(__file__).resolve().parents[1] / "styles" / "shadcn.jinja")


def _build_theme(
    tokens: ShadcnThemeTokens,
    template: str = TEMPLATE_FILE,
    *,
    is_dark: bool = False,
    additional_qss: str | None = None,
) -> str:
    """Render the QSS stylesheet from resolved tokens.

    If ``additional_qss`` is provided it is treated as a Jinja template string
    and rendered with the same token context, then appended to the base
    stylesheet. It may also be a path to a ``.jinja`` or ``.qss`` file, in
    which case its content is loaded from disk before rendering.
    """
    try:
        _add_fonts()
    except Exception as e:
        logger.warning("Error loading fonts: %s", e)

    render_context = {
        "tokens": tokens,
        "colors": colors,
        "icons": ThemedIconManager(),
        "radius": radius,
        "scale": scale,
        "is_dark": is_dark,
    }

    try:
        template_path = Path(template)
        if template_path.exists():
            parent = str(template_path.parent)
            template_name = template_path.name
            loader = jinja2.FileSystemLoader(parent)
            env = jinja2.Environment(autoescape=False, loader=loader)
            base_tpl = env.get_template(template_name)
        else:
            env = jinja2.Environment(autoescape=False, loader=jinja2.BaseLoader())
            base_tpl = env.from_string(template)

        stylesheet = base_tpl.render(**render_context)
    except jinja2.TemplateError as e:
        raise ThemeRenderError(f"Failed to render QSS theme template: {e}") from e

    if additional_qss:
        stylesheet += "\n" + _render_custom_snippet(additional_qss, render_context)

    return stylesheet


def _render_custom_snippet(custom: str, context: dict) -> str:
    """Render a custom QSS Jinja snippet and return the resulting string.

    ``custom`` may be:

    * A path to a ``.jinja`` or ``.qss`` file — its content is loaded from
      disk and rendered as a Jinja template.
    * A raw Jinja template string — rendered directly.

    Raises :class:`~qtshadcn.exceptions.ThemeRenderError` on any Jinja error.
    """
    custom_path = Path(custom)
    if custom_path.suffix.lower() in {".jinja", ".qss"} and custom_path.exists():
        logger.debug("Loading custom theme snippet from file: %s", custom_path)
        try:
            loader = jinja2.FileSystemLoader(str(custom_path.parent))
            env = jinja2.Environment(autoescape=False, loader=loader)
            tpl = env.get_template(custom_path.name)
        except jinja2.TemplateError as e:
            raise ThemeRenderError(f"Failed to load custom theme file '{custom_path}': {e}") from e
    else:
        env = jinja2.Environment(autoescape=False, loader=jinja2.BaseLoader())
        try:
            tpl = env.from_string(custom)
        except jinja2.TemplateError as e:
            raise ThemeRenderError(f"Failed to parse custom theme snippet: {e}") from e

    try:
        return tpl.render(**context)
    except jinja2.TemplateError as e:
        raise ThemeRenderError(f"Failed to render custom theme snippet: {e}") from e
