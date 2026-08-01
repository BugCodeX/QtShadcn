# Changelog

All notable changes to this project will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.0.1] — Unreleased

### Added

- Native XML theme format with `<light>` and `<dark>` palette sections
- `apply_theme(app, config)` — single-call theme application
- `get_theme()` — retrieve the cached resolved theme
- `ThemeConfig` — immutable configuration model (`theme_source_path`, `theme_mode`)
- `ThemeMode` enum — `auto`, `light`, `dark`
- `ShadcnThemeTokens` — resolved palette model with 22 design tokens
- `ShadcnTheme` — container for both light and dark palettes
- `ThemeParseError` — typed exception for all parse and validation failures
- Color format support: hex, `rgb()`, `rgba()`, CSS Color 4-style `hsl()`, `oklch()`, `rem`
- Disk cache — QSS is re-rendered only when the source file changes (mtime-based)
- OS theme auto-detection via `darkdetect`
- Bundled fonts: Open Sans and Roboto
- Default built-in theme
