"""Page registry for the widget gallery."""

from __future__ import annotations

from collections.abc import Callable

from examples.gallery.pages.checkbox import CheckboxPage
from examples.gallery.pages.combo_box import ComboBoxPage
from examples.gallery.pages.label import LabelPage
from examples.gallery.pages.line_edit import LineEditPage
from examples.gallery.pages.overview import OverviewPage
from examples.gallery.pages.push_button import PushButtonPage
from examples.gallery.pages.radio_button import RadioButtonPage
from examples.gallery.pages.text_edit import TextEditPage
from examples.gallery.pages.tool_button import ToolButtonPage
from qtshadcn._qt import QtWidgets

PageBuilder = Callable[[], QtWidgets.QWidget]

PAGE_REGISTRY: list[tuple[str, PageBuilder]] = [
    ("Overview", OverviewPage().build),
    ("QPushButton", PushButtonPage().build),
    ("QToolButton", ToolButtonPage().build),
    ("QLineEdit", LineEditPage().build),
    ("QTextEdit", TextEditPage().build),
    ("QCheckBox", CheckboxPage().build),
    ("QRadioButton", RadioButtonPage().build),
    ("QComboBox", ComboBoxPage().build),
    ("QLabel", LabelPage().build),
]


def build_pages() -> list[QtWidgets.QWidget]:
    """Build every page widget in the registry order."""
    return [builder() for _label, builder in PAGE_REGISTRY]
