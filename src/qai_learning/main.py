import sys

from PySide6.QtWidgets import (
    QApplication,
)

from qai_learning.gui.app_window import AppWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec())
