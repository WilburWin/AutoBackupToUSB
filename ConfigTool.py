# ConfigTool.py 
'''
U盘自动备份神器 v1.0
1. 自动备份指定目录下的所有文件到 U 盘
2. 自动归档旧版文件
3. 自动更新备份列表
4. 界面友好，用户体验好
'''
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar, END, ttk
import os
import re
import shutil
import hashlib
from datetime import datetime
import threading

CONFIG_FILE = "backup_paths.txt"
BACKUP_ROOT = "backups"

# ====================== 备份核心函数 ======================
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
            paths = [line.strip() for line in f if line.strip()]
    return paths

def save_paths_to_file(paths):
    """全局保存函数"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        for p in paths:
            if p.strip():
                f.write(p.strip() + "\n")

def count_total_files(paths):
    """提前统计所有要处理的文件总数（用于进度条）"""
    total = 0
    for p in paths:
        if not os.path.exists(p):
            continue
        if os.path.isfile(p):
            total += 1
        else:
            for _, _, files in os.walk(p):
                total += len(files)
    return total

def do_backup(update_callback):
    paths = load_backup_paths()
    if not paths:
        update_callback("错误：没有配置备份路径！")
        messagebox.showerror("备份失败", "没有找到任何备份路径，请先添加。")
        return False

    if not os.path.exists(BACKUP_ROOT):
        os.makedirs(BACKUP_ROOT)

    total_files = count_total_files(paths)
    if total_files == 0:
        update_callback("没有发现任何文件可备份")
        return True

    update_callback(f"发现 {total_files} 个文件，开始备份...")
    copied_count = 0
    all_count =0
    for backup_path in paths:
        if not os.path.exists(backup_path):
            update_callback(f"跳过不存在：{backup_path}")
            continue

        # 路径 → 文件夹名（安全）
        folder_name = backup_path.replace(':', '').replace('\\', '_').replace('/', '_')
        folder_name = re.sub(r'[<>|"?*]', '_', folder_name).strip('_')
        if not folder_name:
            folder_name = "备份路径"
        backup_dir = os.path.join(BACKUP_ROOT, folder_name)
        os.makedirs(backup_dir, exist_ok=True)

        update_callback(f"正在备份 → {os.path.basename(backup_path) or backup_path}")

        if os.path.isfile(backup_path):
            dst_file = os.path.join(backup_dir, os.path.basename(backup_path))
            if not os.path.exists(dst_file) or get_file_hash(backup_path) != get_file_hash(dst_file):
                shutil.copy2(backup_path, dst_file)
                copied_count += 1
                all_count    += 1
                update_callback(f"已复制：{os.path.basename(backup_path)}")
        else:
            for root, _, files in os.walk(backup_path):
                rel_root = os.path.relpath(root, backup_path)
                dst_root = os.path.join(backup_dir, rel_root) if rel_root != "." else backup_dir
                os.makedirs(dst_root, exist_ok=True)

                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(dst_root, file)

                    should_copy = True
                    rename_old = False

                    if os.path.exists(dst_file):
                        src_mtime = os.path.getmtime(src_file)
                        dst_mtime = os.path.getmtime(dst_file)

                        if src_mtime > dst_mtime :
                            rename_old = True
                        elif get_file_hash(src_file) == get_file_hash(dst_file):
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
                            copied_count += 1
                            all_count    += 1
                            update_callback(f"归档旧版 → {new_name}")
                        else:
                            shutil.copy2(src_file, dst_file)
                            copied_count += 1
                            all_count    += 1
                            update_callback(f"已备份 → {file}")
                    else:
                        all_count    += 1
                        update_callback(f"无需更新 → {file}")

                    # 实时更新进度条
                    current_progress = int((all_count / total_files) * 100)
                    app.progress["value"] = current_progress
                    app.update_status(f"备份中... {copied_count}/{total_files} 文件 ({current_progress}%)")

    update_callback(f"备份完成！本次新增备份/归档旧版共 {copied_count} 个文件")
    messagebox.showinfo("成功", f"备份完成！\n本次处理了 {copied_count} 个文件")
    return True

# ====================== GUI 主程序 ======================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("U盘自动备份神器 v1.0")
        self.root.geometry("600x900")
        self.root.minsize(600, 900)

        self.paths = load_backup_paths()

        # 标题
        tk.Label(root, text="U盘自动备份工具", font=("微软雅黑", 18, "bold"), fg="#0066CC").pack(pady=15)

        # 路径列表
        list_frame = tk.Frame(root)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.listbox = Listbox(list_frame, yscrollcommand=scrollbar.set, font=("微软雅黑", 11), height=12)
        self.listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        for p in self.paths:
            self.listbox.insert(END, p)

        # 按钮区
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill="x", padx=20, pady=8)

        tk.Button(btn_frame, text="添加文件夹", width=12, command=self.add_folder).pack(side="left", padx=5)
        tk.Button(btn_frame, text="添加文件", width=12, command=self.add_file).pack(side="left", padx=5)
        tk.Button(btn_frame, text="删除选中", width=12, bg="#FF4444", fg="white", command=self.remove_selected).pack(side="left", padx=5)

        # 立即备份大按钮
        self.backup_btn = tk.Button(root, text="立即开始备份", font=("微软雅黑", 18, "bold"),
                                    bg="#00AA00", fg="white", height=2, command=self.start_backup)
        self.backup_btn.pack(fill="x", padx=60, pady=20)

        # 进度条
        self.progress = ttk.Progressbar(root, mode='determinate', length=600)
        self.progress.pack(fill="x", padx=60, pady=5)

        # 实时日志文本框（最重要！所有 print 都在这里显示）
        log_frame = tk.LabelFrame(root, text="备份日志", font=("微软雅黑", 10, "bold"))
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.log_text = tk.Text(log_frame, height=10, state='disabled', font=("Consolas", 10))
        log_scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=log_scroll.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scroll.pack(side="right", fill="y")

        # 状态栏
        self.status_label = tk.Label(root, text="就绪", relief="sunken", anchor="w", font=("微软雅黑", 9))
        self.status_label.pack(fill="x", side="bottom")

        # 保存并关闭按钮
        tk.Button(root, text="保存配置并关闭", width=20, bg="#0066CC", fg="white", command=self.save_and_exit).pack(pady=10)

    def log(self, message):
        """把所有输出集中到日志框"""
        self.log_text.config(state='normal')
        self.log_text.insert(END, message + "\n")
        self.log_text.see(END)
        self.log_text.config(state='disabled')
        self.root.update_idletasks()

    def update_status(self, text):
        self.status_label.config(text=text)

    def save_paths(self):
        self.paths = [self.listbox.get(i) for i in range(self.listbox.size())]
        save_paths_to_file(self.paths)

    def add_folder(self):
        path = filedialog.askdirectory(title="选择要备份的文件夹")
        if path and path not in self.paths:
            self.paths.append(path)
            self.listbox.insert(END, path)
            self.save_paths()

    def add_file(self):
        path = filedialog.askopenfilename(title="选择要备份的文件")
        if path and path not in self.paths:
            self.paths.append(path)
            self.listbox.insert(END, path)
            self.save_paths()

    def remove_selected(self):
        sel = self.listbox.curselection()
        if sel:
            idx = sel[0]
            self.listbox.delete(idx)
            self.paths.pop(idx)
            self.save_paths()

    def save_and_exit(self):
        self.save_paths()
        messagebox.showinfo("保存成功", "配置已保存到 backup_paths.txt")
        self.root.quit()

    def start_backup(self):
        # 第一步：强制保存最新配置
        self.save_paths()

        paths = load_backup_paths()
        if not paths:
            messagebox.showwarning("无路径", "请先添加要备份的文件夹或文件！")
            return

        # 禁用按钮 + 清空日志
        self.backup_btn.config(state="disabled", text="备份进行中...")
        self.progress["value"] = 0
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, END)
        self.log_text.config(state='disabled')
        self.update_status("准备备份...")

        # 用线程运行备份，防止界面卡死
        def run():
            global app  # 为了在 do_backup 里能更新进度条
            app = self
            do_backup(self.log)  # 把 log 函数传进去当 callback

            # 完成后恢复按钮
            self.root.after(0, lambda: self.backup_btn.config(state="normal", text="立即开始备份"))
            self.root.after(0, lambda: self.update_status("备份完成，就绪"))

        threading.Thread(target=run, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()