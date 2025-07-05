import json
import os
import shutil
import time
import hashlib
from modules.log import log


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
    比较源文件夹和指定的目标文件夹，返回新增或修改过的文件列表

    参数:
        from_folder (str): 源文件夹路径
        to_folder (str): 目标文件夹路径（通常为上次备份的最新时间戳文件夹）

    返回:
        list: 新增或修改的文件路径列表（相对于源文件夹）
    """
    different_files = []


    # 获取源文件夹所有文件及其哈希值
    from_files = {}
    for root, _, files in os.walk(from_folder):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, from_folder).replace(os.sep, '/')
            file_hash = calculate_file_hash(abs_path)
            from_files[rel_path] = file_hash

    # 如果目标文件夹不存在，则所有文件都需要备份
    if not os.path.exists(to_folder):
        return list(from_files.keys())

    # 获取目标文件夹所有文件及其哈希值
    to_files = {}
    for root, _, files in os.walk(to_folder):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, to_folder).replace(os.sep, '/')
            file_hash = calculate_file_hash(abs_path)
            to_files[rel_path] = file_hash

    # 对比两个文件树
    for rel_path, hash_value in from_files.items():
        if rel_path not in to_files or to_files[rel_path] != hash_value:
            different_files.append(rel_path)

    return different_files


def backup_folder():
    # Configure logging
    
    # 1. 读取配置文件(config.json) -> config
    log("正在读取配置文件: config.json")
    with open('config.json', 'r') as f:
        config = json.load(f)
    log(f"配置内容: {json.dumps(config, indent=2)}")
    
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
        for name in files:
            from_folder_tree.append(os.path.relpath(os.path.join(root, name), from_folder))
    log(f"源文件夹中的文件: {from_folder_tree}")
    
    # 7. 将 from_folder_tree 与 last_folder_tree 比对，将不同的文件列表 -> different_file_list
    log("比较源文件夹和最新时间戳文件夹之间的文件差异")
    if os.path.exists(to_folder):
        dirs = [d for d in os.listdir(to_folder) if os.path.isdir(os.path.join(to_folder, d)) and d.isdigit()]
        if dirs:
            latest_dir = max(dirs, key=lambda x: int(x))
            latest_folder_path = os.path.join(to_folder, latest_dir)
            log(f"最新时间戳文件夹路径: {latest_folder_path}")
            different_file_list = compare_folders(from_folder, latest_folder_path)
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
    os.makedirs(current_folder_path)
    log(f"创建新的时间戳文件夹: {current_folder_path}")
    
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
        elif os.path.isdir(os.path.dirname(src_path)):
            # 若是新目录结构，但未被创建，则创建对应目录
            os.makedirs(dst_path, exist_ok=True)
            log(f"为以下文件创建了目录结构: {file_rel}")
    
    # 10. 读取 to_folder/config.json -> time_config
    time_config_path = os.path.join(to_folder, 'config.json')
    log(f"从目标文件夹读取配置文件: {time_config_path}")
    if os.path.exists(time_config_path):
        with open(time_config_path, 'r') as f:
            time_config = json.load(f)
        log(f"现有配置内容: {json.dumps(time_config, indent=2)}")
    else:
        time_config = {"times": {}}
        log("未找到现有配置文件，正在创建新配置")
    
    # 11. 在 time_config 中的 times 中添加一个条目
    log(f"更新配置以记录新备份信息: {current_time}")
    time_config['times'][current_time] = {
        "files": different_file_list
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

    # 写回 config.json
    log(f"将更新后的配置写回 {time_config_path}")
    with open(time_config_path, 'w') as f:
        json.dump(time_config, f, indent=2)
    log("备份过程完成")


def normalize_path(path):
    """标准化路径格式，统一使用 '/' 分隔符"""
    return path.replace(os.sep, '/')


backup_folder()
