import os,logging,shutil
from datetime import datetime

copyright = "\n© 2025 Time_Machine All rights reserved."

# 创建日志文件夹
log_folder = os.path.join(os.getenv('APPDATA'), 'Time_Machine_Backup', 'log')
if not os.path.exists(log_folder):
    os.makedirs(log_folder)
# 设置日志配置
log_filename = os.path.join(log_folder, f'Time_Machine_Backup_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
if not os.path.exists(log_filename):
    with open(log_filename, 'w', encoding='utf-8') as f:
        f.write('')  # 创建空日志文件
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)

def log(message, level=logging.INFO):
    '''
    发送日志消息，输出到控制台并记录到日志文件。
    ***
    ###### Bloret Launcher 所有 © 2025 Bloret Launcher All rights reserved. © 2025 Bloret All rights reserved.
    '''
    print(message)
    logging.log(level, message)
    logging.getLogger().handlers[0].flush()  # 强制刷新日志
def importlog(message):
    log(f"{message} 的导入已完成。{copyright}")

def clear_log_files():
    '''
    清空日志文件。删除 `{%appdata%}/Bloret-Launcher/log` 文件夹下的所有文件。
    '''
    log_folder = os.path.join(os.getenv('APPDATA'), 'Bloret-Launcher', 'log')
    count = 0
    if os.path.exists(log_folder) and os.path.isdir(log_folder):
        file_num = len(os.listdir(log_folder))-1  # 减去一个正在使用的文件
        for filename in os.listdir(log_folder):
            file_path = os.path.join(log_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                count += 1
            except Exception as e:
                log(f"Failed to delete {file_path}. Reason: {e}", logging.ERROR)
    log(f"已清理 {count} 个日志文件")
    return count
    
    
# importlog("LOG.PY")