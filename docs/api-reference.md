# API Reference

All public symbols are importable directly from `qtshadcn`:

```python
from qtshadcn import (
    apply_theme,
    get_theme,
    ShadcnTheme,
    ShadcnThemeTokens,
    ThemeParseError,
)
```

Qt classes should be imported directly from qtpy so your application uses the
same binding QtShadcn is using:

```python
from qtpy import QtWidgets

app = QtWidgets.QApplication([])
```

Supported bindings: **PySide6**, **PyQt6**, **PySide2**, **PyQt5**. Set
`QT_API` (for example, `QT_API=pyside6`) to choose a binding when multiple are
installed.

---

## Functions

### `apply_theme`

```python
def apply_theme(
    app: QApplication | None = None,
    theme_file: str | None = None,
    *,
    theme_mode: str = "auto",
    custom_tokens: dict[str, dict[str, str] | str] | None = None,
    additional_qss: str | None = None,
    default_theme: str = "dark",
) -> ShadcnThemeTokens
```

Applies a QtShadcn XML theme to the running `QApplication`.

**Pipeline:**

1. Resolves the theme source path from `theme_file` (or the packaged default theme)
2. Detects light/dark mode based on `theme_mode`
3. Checks disk cache — skips re-parsing if inputs and source file are unchanged
4. Parses the XML, applies `custom_tokens`, resolves all color tokens, renders QSS via Jinja2
5. Appends `additional_qss` and calls `app.setStyleSheet(qss)`
6. Returns the active `ShadcnThemeTokens`

**Parameters:**

| Name | Type | Description |
| --- | --- | --- |
| `app` | `QApplication \| None` | The running Qt application. If `None`, `QApplication.instance()` is used. |
| `theme_file` | `str \| None` | Path to the `.xml` theme file. `None` loads the built-in default theme. |
| `theme_mode` | `str` | `"auto"`, `"light"`, or `"dark"`. Default: `"auto"`. |
| `custom_tokens` | `dict[str, dict[str, str] \| str] \| None` | Token overrides. Mode-specific when top-level keys are `"light"` and/or `"dark"`. |
| `additional_qss` | `str \| None` | Inline Jinja snippet, `.qss` file path, or `.jinja` file path to append. |
| `default_theme` | `str` | Fallback mode when `theme_mode="auto"` and OS detection fails. `"light"` or `"dark"`. |

**Returns:** `ShadcnThemeTokens` — the resolved palette for the active mode.

**Raises:** `ThemeParseError` — if the file is missing, malformed, or has missing tokens. `QtShadcnError` — if no `QApplication` instance is available or an argument is invalid.

---

### `get_theme`

```python
def get_theme() -> ShadcnTheme | None
```

Returns the full resolved theme (both light and dark palettes) from disk cache.

Returns `None` if `apply_theme` has never been called or the cache is absent.

---

## Styled Qt Widgets

QtShadcn renders shadcn-style QSS for common Qt widgets. Widget variants are selected with dynamic Qt properties.

### `QPushButton` vs `QToolButton`

Use `QPushButton` for regular command buttons with text labels, form actions, dialog actions, and primary calls to action.

Use `QToolButton` for compact action primitives: icon buttons, toolbar-style controls, menu triggers, and toggle buttons. It shares the same visual variant names as `QPushButton`, but it is sized as an icon-oriented control and is not intended to replace text-first buttons.

Supported `QToolButton` dynamic properties:

| Property | Values | Description |
| --- | --- | --- |
| `variant` | `default`, `outline`, `secondary`, `ghost`, `destructive` | Visual intent. |
| `size` | `icon-sm`, `icon`, `icon-lg` | Icon-oriented control size. |

---

## Supported Widgets

QtShadcn v0.0.16 ships QSS for these widgets:

- `QWidget` — base background, foreground, and typography classes
- `QPushButton` — variants, sizes, and disabled states
- `QToolButton` — compact icon/action variants
- `QLineEdit` — input states including focus, disabled, and invalid
- `QTextEdit` — textarea states including focus, disabled, and invalid
- `QCheckBox` — toggle controls with themed check icons and disabled states

See the [Roadmap](roadmap.md) for planned widget coverage.

---

## Theme Mode

`theme_mode` accepts the following string values:

| Value | Behavior |
| --- | --- |
| `"auto"` | Detects OS light/dark preference via `darkdetect` (default) |
| `"light"` | Always uses the `<light>` palette |
| `"dark"` | Always uses the `<dark>` palette |

When `theme_mode="auto"` and the OS preference cannot be detected, `default_theme` is used.

---

## Models

### `ShadcnThemeTokens`

Immutable Pydantic model holding the resolved tokens for a single palette (light **or** dark). Returned by `apply_theme`.

All fields are `str` and required. Unknown XML tokens are ignored (`extra="ignore"`).

The example values below come from the packaged `default.xml` light palette. They are not model fallbacks for missing custom theme tokens.

| Field | `default.xml` light value |
| --- | --- |
| `background` | `#ffffff` |
| `foreground` | `#020617` |
| `card` | `#ffffff` |
| `card_foreground` | `#020617` |
| `popover` | `#ffffff` |
| `popover_foreground` | `#020617` |
| `primary` | `#0f172a` |
| `primary_foreground` | `#f8fafc` |
| `secondary` | `#f1f5f9` |
| `secondary_foreground` | `#0f172a` |
| `accent` | `#f1f5f9` |
| `accent_foreground` | `#0f172a` |
| `muted` | `#f1f5f9` |
| `muted_foreground` | `#64748b` |
| `destructive` | `#ef4444` |
| `destructive_foreground` | `#f8fafc` |
| `border` | `#e2e8f0` |
| `input` | `#e2e8f0` |
| `ring` | `#0f172a` |
| `radius` | `8px` |
| `font_family` | `system-ui, sans-serif` |
| `spacing` | `4px` |

---

### `ShadcnTheme`

Immutable Pydantic model holding both palettes. Returned by `get_theme`.

| Field | Type |
| --- | --- |
| `light` | `ShadcnThemeTokens` |
| `dark` | `ShadcnThemeTokens` |

---

## Exceptions

### `ThemeParseError`

```python
class ThemeParseError(ValueError): ...
```

Raised by `apply_theme` and `parse_theme_source` when the theme file cannot be loaded or is invalid.

Common causes:

- File not found
- File is not an XML document (JSON, CSS, and URLs are rejected explicitly)
- Missing a required token in `<light>` or `<dark>`
- Token value is empty

```python
from qtshadcn import apply_theme, ThemeParseError

try:
    apply_theme(app, theme_file="my_theme.xml", theme_mode="auto")
except ThemeParseError as e:
    print(f"Theme error: {e}")
```
