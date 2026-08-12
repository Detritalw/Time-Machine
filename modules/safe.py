'''
Safe.py
## Bloret Launcher 错误处理模块

### 模块功能：
 - [x] 捕获未捕获的异常，并显示错误跟踪窗口。
 - [x] 显示错误跟踪窗口，并允许用户复制错误信息到剪贴板，并提交问题。
 - [x] 允许用户忽略警告。


***
###### Bloret Launcher 所有 © 2025 Bloret Launcher All rights reserved. © 2025 Bloret All rights reserved.
'''

import threading,logging,traceback,sys,webbrowser
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from modules.log import log, importlog

def handle_exception(e):
    '''
    ## 显示错误跟踪窗口并报告异常（RinUI 版本）
    '''
    exc_type = type(e)
    exc_value = e
    exc_traceback = e.__traceback__
    log("未捕获的异常:", logging.CRITICAL)
    log("类型: {}".format(exc_type), logging.CRITICAL)
    log("信息: {}".format(exc_value), logging.CRITICAL)
    log("回溯: {}".format(traceback.format_tb(exc_traceback)), logging.CRITICAL)
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = handle_exception

log_lock = threading.Lock()

def log_thread_safe(message, level=logging.INFO):
    with log_lock:
        log(message, level)

importlog("SAFE.PY")