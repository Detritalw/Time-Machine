from PyQt5.QtWidgets import QSystemTrayIcon, QApplication, QWidget
from PyQt5.QtCore import QFile
from PyQt5.uic import loadUi
from qfluentwidgets import FluentWindow, SystemTrayMenu, Action, setThemeColor, FluentIcon
import sys, logging, os, json
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sys, logging, os, json
# 以下导入的部分位于 modules 文件夹中
from modules.log import log
from modules.systems import get_system_theme_color,is_dark_theme,restart
from modules.backup import backup_folder
from modules.setupui import setup_backup_ui, setup_restore_ui
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
        
        if(self.isdarktheme):
            from qfluentwidgets import setTheme, Theme
            setTheme(Theme.AUTO)
            
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
        
        # 添加导航项
        restore_interface = self.restoreInterface if self.restoreInterface else QWidget()
        restore_interface.setObjectName("restoreInterface")
        backup_interface = self.backupInterface if self.backupInterface else QWidget()
        backup_interface.setObjectName("backupInterface")
        settings_interface = self.settingsInterface if self.settingsInterface else QWidget()
        settings_interface.setObjectName("settingsInterface")
        
        self.addSubInterface(restore_interface, FluentIcon.HISTORY, '还原')
        self.addSubInterface(backup_interface, FluentIcon.SYNC, '备份')
        self.addSubInterface(settings_interface, FluentIcon.SETTING, '设置')
        
        # 设置窗口样式
        self.setObjectName("mainWindow")
        self.resize(800, 600)

        setup_backup_ui(self, self.backupInterface, self.config['backup-folder']['to'])
        setup_restore_ui(self, self.restoreInterface, self.config['backup-folder']['to'])
        
        # 初始化其他功能
        # self.initOtherFunctions()

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
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.Trigger:  # 单击托盘图标
            if self.parent.isMinimized() or not self.parent.isVisible():
                self.parent.showNormal()
                self.parent.activateWindow()
            else:
                self.parent.hide()

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
    window.show()  # 确保主窗口先显示
    
    # 初始化系统托盘图标
    tray_icon = SystemTrayIcon(window)
    if tray_icon.isSystemTrayAvailable():
        log("系统托盘可用")
        tray_icon.show()
    else:
        log("系统托盘不可用", logging.ERROR)
    
    sys.exit(app.exec_())
