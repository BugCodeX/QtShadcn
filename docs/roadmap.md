# Roadmap

QtShadcn is focused on becoming a stable, public theming layer for Qt desktop applications. The current release covers the most common building-block widgets; the next release targets the form and layout widgets that make up real applications.

---

## Release 0.0.6 — Public Readiness

The v0.0.6 release ships the foundation and the first set of styled widgets:

- ✅ Multi-binding support: PySide6, PyQt6, PySide2, PyQt5
- ✅ Binding-neutral internal `_qt` shim
- ✅ Widget gallery with sidebar and light/dark toggle
- ✅ QSS for `QWidget`, `QPushButton`, `QToolButton`, `QLineEdit`, `QTextEdit`
- ✅ Cross-platform CI: lint, type-check, docs, and tests under xvfb on Ubuntu
- ✅ Updated documentation and README for public install

---

## Next Release — Forms and Layout

The next release will add the widgets most applications need to build forms and settings panels:

- `QCheckBox` and `QRadioButton` — toggles and option groups
- `QComboBox` and `QSpinBox` / `QDoubleSpinBox` — selection and numeric inputs
- `QSlider` and `QProgressBar` — ranges and progress
- `QGroupBox` and `QFrame` — layout containers
- `QTabWidget` and `QStackedWidget` — navigation containers
- `QMenu`, `QMenuBar`, and `QToolBar` — chrome styling
- `QScrollBar` and `QScrollArea` — consistent scrolling chrome

---

## Future Work

Longer-term areas under consideration:

- `QTableView`, `QTreeView`, `QListView` — data views
- `QDialog` and modal chrome
- Additional bundled themes beyond the default
- Theme validation and authoring tools
- Accessibility improvements (focus indicators, color contrast options)

---

## Contributing

Open an issue on [GitHub](https://github.com/BugCodeX/QtShadcn/issues) if a widget you need is missing or if the gallery should demonstrate a specific state.
