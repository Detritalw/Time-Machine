"""Time Machine — RinUI 版本入口
PySide6 + RinUI (QML) 重写
用法: python time_machine_rinui.py
"""
import sys, os, json, logging
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QIcon, QGuiApplication
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

import RinUI
from RinUI import RinUIWindow, Theme, BackdropEffect

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.log import log
from modules.systems import is_dark_theme, setup_startup_with_self_starting
from src.backend import Backend


def main():
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Time Machine")
    app.setOrganizationName("Bloret")

    # 配置
    config_path = PROJECT_ROOT / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Backend
    backend = Backend()

    # 图标
    icon_path = PROJECT_ROOT / "Time-Machine.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # RinUI 窗口
    window = RinUIWindow()
    window.engine.rootContext().setContextProperty("Backend", backend)

    qml_path = PROJECT_ROOT / "qml" / "TimeMachine.qml"
    window.load(str(qml_path.resolve()))

    # 设置属性
    window.setTheme(Theme.Auto)
    try:
        window.setBackdropEffect(BackdropEffect.Mica)
    except OSError:
        pass  # 非 Windows 忽略

    root = window.root_window
    root.setProperty("title", "Time Machine")

    # 托盘
    _setup_tray(app, window, icon_path, backend)

    # 开机自启
    if config.get("self-starting", False):
        setup_startup_with_self_starting(True)

    # 隐藏模式
    if "--self-starting" in sys.argv:
        root.hide()

    # 启动时自动备份
    if config.get("backup_at_run", False):
        log("启动时自动备份")
        backend.startBackup()

    # 自动备份定时器
    interval = config.get("auto_backup_time", 0)
    if interval > 0:
        timer = QTimer()
        timer.timeout.connect(backend.startBackup)
        timer.start(interval * 1000)
        log(f"自动备份定时器已启动，间隔: {interval} 秒")

    sys.exit(app.exec())


def _setup_tray(app, window, icon_path, backend):
    if not QSystemTrayIcon.isSystemTrayAvailable():
        return
    tray = QSystemTrayIcon(app)
    if icon_path.exists():
        tray.setIcon(QIcon(str(icon_path)))

    menu = QMenu()
    menu.addAction("备份文件", backend.startBackup)
    menu.addAction("显示主窗口", window.root_window.show)
    menu.addSeparator()
    menu.addAction("退出", app.quit)

    tray.setContextMenu(menu)

    def on_activated(reason):
        if reason == QSystemTrayIcon.Trigger:
            root = window.root_window
            if root.isVisible():
                root.hide()
            else:
                root.show()

    tray.activated.connect(on_activated)
    tray.show()
    log("系统托盘已就绪")


if __name__ == "__main__":
    main()
