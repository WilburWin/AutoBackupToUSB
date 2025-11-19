# AutoBackup.py
"""
U盘自动备份程序(无GUI界面) V1.0
1. 自动备份指定目录下的所有文件到 U 盘
2. 自动归档旧版文件
"""
import os,re
import shutil
import hashlib
import time
from datetime import datetime
import sys

CONFIG_FILE = "backup_paths.txt"    # 配置文件
BACKUP_ROOT = "backups"             # 备份根目录

def get_file_hash(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
def load_backup_paths():
    paths = []
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and os.path.exists(line):
                    paths.append(line)
    return paths
# paths = load_backup_paths()
# print(paths )

def AutoBackup():
    # 检查配置文件
    if not os.path.exists(CONFIG_FILE):
        try:
            import subprocess
            subprocess.Popen("ConfigTool.exe")  # 自动帮用户打开配置程序
        except:
            raise Exception("请先运行 ConfigTool.exe 配置程序")
    # 加载配置文件
    paths = load_backup_paths()
    # 检查备份根目录
    if not os.path.exists(BACKUP_ROOT):
        os.makedirs(BACKUP_ROOT)


    # 开始备份
    file2backup_count = 0       #新备份文件计数
    for backup_path in paths:
        if not os.path.exists(backup_path): 
            print(f"跳过此计算机不存在的路径: {backup_path}")
            continue
        # 把路径中的非法字符全部换成下划线，并把开头的盘符后面的 : 也换掉
        folder_name = backup_path.replace(':', '').replace('\\', '_').replace('/', '_')
        folder_name = re.sub(r'[<>|"?*]', '_', folder_name)  # 再保险地把剩余非法字符干掉
        folder_name = folder_name.strip('_')  # 去掉可能前后多余的下划线    
        backup_dir = os.path.join(BACKUP_ROOT, folder_name)
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        if os.path.isfile(backup_path):
            dst = os.path.join(backup_dir, "file_" + os.path.basename(backup_path))
            shutil.copy2(backup_path, dst)
            total_copied += 1
        else:
            # 文件夹：遍历所有文件进行增量判断
            for root, dirs, files in os.walk(backup_path):
                rel_root = os.path.relpath(root, backup_path)
                dst_root = os.path.join(backup_dir, rel_root) if rel_root != "." else backup_dir
                os.makedirs(dst_root, exist_ok=True)

                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(dst_root, file)  # 目标文件（无后缀版）

                    src_mtime = os.path.getmtime(src_file)                  # 源文件修改时间
                    src_time_str = datetime.fromtimestamp(src_mtime).strftime("%Y%m%d_%H%M%S")

                    should_copy = True
                    rename_old = False

                    if os.path.exists(dst_file):
                        dst_mtime = os.path.getmtime(dst_file)

                        if src_mtime > dst_mtime:
                            # 源文件更新的情况：覆盖最新版，旧版改名归档
                            rename_old = True
                            should_copy = True
                            print(f"检测到更新 → {file}（将归档旧版）")
                        elif src_mtime == dst_mtime:
                            # 修改时间完全一样，大概率内容一样 → 跳过（可加MD5再保险）
                            if get_file_hash(src_file) == get_file_hash(dst_file):
                                should_copy = False
                            else:
                                # 万一时间一样内容不同（极少见），也覆盖并归档旧版
                                rename_old = True
                                should_copy = True
                        else:
                            # 备份里的更新（源文件更旧）→ 不覆盖，但可以选择也复制一份新后缀版（可选）
                            should_copy = False

                    if should_copy:
                        if rename_old:
                            old_time = datetime.fromtimestamp(os.path.getmtime(dst_file)).strftime("%Y%m%d_%H%M%S")
                            name, ext = os.path.splitext(file)
                            new_name = f"{name}_old_{old_time}{ext}"
                            archived = os.path.join(dst_root, new_name)
                            n = 1
                            while os.path.exists(archived):
                                archived = os.path.join(dst_root, f"{name}_old_{old_time}_{n}{ext}")
                                n += 1
                            shutil.move(dst_file, archived)
                            shutil.copy2(src_file, dst_file)
                            file2backup_count += 1
                            print(f"归档旧版 → {new_name}")
                        else:
                            shutil.copy2(src_file, dst_file)
                            file2backup_count += 1
                            print(f"已备份 → {file}")
                    else:
                        print(f"无需更新 → {file}")
        print(f"备份完成位置: {os.path.abspath(backup_dir)}")
    print(f"备份完成！本次共复制 {file2backup_count} 个新/变更的文件")

if __name__ == "__main__":
    # 让窗口停留，便于看到结果
    print("U盘自动备份程序启动中...")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    AutoBackup()