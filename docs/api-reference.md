# API Reference

All public symbols are importable directly from `qtshadcn`:

```python
from qtshadcn import (
    qsettings,
    ThemeMode,
    setThemeMode,
    toggleThemeMode,
    themeMode,
    isDarkTheme,
    setTheme,
    getTheme,
    setStyleSheet,
    getStyleSheet,
    SystemThemeWatcher,
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

### `setThemeMode`

```python
def setThemeMode(mode: ThemeMode | str, *, save: bool = True) -> None
```

Set the active theme mode and re-render the stylesheet.

**Parameters:**

| Name | Type | Description |
| --- | --- | --- |
| `mode` | `ThemeMode \| str` | `ThemeMode.AUTO`, `ThemeMode.LIGHT`, `ThemeMode.DARK`, or `"auto"`, `"light"`, `"dark"`. |
| `save` | `bool` | When `True` (default), persist the mode to `config/theme_mode.json`. |

---

### `toggleThemeMode`

```python
def toggleThemeMode(*, save: bool = True) -> None
```

Cycle the theme mode: auto → light → dark → auto.

---

### `themeMode`

```python
def themeMode() -> ThemeMode
```

Return the active theme mode.

---

### `isDarkTheme`

```python
def isDarkTheme() -> bool
```

Return whether the resolved active palette is dark.

---

### `setTheme`

```python
def setTheme(
    source: str | Path,
    *,
    custom_tokens: dict[str, Any] | None = None,
    save: bool = True,
) -> None
```

Load a QtShadcn XML or JSON theme, apply optional token overrides, and re-render the stylesheet.

**Pipeline:**

1. Resolves the theme source path
2. Parses the XML/JSON, applies `custom_tokens`, resolves all color tokens
3. Persists the palette when `save=True`
4. Renders QSS via Jinja2 and calls `app.setStyleSheet(qss)`

**Parameters:**

| Name | Type | Description |
| --- | --- | --- |
| `source` | `str \| Path` | Path to the `.xml` or `.json` theme file. |
| `custom_tokens` | `dict[str, Any] \| None` | Token overrides. Mode-specific when top-level keys are `"light"` and/or `"dark"`. |
| `save` | `bool` | When `True` (default), persist the palette to `config/`. |

**Raises:** `ThemeParseError` — if the file is missing, malformed, or has missing tokens.

---

### `getTheme`

```python
def getTheme() -> ShadcnThemeTokens
```

Return the active palette tokens for the current mode.

---

### `setStyleSheet`

```python
def setStyleSheet(source: str | Path, *, save: bool = True) -> None
```

Set the additional stylesheet layered on top of the base QSS.

`source` can be an inline QSS/Jinja string or a path to a `.qss`/`.jinja` file.
When `save=True`, the content is persisted to `config/style.qss` or
`config/style.jinja`.

---

### `getStyleSheet`

```python
def getStyleSheet() -> str
```

Return the current additional stylesheet content.

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

`ThemeMode` accepts the following values:

| Value | Behavior |
| --- | --- |
| `"auto"` | Detects OS light/dark preference via `darkdetect` (default) |
| `"light"` | Always uses the `<light>` palette |
| `"dark"` | Always uses the `<dark>` palette |

When the mode is `"auto"` and the OS preference cannot be detected, the internal
default of `"dark"` is used.

---

## Models

### `ShadcnThemeTokens`

Immutable Pydantic model holding the resolved tokens for a single palette (light **or** dark). Returned by `getTheme`.

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
| `font_family` | `Open Sans` |
| `spacing` | `4px` |

---

### `ShadcnTheme`

Immutable Pydantic model holding both palettes.

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

Raised by `setTheme` and `parse_theme_source` when the theme file cannot be loaded or is invalid.

Common causes:

- File not found
- File is not an XML document (JSON, CSS, and URLs are rejected explicitly)
- Missing a required token in `<light>` or `<dark>`
- Token value is empty

```python
from qtshadcn import setTheme, ThemeParseError

try:
    setTheme("my_theme.xml")
except ThemeParseError as e:
    print(f"Theme error: {e}")
```
