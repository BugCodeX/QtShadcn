---
name: naming-conventions
description: "Trigger: naming, naming convention, nomenclatura, camelCase, PascalCase, python naming, nombres variables, nombres metodos, signal naming, slot naming. Enforce strict QMaterialYou naming conventions across codebases."
license: MIT
metadata:
  author: BugCodeX
  version: "1.0"
---

# Skill: naming-conventions

## Purpose

Enforce consistent, expressive, and predictable naming conventions across the **QMaterialYou** codebase.

> **Context**: Ruff does not enforce naming style in this project (`N` rules are not selected). Therefore, this skill serves as the binding authority for all code authoring, refactoring, and code reviews.

## When to Use

- Writing or refactoring functions, methods, classes, variables, or properties.
- Declaring Qt Signals and Slots/Event Handlers.
- Defining Enums and global constants.
- Reviewing code for naming consistency and readability.

---

## Naming Matrix

| Symbol | Style | Example | Notes |
| --- | --- | --- | --- |
| **Functions & Methods** | `camelCase` (verb + context) | `resolveRadius`, `getThemeTokens`, `targetUrl` | At least two words (verb + context). |
| **Variables & Parameters** | `camelCase` (noun/context) | `buttonColor`, `iconFamily`, `targetRect` | Fully descriptive; no single letters. |
| **Private Methods & Attributes** | `_camelCase` (leading underscore) | `_updateStyle`, `_handleThemeChanged`, `_dirtyTheme` | Indicates internal/protected use. |
| **Classes, Mixins, Qt Widgets** | `PascalCase` | `FilledButton`, `HyperlinkButton`, `ImageCard` | Substantive nouns or noun phrases. |
| **Enum Classes** | `PascalCase` | `ThemeMode`, `ButtonSize`, `CardVariant` | Singular nouns. |
| **Enum Members & Constants** | `UPPER_SNAKE_CASE` | `BUTTON_SOURCE`, `DEFAULT_ICON_FAMILY`, `LIGHT` | Immutable global constants/enums. |
| **Qt Signals** | `camelCase` (noun/event + Changed/ed) | `themeChanged`, `colorChanged`, `hovered`, `focused` | Event-driven naming. |
| **Qt Event Handlers / Slots** | `_camelCase` (`_handle*` or `_on*`) | `_onThemeChanged`, `_onClicked`, `_handleUrlClick` | Clear event destination mapping. |

---

## Critical Rules

### 1. Absolute Prohibition of Abbreviations

Variable and parameter names must be immediately clear without guessing. Never truncate terms:

- ❌ `btn`, `bg`, `col`, `fam`, `idx`, `tok`, `w`, `h`, `prop`, `dlg`
- ✅ `button`, `backgroundColor`, `color`, `fontFamily`, `index`, `tokens`, `width`, `height`, `property`, `dialog`

Exceptions:

- Standard loop counters in simple numeric ranges: `for i in range(...)` (prefer descriptive names if it represents a dimension or coordinate, e.g. `for row in range(...)`).
- Well-known Qt geometric objects when typed: `event` / `ev`, `rect` / `targetRect`.

---

### 2. Two-Word Rule for Functions and Methods (Verb + Context)

Every function and method must explicitly state the **action (verb)** and the **target (context)**. Single-word names are strictly prohibited:

- ❌ `theme()`
- ✅ `getTheme()`, `setTheme()`, `updateTheme()`

- ❌ `mode()`
- ✅ `getThemeMode()`, `setThemeMode()`

- ❌ `icon()`
- ✅ `resolveIconData()`, `renderIconPixmap()`

- ❌ `data()`
- ✅ `getCustomPropertyData()`, `loadCharmapData()`

---

### 3. Qt Property Getters & Setters

When implementing Qt Properties (`Property(...)`):

- **Getter**: `_get<PropertyName>()` or `<propertyName>()`
  - Example: `_getIconName()`, `_getIsIconFilled()`
- **Setter**: `_set<PropertyName>(value)` or `set<PropertyName>(value)`
  - Example: `_setIconName(name)`, `_setIsIconFilled(filled)`
- **Property Name**: `camelCase`
  - Example: `iconName = Property(str, _getIconName, _setIconName)`
  - Example: `isIconFilled = Property(bool, _getIsIconFilled, _setIsIconFilled)`

---

### 4. Boolean Flags and Predicates

Boolean variables, attributes, parameters, and properties should clearly convey truthfulness using prefixes (`is`, `has`, `should`, `can`):

- ❌ `filled`, `icon`, `visible_flag`
- ✅ `isIconFilled`, `hasIcon`, `shouldRepaint`, `canOpenUrl`

---

## Good vs. Bad Code Examples

### Bad Example (Violation of Conventions)

```python
# BAD
class my_btn(QWidget):
    chg = Signal()

    def __init__(self, col=None, w=100):
        self._bg = col
        self.w = w

    def col(self):
        return self._bg

    def click(self):
        self._on_click()

    def _on_click(self):
        pass
```

### Good Example (Strict Adherence)

```python
# GOOD
class ActionButton(QWidget):
    colorChanged = Signal()

    def __init__(self, backgroundColor: QColor | None = None, width: int = 100, parent: QWidget | None = None):
        super().__init__(parent)
        self._backgroundColor = backgroundColor
        self._buttonWidth = width

    def getBackgroundColor(self) -> QColor | None:
        return self._backgroundColor

    def setBackgroundColor(self, color: QColor) -> None:
        if self._backgroundColor != color:
            self._backgroundColor = color
            self.colorChanged.emit()
            self._updateStyle()

    def _onButtonClicked(self) -> None:
        self._handleActionTriggered()

    def _updateStyle(self) -> None:
        self.update()
```
