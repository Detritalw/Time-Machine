from PyQt5.QtWidgets import QPushButton, QLabel, QComboBox
from qfluentwidgets import ComboBox, SmoothScrollArea, SpinBox, SwitchButton
from modules.backup import backup_folder, calc_folder_size, calc_folder_num, get_last_backup_time, get_backup_times
from modules.log import log
import datetime
import os
import json

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
    
    if backup_now_button:
        # 使用 lambda 传递参数
        backup_now_button.clicked.connect(lambda: backup_folder(widget))
    else:
        log("未找到 backup_now_button 控件")

    if last_backup_time:
        # 设置标签文本为上次备份时间
        ts = get_last_backup_time(folder)
        if ts:
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
        
def setup_restore_files_ui(self, widget, folder):
    restore_files = widget.findChild(SmoothScrollArea, "files")

    if restore_files:
        config_path = os.path.join(folder, "config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            now_value = config.get("now")
            log(f"config.json now: {now_value}")
        except Exception as e:
            log(f"读取 config.json 失败: {e}")
    else:
        log("未找到 files 控件")

def setup_restore_ui(self, widget, folder):
    backup_time = widget.findChild(ComboBox, "backup_time")

    if backup_time:
        times = get_backup_times(folder)
        formatted_times = []
        for ts in times:
            try:
                dt = datetime.datetime.fromtimestamp(float(ts))
                formatted_times.append(dt.strftime("%Y年%m月%d日 %H:%M:%S"))
            except Exception:
                formatted_times.append(str(ts))
        backup_time.addItems(formatted_times)
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
