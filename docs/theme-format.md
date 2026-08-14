# Theme Format

A QtShadcn theme is a plain **XML file** containing two palette sections: `<light>` and `<dark>`.

```xml
<theme>
  <light>
    <!-- design tokens -->
  </light>
  <dark>
    <!-- design tokens -->
  </dark>
</theme>
```

Both sections are required. Unknown tokens are silently ignored, so you can add your own custom tokens freely.

---

## Required Tokens

Every palette section must contain **all 22 tokens** listed below. If any are missing, `setTheme` raises a `ThemeParseError`.

| Token | Description | Example |
| --- | --- | --- |
| `background` | Main window / widget background | `#ffffff` |
| `foreground` | Default text color | `#020617` |
| `card` | Card component background | `#ffffff` |
| `card_foreground` | Card text color | `#020617` |
| `popover` | Popover / dropdown background | `#ffffff` |
| `popover_foreground` | Popover text color | `#020617` |
| `primary` | Primary action color (buttons, etc.) | `#0f172a` |
| `primary_foreground` | Text on primary backgrounds | `#f8fafc` |
| `secondary` | Secondary / subtle backgrounds | `#f1f5f9` |
| `secondary_foreground` | Text on secondary backgrounds | `#0f172a` |
| `accent` | Accent / highlight color | `#f1f5f9` |
| `accent_foreground` | Text on accent backgrounds | `#0f172a` |
| `muted` | Muted / disabled background | `#f1f5f9` |
| `muted_foreground` | Muted text | `#64748b` |
| `destructive` | Destructive action color | `#ef4444` |
| `destructive_foreground` | Text on destructive backgrounds | `#f8fafc` |
| `border` | Default border color | `#e2e8f0` |
| `input` | Input field border color | `#e2e8f0` |
| `ring` | Focus ring color | `#0f172a` |
| `radius` | Default border radius | `8px` |
| `font_family` | CSS font-family stack | `system-ui, sans-serif` |
| `spacing` | Base spacing unit | `4px` |

---

## Supported Token Values

Color and size values are used directly in the generated QSS, so they must be Qt-compatible.

### Colors

Use HEX colors:

```xml
<primary>#0f172a</primary>
```

`rgb()` and `rgba()` values are accepted as QSS-compatible passthrough values:

```xml
<primary>rgb(15, 23, 42)</primary>
<primary>rgba(15, 23, 42, 0.8)</primary>
```

### Sizes

Use pixel values for `radius` and `spacing`:

```xml
<radius>8px</radius>
<spacing>4px</spacing>
```

---

## Fonts

QtShadcn ships with **Open Sans** and **Roboto** under `qtshadcn/fonts/`. They are registered automatically when the stylesheet is rendered.

To use them, reference the family name in your theme:

```xml
<font_family>Open Sans</font_family>
```

```xml
<font_family>Open Sans</font_family>
```

The fallback chain (`sans-serif`) ensures the app works even on systems where the fonts can't be loaded.

---

## Full Example

```xml
<theme>
  <light>
    <background>#ffffff</background>
    <foreground>#020617</foreground>
    <card>#ffffff</card>
    <card_foreground>#020617</card_foreground>
    <popover>#ffffff</popover>
    <popover_foreground>#020617</popover_foreground>
    <primary>#0f172a</primary>
    <primary_foreground>#f8fafc</primary_foreground>
    <secondary>#f1f5f9</secondary>
    <secondary_foreground>#0f172a</secondary_foreground>
    <accent>#f1f5f9</accent>
    <accent_foreground>#0f172a</accent_foreground>
    <muted>#f1f5f9</muted>
    <muted_foreground>#64748b</muted_foreground>
    <destructive>#ef4444</destructive>
    <destructive_foreground>#f8fafc</destructive_foreground>
    <border>#e2e8f0</border>
    <input>#e2e8f0</input>
    <ring>#0f172a</ring>
    <radius>8px</radius>
    <font_family>Open Sans, system-ui, sans-serif</font_family>
    <spacing>4px</spacing>
  </light>
  <dark>
    <!-- dark palette tokens -->
  </dark>
</theme>
```
