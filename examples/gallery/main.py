"""QtShadcn widget gallery bootstrap.

This entry point only creates the QApplication and shows the gallery window.
All page and theme editor logic lives in the sibling ``examples.gallery``
modules.
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

from examples.gallery.window import GalleryWindow  # noqa: E402
from qtshadcn._qt import QtWidgets  # noqa: E402


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
