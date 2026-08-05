"""QtShadcn widget gallery.

A binding-neutral example that demonstrates every currently supported styled
widget with a sidebar navigator and a light/dark theme toggle.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Make the package importable when running from a fresh clone without install.
_ROOT = Path(__file__).resolve().parents[2]
try:
    import qtshadcn  # noqa: F401
except ModuleNotFoundError:
    sys.path.insert(0, str(_ROOT))
    import qtshadcn  # noqa: F401

from qtshadcn import ThemeConfig, apply_theme  # noqa: E402
from qtshadcn._qt import QtCore, QtWidgets  # noqa: E402

_SIDEBAR_WIDTH = 220
_PAGE_MARGIN = 24
_SPACING = 16


class GalleryWindow(QtWidgets.QMainWindow):
    """Main gallery window with a global header, sidebar, and stacked pages."""

    def __init__(self, app: QtWidgets.QApplication) -> None:
        """Initialize the gallery window with the given application."""
        super().__init__()
        logger.debug("Initializing GalleryWindow")
        self._app = app
        self.setWindowTitle("QtShadcn Gallery")
        self.resize(900, 650)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        outer = QtWidgets.QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        outer.addWidget(self._build_top_bar())

        body = QtWidgets.QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self._stack = QtWidgets.QStackedWidget()
        self._sidebar = self._build_sidebar()
        body.addWidget(self._sidebar)
        body.addWidget(self._stack, 1)

        outer.addLayout(body, 1)

        self._pages: list[tuple[str, QtWidgets.QWidget]] = [
            ("Overview", self._build_overview_page()),
            ("QPushButton", self._build_push_button_page()),
            ("QToolButton", self._build_tool_button_page()),
            ("QLineEdit", self._build_line_edit_page()),
            ("QTextEdit", self._build_text_edit_page()),
            ("QCheckBox", self._build_checkbox_page()),
            ("QRadioButton", self._build_radio_button_page()),
            ("QComboBox", self._build_combo_box_page()),
        ]
        for label, page in self._pages:
            self._stack.addWidget(page)
            item = QtWidgets.QListWidgetItem(label)
            self._sidebar.addItem(item)

        self._sidebar.currentRowChanged.connect(self._stack.setCurrentIndex)
        self._sidebar.setCurrentRow(0)

        self._apply_theme("light")

    def _build_top_bar(self) -> QtWidgets.QWidget:
        """Build the global header with the theme toggle."""
        widget = QtWidgets.QWidget()
        widget.setProperty("class", "gallery-header")
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN // 2, _PAGE_MARGIN, _PAGE_MARGIN // 2)
        layout.setSpacing(_SPACING)

        title = QtWidgets.QLabel("QtShadcn Gallery")
        title.setProperty("class", "h2")
        layout.addWidget(title, 1)

        self._theme_toggle = QtWidgets.QPushButton("Dark mode")
        self._theme_toggle.setCheckable(True)
        self._theme_toggle.setProperty("variant", "outline")
        self._theme_toggle.toggled.connect(self._on_theme_toggled)
        layout.addWidget(self._theme_toggle)

        return widget

    def _build_sidebar(self) -> QtWidgets.QListWidget:
        """Build the left navigation sidebar."""
        sidebar = QtWidgets.QListWidget()
        sidebar.setFixedWidth(_SIDEBAR_WIDTH)
        sidebar.setProperty("class", "gallery-sidebar")
        return sidebar

    def _on_theme_toggled(self, checked: bool) -> None:
        """Reapply the theme and refresh dynamic properties across the window."""
        mode = "dark" if checked else "light"
        logger.info("Theme toggled to: %s", mode)
        self._apply_theme(mode)
        self._repolish(self)

    def _apply_theme(self, mode: str) -> None:
        """Apply the requested theme mode to the application."""
        logger.debug("Applying theme mode: %s", mode)
        apply_theme(self._app, ThemeConfig(theme_mode=mode))
        self._theme_toggle.setChecked(mode == "dark")
        self._theme_toggle.setText("Light mode" if mode == "dark" else "Dark mode")
        logger.debug("Theme applied and UI updated")

    def _repolish(self, widget: QtWidgets.QWidget) -> None:
        """Unpolish and polish every descendant so QSS property selectors apply."""
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        for child in widget.findChildren(QtWidgets.QWidget):
            child.style().unpolish(child)
            child.style().polish(child)
            child.update()
        widget.update()

    def _build_overview_page(self) -> QtWidgets.QWidget:
        """Build the overview page."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addWidget(self._page_title("Overview"))
        layout.addWidget(
            self._muted_label(
                "QtShadcn styles common Qt widgets with a single XML theme. "
                "Use the sidebar to explore supported widgets and states."
            )
        )

        content = QtWidgets.QLabel(
            "Supported widgets in this release: QWidget, QPushButton, QToolButton, "
            "QLineEdit, QTextEdit, QCheckBox, QRadioButton, QComboBox."
        )
        content.setWordWrap(True)
        layout.addWidget(content)

        layout.addStretch(1)
        return page

    def _build_push_button_page(self) -> QtWidgets.QWidget:
        """Build the QPushButton page covering variants, sizes, and states."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addWidget(self._page_title("QPushButton"))
        layout.addWidget(
            self._muted_label(
                "Buttons support variant and size properties, plus enabled and disabled states."
            )
        )
        layout.addWidget(self._separator())

        layout.addWidget(self._section_label("Variants"))
        layout.addLayout(self._variant_grid(QPushButtonVariantRow))

        layout.addWidget(self._section_label("Sizes"))
        sizes = QtWidgets.QHBoxLayout()
        sizes.setSpacing(_SPACING)
        for size, label in [
            ("xs", "Extra small"),
            ("sm", "Small"),
            ("default", "Default"),
            ("lg", "Large"),
        ]:
            btn = QtWidgets.QPushButton(label)
            btn.setProperty("size", size)
            sizes.addWidget(btn)
        layout.addLayout(sizes)

        layout.addWidget(self._section_label("Icon sizes"))
        icon_sizes = QtWidgets.QHBoxLayout()
        icon_sizes.setSpacing(_SPACING)
        for size, label in [
            ("icon-xs", "XS"),
            ("icon-sm", "S"),
            ("icon", "M"),
            ("icon-lg", "L"),
        ]:
            btn = QtWidgets.QPushButton(label)
            btn.setProperty("variant", "outline")
            btn.setProperty("size", size)
            icon_sizes.addWidget(btn)
        layout.addLayout(icon_sizes)

        layout.addStretch(1)
        return page

    def _build_tool_button_page(self) -> QtWidgets.QWidget:
        """Build the QToolButton page covering variants and icon sizes."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addWidget(self._page_title("QToolButton"))
        layout.addWidget(
            self._muted_label("Compact action controls for toolbars, toggles, and icon buttons.")
        )
        layout.addWidget(self._separator())

        layout.addWidget(self._section_label("Variants"))
        layout.addLayout(self._variant_grid(QToolButtonVariantRow))

        layout.addWidget(self._section_label("Icon sizes"))
        icon_sizes = QtWidgets.QHBoxLayout()
        icon_sizes.setSpacing(_SPACING)
        for size, label, fixed in [
            ("icon-sm", "S", 28),
            ("icon", "M", 36),
            ("icon-lg", "L", 48),
        ]:
            btn = QtWidgets.QToolButton()
            btn.setText(label)
            btn.setProperty("variant", "outline")
            btn.setProperty("size", size)
            btn.setFixedSize(fixed, fixed)
            icon_sizes.addWidget(btn)
        layout.addLayout(icon_sizes)

        layout.addStretch(1)
        return page

    def _build_line_edit_page(self) -> QtWidgets.QWidget:
        """Build the QLineEdit page covering common input states."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addWidget(self._page_title("QLineEdit"))
        layout.addWidget(
            self._muted_label(
                "Input fields for short text values, including validation and disabled states."
            )
        )
        layout.addWidget(self._separator())

        form = QtWidgets.QFormLayout()
        form.setSpacing(_SPACING)
        form.setVerticalSpacing(_SPACING)

        default = QtWidgets.QLineEdit()
        default.setPlaceholderText("Enter your email")
        form.addRow("Default", default)

        prefilled = QtWidgets.QLineEdit("Olivia Martin")
        prefilled.setPlaceholderText("Full name")
        form.addRow("Prefilled", prefilled)

        disabled = QtWidgets.QLineEdit()
        disabled.setPlaceholderText("Unavailable field")
        disabled.setEnabled(False)
        form.addRow("Disabled", disabled)

        invalid = QtWidgets.QLineEdit("not-an-email")
        invalid.setPlaceholderText("Email address")
        invalid.setProperty("invalid", "true")
        form.addRow("Invalid", invalid)

        password = QtWidgets.QLineEdit("correct-horse-battery-staple")
        password.setPlaceholderText("Password")
        password.setEchoMode(QtWidgets.QLineEdit.Password)
        form.addRow("Password", password)

        layout.addLayout(form)
        layout.addStretch(1)
        return page

    def _build_text_edit_page(self) -> QtWidgets.QWidget:
        """Build the QTextEdit page covering textarea states."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addWidget(self._page_title("QTextEdit"))
        layout.addWidget(
            self._muted_label("Textarea control for longer content, with focus and invalid states.")
        )
        layout.addWidget(self._separator())

        form = QtWidgets.QFormLayout()
        form.setSpacing(_SPACING)
        form.setVerticalSpacing(_SPACING)

        default = QtWidgets.QTextEdit()
        default.setPlaceholderText("Enter a longer message...")
        default.setMinimumHeight(120)
        form.addRow("Default", default)

        disabled = QtWidgets.QTextEdit("This field is disabled.")
        disabled.setEnabled(False)
        disabled.setMinimumHeight(120)
        form.addRow("Disabled", disabled)

        invalid = QtWidgets.QTextEdit()
        invalid.setPlaceholderText("This field is invalid.")
        invalid.setProperty("invalid", "true")
        invalid.setMinimumHeight(120)
        form.addRow("Invalid", invalid)

        layout.addLayout(form)
        layout.addStretch(1)
        return page

    def _build_checkbox_page(self) -> QtWidgets.QWidget:
        """Build the QCheckBox page covering common checkbox states."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addWidget(self._page_title("QCheckBox"))
        layout.addWidget(
            self._muted_label(
                "Toggle controls for boolean choices, with checked, unchecked, indeterminate, and disabled states."
            )
        )
        layout.addWidget(self._separator())

        layout.addWidget(self._section_label("States"))
        states = QtWidgets.QVBoxLayout()
        states.setSpacing(_SPACING)

        unchecked = QtWidgets.QCheckBox("Accept terms and conditions")
        states.addWidget(unchecked)

        checked = QtWidgets.QCheckBox("Subscribe to newsletter")
        checked.setChecked(True)
        states.addWidget(checked)

        indeterminate = QtWidgets.QCheckBox("Partially selected option")
        indeterminate.setTristate(True)
        indeterminate.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)
        states.addWidget(indeterminate)

        disabled_unchecked = QtWidgets.QCheckBox("Disabled option")
        disabled_unchecked.setEnabled(False)
        states.addWidget(disabled_unchecked)

        disabled_checked = QtWidgets.QCheckBox("Disabled checked option")
        disabled_checked.setChecked(True)
        disabled_checked.setEnabled(False)
        states.addWidget(disabled_checked)

        layout.addLayout(states)

        layout.addWidget(self._separator())
        layout.addWidget(self._section_label("Invalid"))

        invalid_layout = QtWidgets.QVBoxLayout()
        invalid_layout.setSpacing(_SPACING)

        invalid = QtWidgets.QCheckBox("Invalid checkbox")
        invalid.setProperty("invalid", "true")
        invalid_layout.addWidget(invalid)

        invalid_checked = QtWidgets.QCheckBox("Invalid checked checkbox")
        invalid_checked.setChecked(True)
        invalid_checked.setProperty("invalid", "true")
        invalid_layout.addWidget(invalid_checked)

        invalid_indeterminate = QtWidgets.QCheckBox("Invalid indeterminate checkbox")
        invalid_indeterminate.setTristate(True)
        invalid_indeterminate.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)
        invalid_indeterminate.setProperty("invalid", "true")
        invalid_layout.addWidget(invalid_indeterminate)

        layout.addLayout(invalid_layout)
        layout.addStretch(1)
        return page

    def _build_radio_button_page(self) -> QtWidgets.QWidget:
        """Build the QRadioButton page covering common radio button states."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addWidget(self._page_title("QRadioButton"))
        layout.addWidget(
            self._muted_label(
                "Radio buttons for selecting one option from a set, with checked, unchecked, and disabled states."
            )
        )
        layout.addWidget(self._separator())

        layout.addWidget(self._section_label("States"))
        states = QtWidgets.QVBoxLayout()
        states.setSpacing(_SPACING)

        unchecked = QtWidgets.QRadioButton("Default")
        states.addWidget(unchecked)

        checked = QtWidgets.QRadioButton("Selected option")
        checked.setChecked(True)
        states.addWidget(checked)

        disabled_unchecked = QtWidgets.QRadioButton("Disabled option")
        disabled_unchecked.setEnabled(False)
        states.addWidget(disabled_unchecked)

        disabled_checked = QtWidgets.QRadioButton("Disabled selected")
        disabled_checked.setChecked(True)
        disabled_checked.setEnabled(False)
        states.addWidget(disabled_checked)

        layout.addLayout(states)

        layout.addWidget(self._separator())
        layout.addWidget(self._section_label("Invalid"))

        invalid_layout = QtWidgets.QVBoxLayout()
        invalid_layout.setSpacing(_SPACING)

        invalid = QtWidgets.QRadioButton("Invalid radio button")
        invalid.setProperty("invalid", "true")
        invalid_layout.addWidget(invalid)

        invalid_checked = QtWidgets.QRadioButton("Invalid selected radio button")
        invalid_checked.setChecked(True)
        invalid_checked.setProperty("invalid", "true")
        invalid_layout.addWidget(invalid_checked)

        layout.addLayout(invalid_layout)
        layout.addStretch(1)
        return page

    def _build_combo_box_page(self) -> QtWidgets.QWidget:
        """Build the QComboBox page covering common combo box states."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addWidget(self._page_title("QComboBox"))
        layout.addWidget(
            self._muted_label(
                "Dropdown selection controls with styled trigger and popup."
            )
        )
        layout.addWidget(self._separator())

        layout.addWidget(self._section_label("States"))
        states = QtWidgets.QVBoxLayout()
        states.setSpacing(_SPACING)

        default = QtWidgets.QComboBox()
        default.addItems(["Next.js", "SvelteKit", "Nuxt.js", "Remix", "Astro"])
        default.setCurrentIndex(-1)
        default.setPlaceholderText("Select a framework")
        states.addWidget(default)

        selected = QtWidgets.QComboBox()
        selected.addItems(["Next.js", "SvelteKit", "Nuxt.js", "Remix", "Astro"])
        selected.setCurrentIndex(0)
        states.addWidget(selected)

        disabled = QtWidgets.QComboBox()
        disabled.addItems(["Option 1", "Option 2", "Option 3"])
        disabled.setEnabled(False)
        states.addWidget(disabled)

        layout.addLayout(states)

        layout.addWidget(self._separator())
        layout.addWidget(self._section_label("Invalid"))

        invalid_layout = QtWidgets.QVBoxLayout()
        invalid_layout.setSpacing(_SPACING)

        invalid = QtWidgets.QComboBox()
        invalid.addItems(["Option 1", "Option 2", "Option 3"])
        invalid.setProperty("invalid", "true")
        invalid_layout.addWidget(invalid)

        invalid_selected = QtWidgets.QComboBox()
        invalid_selected.addItems(["Option 1", "Option 2", "Option 3"])
        invalid_selected.setCurrentIndex(1)
        invalid_selected.setProperty("invalid", "true")
        invalid_layout.addWidget(invalid_selected)

        layout.addLayout(invalid_layout)
        layout.addStretch(1)
        return page

    def _page_title(self, text: str) -> QtWidgets.QLabel:
        """Return a page title label."""
        label = QtWidgets.QLabel(text)
        label.setProperty("class", "h3")
        return label

    def _section_label(self, text: str) -> QtWidgets.QLabel:
        """Return a section label."""
        label = QtWidgets.QLabel(text)
        label.setProperty("class", "h4")
        return label

    def _muted_label(self, text: str) -> QtWidgets.QLabel:
        """Return a muted description label."""
        label = QtWidgets.QLabel(text)
        label.setProperty("class", "muted")
        label.setWordWrap(True)
        return label

    def _separator(self) -> QtWidgets.QFrame:
        """Return a horizontal separator line."""
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setProperty("class", "separator")
        return line

    def _variant_grid(self, row_class: type) -> QtWidgets.QGridLayout:
        """Return a grid of variant rows for buttons."""
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(_SPACING)

        variants = ["default", "outline", "secondary", "ghost", "destructive"]
        for row, variant in enumerate(variants):
            grid.addWidget(QtWidgets.QLabel(variant), row, 0)
            grid.addLayout(row_class(variant), row, 1)
        return grid


def _button_with_property(variant: str, enabled: bool) -> QtWidgets.QPushButton:
    """Create a QPushButton with the given variant and enabled state."""
    btn = QtWidgets.QPushButton(variant.capitalize())
    btn.setProperty("variant", variant)
    btn.setEnabled(enabled)
    return btn


def _tool_button_with_property(variant: str, enabled: bool) -> QtWidgets.QToolButton:
    """Create a QToolButton with the given variant and enabled state."""
    btn = QtWidgets.QToolButton()
    btn.setText(variant.capitalize())
    btn.setProperty("variant", variant)
    btn.setEnabled(enabled)
    return btn


class QPushButtonVariantRow(QtWidgets.QHBoxLayout):
    """Row showing an enabled and disabled QPushButton for a variant."""

    def __init__(self, variant: str) -> None:
        """Create a row with enabled and disabled push buttons for the variant."""
        super().__init__()
        self.setSpacing(_SPACING)
        self.addWidget(_button_with_property(variant, True))
        self.addWidget(_button_with_property(variant, False))
        self.addStretch(1)


class QToolButtonVariantRow(QtWidgets.QHBoxLayout):
    """Row showing an enabled and disabled QToolButton for a variant."""

    def __init__(self, variant: str) -> None:
        """Create a row with enabled and disabled tool buttons for the variant."""
        super().__init__()
        self.setSpacing(_SPACING)
        self.addWidget(_tool_button_with_property(variant, True))
        self.addWidget(_tool_button_with_property(variant, False))
        self.addStretch(1)


def main() -> int:
    """Run the gallery application."""
    logger.info("Starting QtShadcn Gallery")
    app = QtWidgets.QApplication(sys.argv)
    window = GalleryWindow(app)
    window.show()
    logger.info("Gallery window displayed")
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
