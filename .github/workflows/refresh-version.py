import json

'''
修改 config.json 文件中的指定字段
'''
# 读取 config.json 文件
with open('config.json', 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

# 修改 config.json 的指定字段
config['backup-folder'] = {
        "from": "",
        "to": ""
    }

# 保存修改后的 config.json
with open('config.json', 'w', encoding='utf-8') as config_file:
    json.dump(config, config_file, indent=4)

print("Config values updated successfully.")

'''
修改 Time-Machine-Setup.iss 文件中的 MyAppVersion 字段
'''
# 获取 ver 值并转换为字符串
version = config.get('ver', '')
version_str = str(version)

# 读取 Time-Machine-Setup.iss 文件
setup_file_path = 'Time-Machine-Setup.iss'
with open(setup_file_path, 'r', encoding='utf-8') as setup_file:
    setup_content = setup_file.readlines()

# 修改 MyAppVersion 的值
for i, line in enumerate(setup_content):
    if line.startswith('#define MyAppVersion'):
        setup_content[i] = f'#define MyAppVersion "{version_str}-Beta"\n'
        break

# 保存修改后的内容
with open(setup_file_path, 'w', encoding='utf-8') as setup_file:
    setup_file.writelines(setup_content)

print(f"Updated MyAppVersion to {version_str} in {setup_file_path}")