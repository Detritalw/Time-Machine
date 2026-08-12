"""Time Machine entry point — RinUI (PySide6 + QML)"""
import sys
import os
from pathlib import Path

from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

import RinUI
from RinUI import RinUIWindow, Theme, BackdropEffect
from src.backend import Backend

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent


def main():
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Time Machine")
    app.setOrganizationName("Bloret")

    # Create RinUI window
    window = RinUIWindow()

    # Backend bridge
    backend = Backend()
    window.engine.rootContext().setContextProperty("Backend", backend)

    # Load main QML
    qml_path = SCRIPT_DIR / ".." / "qml" / "TimeMachine.qml"
    window.load(str(qml_path.resolve()))

    # Icon
    icon_path = PROJECT_ROOT / "Time-Machine.ico"
    if icon_path.exists():
        window.setIcon(str(icon_path))

    # Title
    window.setProperty("title", "Time Machine")

    # Startup: check if self-starting (hidden mode)
    if "--self-starting" in sys.argv:
        window.root_window.setProperty("visibility", 1)  # Hide

    # Theme & backdrop
    window.setTheme(Theme.Auto)
    window.setBackdropEffect(BackdropEffect.Mica)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
