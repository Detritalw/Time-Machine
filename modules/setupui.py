from PyQt5.QtWidgets import QPushButton, QLabel
from modules.backup import backup_folder, calc_folder_size, calc_folder_num, get_last_backup_time
from modules.log import log
import datetime

def setup_backup_ui(self, widget, folder):
    backup_now_button = widget.findChild(QPushButton, "backup_now_button")
    last_backup_time = widget.findChild(QLabel, "last_backup_time")
    backup_size = widget.findChild(QLabel, "backup_size")
    backup_num = widget.findChild(QLabel, "backup_num")
    
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