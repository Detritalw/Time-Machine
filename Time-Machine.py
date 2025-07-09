from PyQt5.QtWidgets import QSystemTrayIcon, QApplication, QWidget
from PyQt5.QtCore import QFile, QTimer
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QColor, QPalette
from qfluentwidgets import FluentWindow, SystemTrayMenu, Action, setThemeColor, FluentIcon, NavigationItemPosition
import sys, logging, os, json
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sys, logging, os, json
# 以下导入的部分位于 modules 文件夹中
from modules.log import log
from modules.systems import get_system_theme_color,is_dark_theme, setup_startup_with_self_starting
from modules.backup import backup_folder
from modules.setupui import setup_backup_ui, setup_restore_ui, setup_settings_ui, setup_about_ui

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()

        # 初始化配置文件
        with open('config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        # 获取系统主题颜色
        theme_color = get_system_theme_color()
        log(f"系统主题颜色: {theme_color}")
        setThemeColor(theme_color)

        # 定义并获取isdarktheme变量
        self.isdarktheme = is_dark_theme()
        log(f"当前主题是否为暗色: {self.isdarktheme}")
        if(self.isdarktheme):
            from qfluentwidgets import setTheme, Theme
            setTheme(Theme.AUTO)
        else:
            # 监听系统主题变化
            QApplication.instance().paletteChanged.connect(self.apply_theme)
            self.apply_theme()
            
        self.setWindowTitle("Time Machine")
        icon_path = os.path.join(os.getcwd(), 'Time-Machine.ico')
        if os.path.exists(icon_path):
            log(f"图标路径存在: {icon_path}")
        else:
            log(f"图标路径不存在: {icon_path}", logging.ERROR)
        self.setWindowIcon(QIcon(icon_path))
        
        # 加载界面UI文件
        self.backupInterface = self.load_ui("ui/backup.ui")
        self.restoreInterface = self.load_ui("ui/restore.ui")
        self.settingsInterface = self.load_ui("ui/settings.ui")
        self.aboutInterface = self.load_ui("ui/about.ui")
        
        # 添加导航项
        restore_interface = self.restoreInterface if self.restoreInterface else QWidget()
        restore_interface.setObjectName("restoreInterface")
        backup_interface = self.backupInterface if self.backupInterface else QWidget()
        backup_interface.setObjectName("backupInterface")
        settings_interface = self.settingsInterface if self.settingsInterface else QWidget()
        settings_interface.setObjectName("settingsInterface")
        about_interface = self.aboutInterface if self.aboutInterface else QWidget()
        about_interface.setObjectName("aboutInterface")
        
        self.addSubInterface(restore_interface, FluentIcon.HISTORY, '还原',NavigationItemPosition.TOP)
        self.addSubInterface(backup_interface, FluentIcon.SYNC, '备份',NavigationItemPosition.TOP)
        self.addSubInterface(settings_interface, FluentIcon.SETTING, '设置',NavigationItemPosition.BOTTOM)
        self.addSubInterface(about_interface, FluentIcon.INFO, '关于',NavigationItemPosition.BOTTOM)
        
        # 设置窗口样式
        self.setObjectName("mainWindow")
        self.resize(800, 600)

        setup_backup_ui(self, self.backupInterface, self.config['backup-folder']['to'])
        setup_restore_ui(self, self.restoreInterface, self.config['backup-folder']['to'])
        setup_settings_ui(self, self.settingsInterface)
        setup_about_ui(self, self.aboutInterface)

        # 检查是否需要设置开机自启
        if self.config.get("self-starting", False):
            setup_startup_with_self_starting(True)

        
        if self.config.get('backup_at_run'):
            log("检测到开启自动备份设置，正在执行备份...")
            # 执行备份操作
            backup_folder(self.backupInterface)

        if self.config.get('auto_backup_time'):
            log(f"检测到自动备份时间设置为: {self.config['auto_backup_time']} 秒")
            self.backup_delay = self.config.get("auto_backup_time", 5) * 1000  # 转换为毫秒
            self.remaining_time = self.backup_delay  # 初始化剩余时间

            self.backup_timer = QTimer(self)
            self.backup_timer.timeout.connect(lambda: backup_folder(self.backupInterface))
            self.backup_timer.start(self.backup_delay)

            # 启动倒计时更新
            self.backup_delay = self.config.get("auto_backup_time", 5) * 1000  # 转换为毫秒
            self.remaining_time = self.backup_delay  # 初始化剩余时间

            # 启动倒计时更新 (1s)
            self.countdown_timer = QTimer(self)
            self.countdown_timer.timeout.connect(self.update_countdown_slot)
            self.countdown_timer.start(1000)  # 毎秒更新一次倒計時
            self.update_countdown_slot()  # 立即更新一次初始時間

        # 初始化其他功能
        # self.initOtherFunctions()
    
    def apply_theme(self, palette=None):
        if palette is None:
            palette = QApplication.palette()

        # 检测系统主题
        if palette.color(QPalette.Window).lightness() < 128:
            theme = "dark"
        else:
            theme = "light"

        if theme == "dark":
            self.setStyleSheet("""
                QWidget { background-color: #2e2e2e; color: #ffffff; }
                QPushButton { background-color: #3a3a3a; border: 1px solid #444444; color: #ffffff; }
                QPushButton:hover { background-color: #4a4a4a; color: #ffffff; }
                QPushButton:pressed { background-color: #5a5a5a; color: #ffffff; }
                QComboBox { background-color: #3a3a3a; border: 1px solid #444444; color: #ffffff; }
                QComboBox:hover { background-color: #4a4a4a; color: #ffffff; }
                QComboBox:pressed { background-color: #5a5a5a; color: #ffffff; }
                QComboBox QAbstractItemView { background-color: #2e2e2e; selection-background-color: #4a4a4a; color: #ffffff; }
                QLineEdit { background-color: #3a3a3a; border: 1px solid #444444; color: #ffffff; }
                QLabel { color: #ffffff; }
                QCheckBox { color: #ffffff; }
                QCheckBox::indicator { width: 20px; height: 20px; }
                QCheckBox::indicator:checked { image: url(ui/icon/checked.png); }
                QCheckBox::indicator:unchecked { image: url(ui/icon/unchecked.png); }
                """)
            palette.setColor(QPalette.Window, QColor("#2e2e2e"))
            palette.setColor(QPalette.WindowText, QColor("#ffffff"))
            palette.setColor(QPalette.Base, QColor("#1e1e1e"))
            palette.setColor(QPalette.AlternateBase, QColor("#2e2e2e"))
            palette.setColor(QPalette.ToolTipBase, QColor("#ffffff"))
            palette.setColor(QPalette.ToolTipText, QColor("#ffffff"))
            palette.setColor(QPalette.Text, QColor("#ffffff"))
            palette.setColor(QPalette.Button, QColor("#3a3a3a"))
            palette.setColor(QPalette.ButtonText, QColor("#ffffff"))
            palette.setColor(QPalette.BrightText, QColor("#ff0000"))
            palette.setColor(QPalette.Link, QColor("#2a82da"))
            palette.setColor(QPalette.Highlight, QColor("#2a82da"))
            palette.setColor(QPalette.HighlightedText, QColor("#000000"))
            self.setPalette(palette)
        else:
            self.setStyleSheet("")
            self.setPalette(self.style().standardPalette())

    def update_countdown_slot(self):
        """槽函数，用于更新倒计时并刷新界面"""
        if self.remaining_time > 0:
            self.remaining_time -= 1000  # 减少一秒（单位为毫秒）
        else:
            self.remaining_time = self.backup_delay  # 重置倒计时

        from modules.setupui import update_countdown
        update_countdown(self.backupInterface, self.remaining_time)

    def load_ui(self, ui_path):
        """加载.ui文件"""
        try:
            ui_file = QFile(ui_path)
            if not ui_file.open(QFile.ReadOnly):
                log(f"无法打开UI文件: {ui_path}", logging.ERROR)
                return None
            
            widget = loadUi(ui_file)
            ui_file.close()
            
            if not widget:
                log(f"UI文件加载失败: {ui_path}", logging.ERROR)
                return None
            
            log(f"成功加载UI文件: {ui_path}")
            return widget
        except Exception as e:
            log(f"加载UI文件时发生异常: {e}", logging.ERROR)
            return None
    
    def closeEvent(self, event):
        """重写关闭事件以最小化到托盘而非退出"""
        if self.tray_icon and self.tray_icon.isSystemTrayAvailable():
            # 隐藏主窗口
            self.hide()
            # 显示托盘消息（可选）
            # self.tray_icon.showMessage(
            #     "Time Machine",
            #     "程序已最小化至托盘",
            #     QIcon("Time-Machine.ico"),  # 使用你的图标路径
            #     2000
            # )
            event.ignore()  # 忽略默认的关闭事件
        else:
            event.accept()  # 如果没有可用的托盘，则正常关闭

class SystemTrayIcon(QSystemTrayIcon):
    """系统托盘图标"""
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        # 添加日志记录
        log("初始化系统托盘图标")
        
        if parent is None:
            log("警告：SystemTrayIcon 的 parent 参数为 None", logging.WARNING)
        
        # 检查图标文件是否存在
        icon_path = 'Time-Machine.ico'
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))  # 设置托盘图标
        else:
            log(f"托盘图标文件不存在: {icon_path}", logging.ERROR)
            # 使用默认图标作为回退
            default_icon = QIcon()
            self.setIcon(default_icon)
            log("使用默认图标作为回退")
        
        self.parent = parent
        self.main_window = parent

        # 创建托盘菜单
        self.menu = SystemTrayMenu(parent=parent)

        self.menu.addActions([
            Action(FluentIcon.SYNC, '备份文件', triggered=lambda: backup_folder(self.backupInterface)),
            Action(FluentIcon.CANCEL_MEDIUM,'退出程序', triggered=QApplication.quit)
        ])
        self.setContextMenu(self.menu)

        # 连接托盘图标激活事件
        self.activated.connect(self.on_tray_icon_activated)

    def on_tray_icon_activated(self, reason):
        """# 托盘图标激活事件"""
        if reason == QSystemTrayIcon.Trigger:  # 单击托盘图标
            if self.parent.isMinimized() or not self.parent.isVisible():
                self.parent.showNormal()
                self.parent.activateWindow()
            else:
                self.parent.hide()

    def load_ui(self, ui_path):
        """# 加载.ui文件"""
        try:
            ui_file = QFile(ui_path)
            if not ui_file.open(QFile.ReadOnly):
                log(f"无法打开UI文件: {ui_path}", logging.ERROR)
                return None
            
            widget = loadUi(ui_file)
            ui_file.close()
            
            if not widget:
                log(f"UI文件加载失败: {ui_path}", logging.ERROR)
                return None
            
            log(f"成功加载UI文件: {ui_path}")
            return widget
        except Exception as e:
            log(f"加载UI文件时发生异常: {e}", logging.ERROR)
            return None
    
    def initOtherFunctions(self):
        # 这里可以添加更多初始化代码
        pass

if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    window = MainWindow()

    # 如果启动参数包含 --self-starting，则不显示窗口
    if '--self-starting' in sys.argv:
        window.hide()  # 直接隐藏主窗口
    else:
        window.show()  # 否则正常显示主窗口
    
    # 初始化系统托盘图标
    tray_icon = SystemTrayIcon(window)
    if tray_icon.isSystemTrayAvailable():
        log("系统托盘可用")
        tray_icon.show()
    else:
        log("系统托盘不可用", logging.ERROR)
    
    # 将 tray_icon 保存为窗口的属性，以便 closeEvent 可以访问
    window.tray_icon = tray_icon
    
    sys.exit(app.exec_())
