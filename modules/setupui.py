from re import S
from PyQt5.QtWidgets import QPushButton, QLabel, QComboBox, QFileDialog, QVBoxLayout, QHBoxLayout, QWidget
from qfluentwidgets import ComboBox, SmoothScrollArea, SpinBox, SwitchButton, CardWidget, StrongBodyLabel, CaptionLabel, RoundMenu, Action, FluentIcon, HyperlinkLabel, PushButton
from modules.backup import backup_folder, calc_folder_size, calc_folder_num, get_last_backup_time, get_backup_times, backup_files, del_backup_files
from modules.log import log
from modules.systems import setup_startup_with_self_starting
import datetime
import os
import json
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from PyQt5 import QtCore

def update_countdown(widget, countdown_time):
    countdown_time = countdown_time // 1000  # 转换为秒
    backup_time_wait = widget.findChild(QLabel, "backup_time_wait")
    if backup_time_wait:
        # log(f"更新倒计时: {countdown_time} 秒")
        backup_time_wait.setText(f"下次备份 {countdown_time} 秒后")
    else:
        log("未找到 backup_time_wait 控件")


def on_auto_backup_time_changed(value):
    """
    当 SpinBox 值变化时，更新配置文件中的 auto_backup_time 字段
    """
    log(f"自动备份时间设置为: {value} 秒")
    config_path = os.path.join("config.json")
    try:
        # 读取现有配置
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # 如果文件不存在或格式错误，则初始化空配置
        config = {}

    # 更新配置项
    config["auto_backup_time"] = value

    try:
        # 写回配置文件
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        log(f"已更新配置: auto_backup_time={value}")
    except Exception as e:
        log(f"写入配置文件失败: {e}")

def on_self_starting_changed(value):
    """
    当 SwitchButton 状态变化时，更新配置文件中的 self-starting 字段
    """
    log(f"开机自启设置为: {value}")
    config_path = os.path.join("config.json")
    try:
        # 读取现有配置
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}
    config["self-starting"] = value
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        log(f"已更新配置: self-starting={value}")
        setup_startup_with_self_starting(value) # 更新开机自启设置
        log(f"已更新开机自启设置: {value}")
    except Exception as e:
        log(f"写入配置文件失败: {e}")

def on_backup_at_run_changed(value):
    """
    当 SwitchButton 状态变化时，更新配置文件中的 backup_at_run 字段
    """
    log(f"开机自动备份设置为: {value}")
    config_path = os.path.join("config.json")
    try:
        # 读取现有配置
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}
    config["backup_at_run"] = value
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        log(f"已更新配置: backup_at_run={value}")
    except Exception as e:
        log(f"写入配置文件失败: {e}")

def setup_backup_ui(self, widget, folder):
    backup_now_button = widget.findChild(QPushButton, "backup_now_button")
    last_backup_time = widget.findChild(QLabel, "last_backup_time")
    backup_size = widget.findChild(QLabel, "backup_size")
    backup_num = widget.findChild(QLabel, "backup_num")
    auto_backup_time = widget.findChild(SpinBox, "auto_backup_time")
    backup_at_run = widget.findChild(SwitchButton, "backup_at_run")
    from_folder_button = widget.findChild(QPushButton, "from_folder_button")
    to_folder_button = widget.findChild(QPushButton, "to_folder_button")
    to_folder_label = widget.findChild(HyperlinkLabel, "to_folder_label")
    from_folder_label = widget.findChild(HyperlinkLabel, "from_folder_label")

    # 读取配置文件(config.json) -> config
    log("正在读取配置文件: config.json")
    with open('config.json', 'r') as f:
        config = json.load(f)

    if to_folder_label:
        to_folder_label.setText(config["backup-folder"]["to"].replace("//", "/"))
        to_folder_label.setUrl(config["backup-folder"]["to"])
    else:
        log("未找到 to_folder_label 控件")
    
    if from_folder_label:
        from_folder_label.setText(config["backup-folder"]["from"].replace("//", "/"))
        from_folder_label.setUrl(config["backup-folder"]["from"])
    else:
        log("未找到 from_folder_label 控件")
    
    if backup_now_button:
        # 使用 lambda 传递参数
        backup_now_button.clicked.connect(lambda: backup_folder(widget))
    else:
        log("未找到 backup_now_button 控件")

    if last_backup_time:
        # 设置标签文本为上次备份时间
        ts = get_last_backup_time(folder)
        if ts:
            if ts == '无备份记录':
                last_backup_time.setText("无备份记录")
            else:
                dt = datetime.datetime.fromtimestamp(float(ts))
                formatted_time = dt.strftime("%Y年%m月%d日 %H:%M:%S")
                last_backup_time.setText(f"{formatted_time}")
        else:
            last_backup_time.setText("无")
    else:
        log("未找到 last_backup_time 控件")

    if backup_size:
        size_bytes = calc_folder_size(folder)
        for unit in [' B', ' KB', ' MB', ' GB', ' TB']:
            if size_bytes < 1024:
                break
            size_bytes /= 1024
        backup_size.setText(f"{size_bytes:.2f} {unit}")
    else:
        log("未找到 backup_size 控件")

    if backup_num:
        backup_num.setText(f"{calc_folder_num(folder)} 次")
    else:
        log("未找到 backup_num 控件")

    if auto_backup_time:
        # 从配置文件中获取 auto_backup_time 的初始值
        try:
            with open(os.path.join("config.json"), "r", encoding="utf-8") as f:
                config = json.load(f)
            initial_value = config.get("auto_backup_time", 3600)  # 默认值为 3600 秒
        except (FileNotFoundError, json.JSONDecodeError):
            initial_value = 3600  # 如果配置文件不存在或格式错误，默认值为 3600 秒

        auto_backup_time.setValue(initial_value)  # 设置 SpinBox 的初始值
        auto_backup_time.valueChanged.connect(
            lambda val: on_auto_backup_time_changed(val)
        )
    else:
        log("未找到 auto_backup_time 控件")

    if backup_at_run:
        backup_at_run.setChecked(
            get_backup_at_run_from_config()
        )
        backup_at_run.checkedChanged.connect(
            lambda val: on_backup_at_run_changed(val)
        )
    else:
        log("未找到 backup_at_run 控件")

    if from_folder_button:
        from_folder_button.clicked.connect(lambda: select_folder(widget, "from"))
    else:
        log("未找到 from_folder_button 控件")

    if to_folder_button:
        to_folder_button.clicked.connect(lambda: select_folder(widget, "to"))
    else:
        log("未找到 to_folder_button 控件")

