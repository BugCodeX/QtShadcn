"""Gallery window shell."""

from __future__ import annotations

import logging
from pathlib import Path

import qtshadcn
from examples.gallery.page_selector import PageSelector
from examples.gallery.pages import PAGE_REGISTRY
from examples.gallery.pages.overview import OverviewPage
from examples.gallery.theme_editor import ThemeEditor
from qtshadcn import ThemeConfig
from qtshadcn._qt import QtCore, QtGui, QtWidgets

logger = logging.getLogger(__name__)

_PAGE_MARGIN = 24
_SPACING = 16
_LEFT_PANEL_MIN_WIDTH = 420
_LEFT_PANEL_MARGIN = 16


class GalleryWindow(QtWidgets.QMainWindow):
    """Main gallery window with an always-visible left sidebar."""

    def __init__(
        self,
        app: QtWidgets.QApplication,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        """Initialize the gallery window with the given application."""
        super().__init__(parent)
        logger.debug("Initializing GalleryWindow")
        self._app = app
        self.setWindowTitle("QtShadcn Gallery")
        logo_path = Path(__file__).resolve().parents[2] / "docs" / "source" / "logo.ico"
        if logo_path.exists():
            self.setWindowIcon(QtGui.QIcon(str(logo_path)))
        self.resize(1100, 700)

        self._current_mode = "light"
        self._active_tokens = None
        self._stack = QtWidgets.QStackedWidget()
        self._selector = PageSelector()
        self._theme_toggle = QtWidgets.QPushButton("Dark mode")
        self._editor = ThemeEditor()
        self._editor_scroll = QtWidgets.QScrollArea()
        self._left_panel: QtWidgets.QWidget | None = None

        self._setup_pages()
        self._setup_selector()
        self._setup_ui()

        self._on_editor_changed()
        self.apply_theme("light")

    def apply_theme(self, mode: str) -> None:
        """Apply the requested theme mode and refresh the UI."""
        self._current_mode = mode
        logger.info("Applying theme mode: %s", mode)
        self._editor.set_active_mode(mode)
        self._active_tokens = qtshadcn.apply_theme(
            self._app,
            ThemeConfig(theme_source_path=str(self._working_xml_path()), theme_mode=mode),
        )
        self._theme_toggle.blockSignals(True)
        self._theme_toggle.setChecked(mode == "dark")
        self._theme_toggle.blockSignals(False)
        self._theme_toggle.setText("Light mode" if mode == "dark" else "Dark mode")
        self._update_sidebar_style()
        self._repolish(self)

    def _setup_pages(self) -> None:
        """Mount every page from the registry into the stacked widget."""
        self._overview_page: OverviewPage | None = None
        for label, builder in PAGE_REGISTRY:
            if label == "Overview":
                self._overview_page = OverviewPage()
                page = self._overview_page.build()
                self._overview_page.navigateToPage.connect(self._on_overview_navigate)
            else:
                page = builder()
            self._stack.addWidget(page)

    def _on_overview_navigate(self, label: str) -> None:
        """Switch the page selector to the requested gallery page."""
        for index, (page_label, _) in enumerate(PAGE_REGISTRY):
            if page_label == label:
                self._selector.setCurrentRow(index)
                return

    def _setup_selector(self) -> None:
        """Populate the page selector and wire it to the stack."""
        for label, _ in PAGE_REGISTRY:
            self._selector.add_page(label)
        self._selector.currentIndexChanged.connect(self._stack.setCurrentIndex)
        self._selector.setCurrentRow(0)

    def _setup_ui(self) -> None:
        """Build the central splitter with a left panel and a right page area."""
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        outer = QtWidgets.QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        self._left_panel = self._build_left_panel()
        right_area = self._build_right_area()

        splitter.addWidget(self._left_panel)
        splitter.addWidget(right_area)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        outer.addWidget(splitter)

    def _build_left_panel(self) -> QtWidgets.QWidget:
        """Build the always-visible left panel with selector, toggle, and editor."""
        panel = QtWidgets.QWidget()
        panel.setMinimumWidth(_LEFT_PANEL_MIN_WIDTH)
        panel.setProperty("class", "gallery-sidebar")
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(
            _LEFT_PANEL_MARGIN,
            _LEFT_PANEL_MARGIN,
            _LEFT_PANEL_MARGIN,
            _LEFT_PANEL_MARGIN,
        )
        layout.setSpacing(_SPACING)

        layout.addWidget(self._selector)

        self._theme_toggle.setCheckable(True)
        self._theme_toggle.setProperty("variant", "default")
        self._theme_toggle.toggled.connect(self._on_theme_toggled)
        layout.addWidget(self._theme_toggle)

        self._copy_xml_button = QtWidgets.QPushButton("Copy theme XML")
        self._copy_xml_button.setProperty("variant", "outline")
        self._copy_xml_button.clicked.connect(self._on_copy_xml_clicked)
        layout.addWidget(self._copy_xml_button)

        self._editor_scroll.setWidgetResizable(True)
        self._editor_scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self._editor_scroll.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._editor_scroll.setWidget(self._editor)
        layout.addWidget(self._editor_scroll, 1)

        self._editor.themeChanged.connect(self._on_editor_changed)

        return panel

    def _build_right_area(self) -> QtWidgets.QWidget:
        """Build the right area with a header and stacked gallery pages."""
        area = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(area)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QtWidgets.QWidget()
        header.setProperty("class", "gallery-header")
        header_layout = QtWidgets.QHBoxLayout(header)
        header_layout.setContentsMargins(
            _PAGE_MARGIN,
            _PAGE_MARGIN // 2,
            _PAGE_MARGIN,
            _PAGE_MARGIN // 2,
        )
        header_layout.setSpacing(_SPACING)

        title = QtWidgets.QLabel("QtShadcn Gallery")
        title.setProperty("class", "h2")
        header_layout.addWidget(title, 1)

        docs_button = QtWidgets.QPushButton("Open Docs")
        docs_button.setProperty("variant", "outline")
        docs_button.clicked.connect(self._open_docs)
        header_layout.addWidget(docs_button)

        layout.addWidget(header)
        layout.addWidget(self._stack, 1)

        return area

    def _on_theme_toggled(self, checked: bool) -> None:
        """Switch the theme mode when the toggle button changes state."""
        mode = "dark" if checked else "light"
        self.apply_theme(mode)

    def _on_copy_xml_clicked(self) -> None:
        """Copy the current theme XML to the application clipboard."""
        xml_bytes = self._editor.to_xml_bytes()
        QtWidgets.QApplication.clipboard().setText(xml_bytes.decode("utf-8"))
        logger.info("Copied theme XML to clipboard")

    def _on_editor_changed(self) -> None:
        """Persist the editor palette and reapply the theme."""
        path = self._working_xml_path()
        path.write_bytes(self._editor.to_xml_bytes())
        self.apply_theme(self._current_mode)

    def _open_docs(self) -> None:
        """Open the project documentation in the default browser."""
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://BugCodeX.github.io/QtShadcn/"))

    def _update_sidebar_style(self) -> None:
        """Apply the sidebar background/border using the active theme tokens."""
        if self._left_panel is None or self._active_tokens is None:
            return
        self._left_panel.setStyleSheet(
            f".gallery-sidebar {{"
            f"  background-color: {self._active_tokens.muted};"
            f"  border-right: 1px solid {self._active_tokens.border};"
            "}"
        )

    def _working_xml_path(self) -> Path:
        """Return the deterministic working theme path under AppData."""
        app_data = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppDataLocation)
        path = Path(app_data) / "qtshadcn" / "gallery"
        path.mkdir(parents=True, exist_ok=True)
        return path / "working.xml"

    def _repolish(self, widget: QtWidgets.QWidget) -> None:
        """Unpolish and polish every descendant so QSS property selectors apply."""
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        for child in widget.findChildren(QtWidgets.QWidget):
            child.style().unpolish(child)
            child.style().polish(child)
            child.update()
        widget.update()
