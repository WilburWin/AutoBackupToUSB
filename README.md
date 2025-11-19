# AutoBackupToUSB - 自动备份文件到 U 盘工具

一个简单实用的 Python 工具，帮助你把电脑上的重要文件夹自动备份到 U 盘，支持增量备份、旧版本自动归档，带图形化配置工具，使用非常方便。

## 功能特点

- 完全离线运行，无需安装任何软件
- 将 `AutoBackup.exe` 和 `ConfigTool.exe` 直接放在 U 盘根目录，即插即用
- 自动生成配置文件 `backup_paths.txt`，一行一个需要备份的文件夹路径
- 自动在 U 盘创建 `backups` 文件夹，所有备份内容存放在这里
- 备份文件夹以原始完整路径命名（路径中的 `\` 会自动转为 `_`，避免冲突）
- 检测到已有备份时，旧文件会自动重命名为 `xxx_old_YYYYMMDD_HHMMSS` 归档保留
- 提供 `ConfigTool.exe` 图形化配置工具，一键添加/删除备份路径，适合小白使用

## 使用方法（最简单版）

1. 把仓库中的 `AutoBackup.exe` 和 `ConfigTool.exe` 复制到你的 U 盘根目录
2. 插入 U 盘，双击 `ConfigTool.exe`  
   → 点击「添加文件夹」选择需要备份的目录 → 保存退出
3. 以后每次插入 U 盘，双击 U 盘里的 `AutoBackup.exe` 即可一键备份
4. 备份内容会出现在 U 盘的 `backups` 文件夹中

## 文件结构示例
```bash
├─ AutoBackup.exe          ← 双击运行备份
├─ ConfigTool.exe          ← 图形化配置工具
├─ backup_paths.txt        ← 自动生成，保存需要备份的路径
└─ backups/                ← 自动生成，所有备份放在这里
   ├─ C_Users_YourName_Documents/
   ├─ D_Work_Projects/
   └─ ...

> 小技巧：把 `AutoBackup.exe` 快捷方式放到电脑桌面，每次想备份时直接拖 U 盘图标到快捷方式上也能运行（Windows 支持）

## 自己打包生成 exe（开发者/进阶用户）

```bash
# 1. 克隆仓库（或直接下载 AutoBackup.py 和 ConfigTool.py）
git clone https://github.com/yourname/AutoBackupToUSB.git
cd AutoBackupToUSB

# 2. 安装打包工具
pip install pyinstaller

# 3. 打包（会生成 dist 文件夹，里面就是 exe）
pyinstaller --onefile --name AutoBackup.exe AutoBackup.py
pyinstaller --onefile --windowed --name ConfigTool.exe ConfigTool.py

# 4. 把生成的 dist/AutoBackup.exe 和 dist/ConfigTool.exe 复制到 U 盘根目录即可

