使用python语言编写了一个自动备份文件到U盘的程序
将AutoBackup.exe和ConfigTool.exe放在U盘根目录
将自动生成backup_paths.txt配置文件，需要备份的文件目录在这里
将自动生成backups文件夹，备份的文件夹都在这里，备份的文件夹将以自身路径为文件夹名

AutoBackup.exe实现了自动备份，旧备份文件将被归档增加【_old_旧修改时间】文件名后缀
ConfigTool.exe增加了GUI界面，操作更加直观友好

pip install pyinstaller
pyinstaller --onefile --name AutoBackup.exe AutoBackup.py
pyinstaller --onefile --windowed --name ConfigTool.exe ConfigTool.py
