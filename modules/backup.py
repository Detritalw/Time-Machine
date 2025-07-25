import json,os,shutil,time,hashlib,datetime
from modules.log import log
from PyQt5.QtWidgets import QPushButton, QLabel
import threading
from send2trash import send2trash

def calc_folder_size(folder_path):
    """
    计算文件夹的总大小
    
    参数:
        folder_path (str): 要计算大小的文件夹路径
    
    返回:
        int: 文件夹的总大小（以字节为单位）
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):  # 跳过符号链接
                total_size += os.path.getsize(fp)
    return total_size

def calc_folder_num(folder_path):
    '''
    计算文件夹中的文件夹数量 (不包括文件，也不包括子文件夹和子文件)
    '''
    count = 0
    if not os.path.exists(folder_path):
        return 0
    for entry in os.listdir(folder_path):
        full_path = os.path.join(folder_path, entry)
        if os.path.isdir(full_path):
            count += 1
    return count

def get_last_backup_time(to_folder):
    """
    获取上次备份的时间戳
    
    参数:
        to_folder (str): 目标文件夹路径
    
    返回:
        str: 上次备份的时间戳字符串，如果没有备份则返回 '无备份记录'
    """
    if not os.path.exists(to_folder):
        return '无备份记录'
    
    dirs = [d for d in os.listdir(to_folder) if os.path.isdir(os.path.join(to_folder, d)) and d.isdigit()]
    if not dirs:
        return '无备份记录'
    
    latest_dir = max(dirs, key=lambda x: int(x))
    return latest_dir

def get_backup_times(folder):
    """
    获取指定文件夹下的所有备份文件的时间戳列表。

    参数:
        folder (str): 文件夹路径

    返回:
        list: 时间戳列表
    """
    if not os.path.exists(folder):
        return []

    # 获取所有子文件夹的名称，这些名称应该是时间戳
    dirs = [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d)) and d.isdigit()]
    
    # 如果没有找到任何时间戳文件夹，返回空列表
    if not dirs:
        return []

    # 将字符串转换为整数并排序
    timestamps = sorted(int(d) for d in dirs)
    
    # 返回格式化后的时间戳列表
    log(f"获取到的时间戳列表: {timestamps}")
    return [str(ts) for ts in timestamps]

def calculate_file_hash(file_path, hash_algorithm='sha256'):
    """
    计算文件的哈希值
    
    参数:
        file_path (str): 要计算哈希的文件路径
        hash_algorithm (str): 哈希算法 (支持 'md5', 'sha1', 'sha256')
    
    返回:
        str: 文件的哈希值
    """
    if not os.path.isfile(file_path):
        return None
    
    hash_func = hashlib.new(hash_algorithm)
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def compare_folders(from_folder, to_folder):
    """
    比较源文件夹和目标文件夹，返回新增或修改过的文件列表

    参数:
        from_folder (str): 源文件夹路径
        to_folder (str): 目标文件夹路径（通常为上次备份的最新时间戳文件夹）

    返回:
        list: 新增或修改的文件路径列表（相对于源文件夹）
    """
    different_files = []

    # 检查源文件夹或目标文件夹是否存在
    if not os.path.exists(from_folder) or not os.path.exists(to_folder):
        if not os.path.exists(from_folder):
            log(f"源文件夹不存在: {from_folder}")
        if not os.path.exists(to_folder):
            log(f"目标文件夹不存在: {to_folder}")
        log("任一文件夹不存在，所有文件都将被备份")
        from_files = {}
        for root, _, files in os.walk(from_folder):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = normalize_path(os.path.relpath(abs_path, from_folder))
                file_hash = calculate_file_hash(abs_path)
                if file_hash is not None:
                    from_files[rel_path] = file_hash
                    log(f"源文件 {rel_path} 的哈希值: {file_hash}")
        return list(from_files.keys())

    # 获取源文件夹所有文件及其哈希值
    from_files = {}
    for root, _, files in os.walk(from_folder):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = normalize_path(os.path.relpath(abs_path, from_folder))
            file_hash = calculate_file_hash(abs_path)
            if file_hash is not None:
                from_files[rel_path] = file_hash
                log(f"源文件 {rel_path} 的哈希值: {file_hash}")
    
    # 获取目标文件夹的 now 字段内容
    if os.path.exists(os.path.join(to_folder, 'config.json')):
        with open(os.path.join(to_folder, 'config.json'), 'r') as f:
            try:
                target_config = json.load(f)
                now_files = target_config.get('now', {})
                log(f"使用目标文件夹配置的now字段进行比对")
            except json.JSONDecodeError:
                now_files = {}
                log(f"目标文件夹配置文件读取失败，所有文件都将被备份")
    else:
        now_files = {}
        log(f"目标文件夹配置文件不存在，所有文件都将被备份")
    
    # 对比源文件夹和目标文件夹的 now 字段
    for rel_path, hash_value in from_files.items():
        log(f"对比文件: {rel_path} (源哈希: {hash_value})")
        target_hash = now_files.get(rel_path)
        if rel_path not in now_files:
            log(f"发现不同的文件: {rel_path} (原因: 在目标文件夹配置中不存在)")
            different_files.append(rel_path)
        elif target_hash != hash_value:
            log(f"发现不同的文件: {rel_path} (源哈希: {hash_value}, 目标哈希: {target_hash})")
            different_files.append(rel_path)
        else:
            log(f"文件 {rel_path} 未发生变化 (哈希值相同)")
    
    # 计算并记录未变化的文件数量
    unchanged_count = len(from_files) - len(different_files)
    log(f"未发生变化的文件数量: {unchanged_count}")
    log(f"发现需要复制的文件数量: {len(different_files)}")
    log(f"需要复制的文件: {different_files}")
    
    return different_files

def setup_backup_ui(widget, folder):
    last_backup_time = widget.findChild(QLabel, "last_backup_time")
    backup_size = widget.findChild(QLabel, "backup_size")
    backup_num = widget.findChild(QLabel, "backup_num")

    if last_backup_time:
        # 设置标签文本为上次备份时间
        ts = get_last_backup_time(folder)
        if ts == '无备份记录':
            log(f"没有备份记录，显示: {ts}")
            last_backup_time.setText(f"{ts}")
        else:
            try:
                dt = datetime.datetime.fromtimestamp(float(ts))
                formatted_time = dt.strftime("%Y年%m月%d日 %H:%M:%S")
                last_backup_time.setText(f"{formatted_time}")
            except ValueError:
                log(f"无法转换时间戳: {ts}，显示原始值")
                last_backup_time.setText(f"{ts}")
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

def start_backup_thread(backup_interface):
    """启动一个独立线程来执行备份过程"""
    thread = threading.Thread(target=backup_folder, args=(backup_interface,))
    thread.start()
    log("备份线程已启动")


def backup_folder(backup_interface):
    # Configure logging

    # 1. 读取配置文件(config.json) -> config
    log("正在读取配置文件: config.json")
    with open('config.json', 'r') as f:
        config = json.load(f)
    log(f"配置内容: {json.dumps(config, indent=2)}")

    # 确保 config 中有 'times' 键
    if 'times' not in config:
        config['times'] = {}
        log("配置中缺少 'times' 键，已初始化为空字典")
    
    # 2. config[folder] -> folder
    log("从配置中获取文件夹设置")
    folder_config = config['backup-folder']
    log(f"文件夹配置: {json.dumps(folder_config, indent=2)}")
    
    # 3. folder[from] -> from_folder
    log("从文件夹配置中获取源文件夹路径")
    from_folder = folder_config['from']
    log(f"源文件夹: {from_folder}")
    
    # 4. folder[to] -> to_folder
    log("从文件夹配置中获取目标文件夹路径")
    to_folder = folder_config['to']
    log(f"目标文件夹: {to_folder}")
    
    # 5. 读取 to_folder 中名称上的时间戳最晚的那个文件夹的文件列表 -> last_folder_tree
    log(f"在 {to_folder} 中查找最新的时间戳文件夹")
    if os.path.exists(to_folder):
        dirs = [d for d in os.listdir(to_folder) if os.path.isdir(os.path.join(to_folder, d)) and d.isdigit()]
        if dirs:
            latest_dir = max(dirs, key=lambda x: int(x))
            last_folder_tree = os.listdir(os.path.join(to_folder, latest_dir))
            log(f"找到最新时间戳文件夹: {latest_dir}")
            log(f"最新文件夹中的文件: {last_folder_tree}")
        else:
            last_folder_tree = []
            log("目标文件夹中未找到时间戳文件夹")
    else:
        last_folder_tree = []
        log(f"目标文件夹不存在: {to_folder}")
    
    # 6. 读取 from_folder 的文件列表 -> from_folder_tree
    log(f"读取源文件夹中的文件: {from_folder}")
    from_folder_tree = []
    for root, dirs, files in os.walk(from_folder):
        # 添加文件夹
        for name in dirs:
            dir_path = os.path.join(root, name)
            rel_path = normalize_path(os.path.relpath(dir_path, from_folder))
            from_folder_tree.append(rel_path)
        # 添加文件
        for name in files:
            file_path = os.path.join(root, name)
            rel_path = normalize_path(os.path.relpath(file_path, from_folder))
            from_folder_tree.append(rel_path)
    log(f"源文件夹中的文件和文件夹: {from_folder_tree}")
    
    # 7. 将 from_folder_tree 与 last_folder_tree 比对，将不同的文件列表 -> different_file_list
    log("比较源文件夹和最新时间戳文件夹之间的文件差异")
    if os.path.exists(to_folder):
        dirs = [d for d in os.listdir(to_folder) if os.path.isdir(os.path.join(to_folder, d)) and d.isdigit()]
        if dirs:
            latest_dir = max(dirs, key=lambda x: int(x))
            latest_folder_path = os.path.join(to_folder, latest_dir)
            log(f"最新时间戳文件夹路径: {latest_folder_path}")
            # 使用 config['now'] 进行比对
            different_file_list = compare_folders(from_folder, to_folder)
        else:
            log("目标文件夹中未找到时间戳文件夹，所有文件都需要备份")
            different_file_list = list(from_folder_tree)  # 如果没有时间戳文件夹，则所有文件都需要备份
    else:
        log(f"目标文件夹不存在: {to_folder}，所有文件都需要备份")
        different_file_list = list(from_folder_tree)  # 如果目标文件夹不存在，则所有文件都需要备份

    log(f"发现需要复制的文件数量: {len(different_file_list)}")
    log(f"需要复制的文件: {different_file_list}")

    # 8. 在 to_folder 中创建一个名为 当前时间时间戳 的文件夹
    current_time = str(int(time.time()))
    current_folder_path = os.path.join(to_folder, current_time)
    try:
        os.makedirs(current_folder_path)
        log(f"创建新的时间戳文件夹: {current_folder_path}")
    except FileExistsError:
        log(f"时间戳文件夹已存在: {current_folder_path}")
        # 如果文件夹已存在，直接结束备份进程并日志记录。
        # current_time = str(int(time.time()) + 1)
        # current_folder_path = os.path.join(to_folder, current_time)
        # os.makedirs(current_folder_path)
        # log(f"使用新时间戳创建文件夹: {current_folder_path}")
        log(f"备份已存在，跳过此次备份")
        return

    # 9. 读取 from_folder 中 different_file_list 中的文件复制到 to_folder/当前时间时间戳/ 文件夹中
    log(f"将文件复制到 {current_folder_path}")
    for file_rel in different_file_list:
        src_path = os.path.join(from_folder, file_rel)
        dst_path = os.path.join(current_folder_path, file_rel)

        if os.path.isfile(src_path):
            # 确保目标路径的父目录存在
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(src_path, dst_path)
            log(f"已复制文件: {file_rel}")
        elif os.path.isdir(src_path):
            # 创建对应的空目录
            os.makedirs(dst_path, exist_ok=True)
            log(f"创建了空目录: {file_rel}")
            # 复制空目录的元数据
            shutil.copystat(src_path, dst_path)
            log(f"复制了空目录的元数据: {file_rel}")
    
    # 10. 读取 to_folder/config.json -> time_config
    time_config_path = os.path.join(to_folder, 'config.json')
    log(f"从目标文件夹读取配置文件: {time_config_path}")
    if os.path.exists(time_config_path):
        with open(time_config_path, 'r') as f:
            time_config = json.load(f)
        log(f"现有配置内容: {json.dumps(time_config, indent=2)}")
    else:
        time_config = {}
        log("未找到现有配置文件，正在创建新配置")

    # 确保 time_config 中有 'times' 键
    if 'times' not in time_config:
        time_config['times'] = {}
        log("配置中缺少 'times' 键，已初始化为空字典")

    # 确保 time_config 中有 'times' 键
    if 'times' not in time_config:
        time_config['times'] = {}
    log("已确保 'times' 键存在")

    # 读取目标文件夹的 config.json 获取历史备份记录
    time_config_path = os.path.join(to_folder, 'config.json')
    if os.path.exists(time_config_path):
        with open(time_config_path, 'r') as f:
            history_config = json.load(f)
        log(f"读取历史配置成功: {json.dumps(history_config, indent=2)}")
    else:
        history_config = {"times": {}}
        log("未找到历史配置文件，使用空配置")

    # 向 time_config['times'][current_time] 添加 'times' 字段
    file_times = {}

    for rel_path in from_folder_tree:
        normalized_path = normalize_path(rel_path)
        last_timestamp = None
        # 逆序检查历史备份记录，查找文件最后一次备份的时间戳
        for timestamp in sorted(history_config.get('times', {}).keys(), key=lambda x: int(x), reverse=True):
            if normalized_path in history_config['times'][timestamp].get('files', []):
                last_timestamp = timestamp
                break
        # 如果找不到历史记录，则使用当前时间戳
        file_times[normalized_path] = last_timestamp if last_timestamp is not None else current_time
    log(f"已添加 'times' 字段: {file_times}")

    # 更新 time_config['times'][current_time]
    time_config['times'][current_time] = {
        "files": different_file_list,
        "times": file_times
    }

    # 12. 将源文件夹结构写入 time_config 中的 now
    log("开始记录源文件夹结构到 time_config['now']")
    now_files = {}

    for root, _, files in os.walk(from_folder):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = normalize_path(os.path.relpath(abs_path, from_folder))
            file_hash = calculate_file_hash(abs_path)
            now_files[rel_path] = file_hash

    time_config['now'] = now_files
    log(f"已记录源文件夹结构，共 {len(now_files)} 个文件")

    # 13. 向 time_config['times'][current_time] 添加 'times' 字段
    log("开始向 time_config['times'][current_time] 添加 'times' 字段")
    file_times = {}
    
    # 确保 config 中有 'times' 键
    if 'times' not in config:
        config['times'] = {}
        log("配置中缺少 'times' 键，已初始化为空字典")

    # 构建文件树结构
    def build_file_tree(path, parent_key=""):
        file_tree = {}
        full_path = os.path.join(from_folder, path) if parent_key else from_folder
        for entry in os.listdir(full_path):
            entry_path = os.path.join(full_path, entry)
            rel_path = normalize_path(os.path.join(path, entry))
            key = entry if not parent_key else f"{parent_key}/{entry}"
            
            if os.path.isdir(entry_path):
                # 处理目录
                child_tree = build_file_tree(rel_path, key)
                file_hash = calculate_file_hash(entry_path)
                # 检查该目录是否在本次备份中被拷贝
                dir_in_current = any(rel_path == f for f in different_file_list)
                dir_time = current_time if dir_in_current else get_last_backup_time_for_dir(rel_path, history_config, current_time)
                file_tree[entry] = {
                    "time": dir_time,
                    "type": "folder",
                    "hash": file_hash,
                    "child": child_tree
                }
            elif os.path.isfile(entry_path):
                # 处理文件
                file_hash = calculate_file_hash(entry_path)
                # 检查该文件是否在本次备份中被拷贝
                file_in_current = rel_path in different_file_list
                file_time = current_time if file_in_current else get_last_backup_time_for_file(rel_path, history_config, current_time)
                file_tree[entry] = {
                    "time": file_time,
                    "type": "file",
                    "hash": file_hash,
                    "child": []
                }
        return file_tree

    # 更新 time_config['times'][current_time]
    file_tree = build_file_tree("")
    time_config['times'][current_time] = {
        "files": different_file_list,
        "times": file_tree
    }
    log(f"已添加 'times' 字段: {file_tree}")

    # 写回 config.json
    log(f"将更新后的配置写回 {time_config_path}")
    with open(time_config_path, 'w') as f:
        json.dump(time_config, f, indent=2)
    log("备份过程完成")
    setup_backup_ui(backup_interface, to_folder)
    log("已更新备份界面信息")


def normalize_path(path):
    """标准化路径格式，统一使用 '/' 分隔符"""
    return path.replace(os.sep, '/')


def backup_folder_thread(backup_interface):
    """
    在独立线程中运行备份任务。
    """
    try:
        backup_folder(backup_interface)
    except Exception as e:
        log(f"备份线程发生错误: {e}")


def backup_files(file, time):
    """
    从配置文件中读取备份设置，并将最新备份时间戳中的文件复制回源文件夹。
    """
    # 读取配置文件(config.json) -> config
    log("正在读取配置文件: config.json")
    with open('config.json', 'r') as f:
        config = json.load(f)
    to_folder = config['backup-folder']['to']
    from_folder = config['backup-folder']['from']

    # 检查并复制文件
    src_path = os.path.join(to_folder, time, file)
    dst_path = os.path.join(from_folder)

    if not os.path.exists(src_path):
        log(f"文件不存在: {src_path}")
        return False

    if not os.path.exists(dst_path):
        log(f"目标文件夹不存在: {dst_path}")
        return False

    shutil.copy2(src_path, dst_path)

    log("恢复过程完成")
    return True

def del_backup_files(file, time):
    '''
    删除备份文件
    '''
    # 读取配置文件(config.json) -> config
    log("正在读取配置文件: config.json")
    with open('config.json', 'r') as f:
        config = json.load(f)

    log("从配置中获取文件夹设置")
    to_folder = config['backup-folder']['to']
    log(f"目标文件夹: {to_folder}")

    time_config_path = os.path.join(to_folder, 'config.json')

    # 读取配置文件(to_folder/config.json) -> to_config
    log("正在读取配置文件: config.json")
    with open(time_config_path, 'r') as f:
        to_config = json.load(f)

    # 检查并删除 to_config['times'][time]
    del to_config['times'][time]['files'][file]
    log(f"已删除 to_config['times']['{time}']['files']['{file}']")
    del to_config['times'][time]['times'][file]
    log(f"已删除 to_config['times']['{time}']['times']['{file}']")

    # 将更新后的 to_config 写回 config.json
    log(f"将更新后的配置写回 {time_config_path}")
    with open(time_config_path, 'w') as f:
        json.dump(to_config, f, indent=2)

    # 检查并复制文件
    src_path = os.path.join(to_folder, time, file)

    if not os.path.exists(src_path):
        log(f"文件不存在: {src_path}")
        return False

    # 送到回收站
    send2trash(src_path)

    log("恢复过程完成")
    return True

def get_last_backup_time_for_file(file_path, history_config, current_time):
    """
    获取文件最后一次备份的时间戳
    
    参数:
        file_path (str): 文件路径（相对于源文件夹）
        history_config (dict): 历史备份配置
        current_time (str): 当前时间戳
    
    返回:
        str: 最后一次备份的时间戳，如果没有找到则返回当前时间戳
    """
    # 从历史备份记录中查找
    if 'times' in history_config:
        for timestamp in sorted(history_config['times'].keys(), key=lambda x: int(x), reverse=True):
            if file_path in history_config['times'][timestamp].get('times', {}):
                return timestamp
    return current_time

def get_last_backup_time_for_dir(dir_path, history_config, current_time):
    """
    获取目录最后一次备份的时间戳
    
    参数:
        dir_path (str): 目录路径（相对于源文件夹）
        history_config (dict): 历史备份配置
        current_time (str): 当前时间戳
    
    返回:
        str: 最后一次备份的时间戳，如果没有找到则返回当前时间戳
    """
    # 从历史备份记录中查找
    if 'times' in history_config:
        for timestamp in sorted(history_config['times'].keys(), key=lambda x: int(x), reverse=True):
            if dir_path in history_config['times'][timestamp].get('times', {}):
                return timestamp
    return current_time

# backup_folder()