def setup_restore_files_ui(self, widget, folder, selected_ts=None):
    restore_files = widget.findChild(SmoothScrollArea, "files")

    if restore_files:
        config_path = os.path.join(folder, "config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            now_value = config.get("now")
            log(f"config.json now: {now_value}")
            if selected_ts is not None:
                log(f"当前选中备份时间戳: {selected_ts}")
                # do thing selected_ts
                try:
                    times_data = config.get("times", {})
                    selected_time_data = times_data.get(str(selected_ts), {})
                    files_data = selected_time_data.get("times", {})
                    
                    # 创建一个 QWidget 作为滚动区域的内容容器
                    scroll_content = QWidget()
                    layout = QVBoxLayout(scroll_content)
                    
                    for filename, filedata in files_data.items():
                        ts = filedata["time"]
                        # 创建 CardWidget
                        card = CardWidget()
                        card_layout = QVBoxLayout()
                        
                        # 文件名标签
                        file_label = StrongBodyLabel(filename)
                        
                        # 次标签
                        if filedata["type"] == "file":
                            file_type_label = "文件"
                        elif filedata["type"] == "folder":
                            file_type_label = "文件夹"
                        else:
                            file_type_label = "未知"

                        sub_label = CaptionLabel(f"{file_type_label} · 时间: {time_to_time(ts)}")
                        
                        # 将标签添加到 CardWidget 中
                        card_layout.addWidget(file_label)
                        card_layout.addWidget(sub_label)

                        card.setContextMenuPolicy(Qt.CustomContextMenu)
                        # 连接右键点击信号到槽函数
                        card.customContextMenuRequested.connect(lambda pos, c=card, file=filename, time=selected_ts : show_context_menu(pos, c, file, time))

                        # 设置 CardWidget 的布局
                        card.setLayout(card_layout)
                        
                        # 将 CardWidget 添加到主布局
                        layout.addWidget(card)
                    
                    # 设置滚动区域的内容
                    restore_files.setWidget(scroll_content)
                    # 设置滚动区域的布局方式（可选）
                    restore_files.setWidgetResizable(True)
                    
                except Exception as e:
                    log(f"处理选中时间戳数据时出错: {e}")
        except Exception as e:
            log(f"读取 config.json 失败: {e}")
    else:
        log("未找到 files 控件")


def time_to_time(timestamp):
    """
    将时间戳转换为格式为 %Y年%m月%d日 %H:%M:%S 的字符串。

    参数:
        timestamp (str): 要转换的时间戳。

    返回:
        str: 格式化后的时间字符串。
    """
    if timestamp == "unknown":
        log("时间戳为 unknown")
        return "----年--月--日 --:--:--"
    dt = datetime.datetime.fromtimestamp(float(timestamp))
    return dt.strftime("%Y年%m月%d日 %H:%M:%S")


def setup_restore_ui(self, widget, folder):
    backup_time = widget.findChild(ComboBox, "backup_time")

    if backup_time:
        times = get_backup_times(folder)
        formatted_times = []
        log(f"times: {times}")
        if times == []:
            log("未找到备份数据")
            backup_time.addItems(["未找到备份数据"])
        else:
            for ts in times:
                try:
                    log(f"时间戳: {ts}")
                    formatted_times.append(time_to_time(ts))
                except Exception:
                    formatted_times.append(str(ts))
            backup_time.addItems(formatted_times)

        # 如果有时间戳数据，则默认选择最新的时间戳
        if times:
            latest_index = len(times) - 1  # 最新时间戳位于列表末尾
            backup_time.setCurrentIndex(latest_index)

        # 绑定选择变化事件
        def on_backup_time_changed(index):
            if index < 0 or index >= len(times):
                selected_ts = None
            else:
                selected_ts = times[index]
            setup_restore_files_ui(self, widget, folder, selected_ts)
        backup_time.currentIndexChanged.connect(on_backup_time_changed)

        # 初始化时也调用一次
        if times:
            setup_restore_files_ui(self, widget, folder, times[-1])  # 使用最新的时间戳初始化
        else:
            setup_restore_files_ui(self, widget, folder, None)
    else:
        log("未找到 backup_time 控件")

    setup_restore_files_ui(self,widget, folder)

def get_backup_at_run_from_config():
    config_path = os.path.join("config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get("backup_at_run", False)
    except Exception:
        return False

def select_folder(widget, folder_type):
    """
    打开文件夹选择对话框，选择的文件夹路径存储到配置文件中的 [backup-folder][folder_type]
    """
    folder_path = QFileDialog.getExistingDirectory(None, "选择文件夹", os.getcwd())
    if folder_path:
        config_path = os.path.join("config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            config = {}
        
        # 确保 backup-folder 存在
        if "backup-folder" not in config:
            config["backup-folder"] = {}
        
        # 更新对应的文件夹路径
        config["backup-folder"][folder_type] = folder_path
        
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            log(f"已更新配置: backup-folder.{folder_type}={folder_path}")
            # 更新界面显示
            if folder_type == "from":
                from_folder_label = widget.findChild(QLabel, "from_folder_label")
                if from_folder_label:
                    from_folder_label.setText(folder_path)
                    from_folder_label.setUrl(config["backup-folder"]["from"])
                else:
                    log("未找到 from_folder_label 控件")
            elif folder_type == "to":
                to_folder_label = widget.findChild(QLabel, "to_folder_label")
                if to_folder_label:
                    to_folder_label.setText(folder_path)
                    to_folder_label.setUrl(config["backup-folder"]["to"])
                else:
                    log("未找到 to_folder_label 控件")
        except Exception as e:
            log(f"写入配置文件失败: {e}")

def show_context_menu(pos, card, file, time):
    # 创建右键菜单
    menu = RoundMenu(card)
    test_action = Action(FluentIcon.INFO, f"{file} · {time_to_time(time)}", triggered=lambda: print(f"{file} · {time}"))
    restore_action = Action(FluentIcon.HISTORY, '恢复到原位置', triggered=lambda: backup_files(file, time))
    delete_action = Action(FluentIcon.DELETE, '从备份中删除', triggered=lambda: del_backup_files(file, time))

    menu.addActions([
        test_action,
        restore_action,
        delete_action
    ])

    # 计算全局位置并弹出菜单
    global_pos = card.mapToGlobal(pos)
    menu.exec(global_pos)

def setup_settings_ui(self, widget):
    TM_version = widget.findChild(StrongBodyLabel, "TM_version")
    Self_starting = widget.findChild(SwitchButton, "Self_starting")

    # 读取配置文件(config.json) -> config
    log("正在读取配置文件: config.json")
    with open('config.json', 'r') as f:
        config = json.load(f)

    if TM_version:
        TM_version.setText(config["ver"])
        log(f"版本: {config['ver']}")
    else :
        log("未找到 TM_version 控件")

    if Self_starting:
        Self_starting.setChecked(config.get("self-starting", False))
        Self_starting.checkedChanged.connect(lambda val: on_self_starting_changed(val))
    else:
        log("未找到 Self_starting 控件")

def setup_about_ui(self, widget):
    BSC_QQ = widget.findChild(PushButton, "BSC_QQ")
    button_github = widget.findChild(PushButton, "button_github")

    if BSC_QQ:
        BSC_QQ.clicked.connect(lambda: QtCore.QDesktopServices.openUrl(QtCore.QUrl("https://qm.qq.com/q/IM122YNoUo")))
    else :
        log("未找到 BSC_QQ 控件")

    if button_github:
        button_github.clicked.connect(lambda: QtCore.QDesktopServices.openUrl(QtCore.QUrl("https://github.com/Detritalw/Time-Machine")))
    else :
        log("未找到 button_github 控件")