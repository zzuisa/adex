import tkinter as tk
from tkinter import messagebox, filedialog, Button
import webbrowser
import subprocess
import os
import pypinyin
import re
from res.resources_manager import  RESOURCE_FILE
from PIL import Image, ImageTk
import json
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog

class SuggestionManager:
    def __init__(self, root, resources):
        self.root = root
        self.resources = resources
        self.suggestions = []
        self.search_res = resources

        # 创建一个 Frame 容器用于输入框和按钮
        self.input_frame = tk.Frame(self.root, bg="#ffffff")
        self.input_frame.pack(padx=10, pady=10, fill="x")

        # 输入框
        self.entry = tk.Entry(
            self.input_frame,
            font=("Arial", 16),
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#d0d0d0",
            bg="#ffffff",
            fg="#333333"
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=5)

        # 加载图标图片
        try:
            img = Image.open("./src/res/static/manage.png").resize((24, 24))  # 调整图标大小
            self.search_icon = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"加载图标失败: {e}")
            self.search_icon = None

        # 搜索管理按钮（图标）
        if self.search_icon:
            self.search_management_button = Button(
                self.input_frame,
                image=self.search_icon,
                command=self.open_search_management,
                borderwidth=0,
                bg="#ffffff",
                activebackground="#eaf4fc"
            )
        else:
            self.search_management_button = Button(
                self.input_frame,
                text="搜索管理",
                font=("Arial", 14),
                command=self.open_search_management,
                borderwidth=0,
                bg="#ffffff",
                activebackground="#eaf4fc"
            )

        self.search_management_button.pack(side="left", padx=(5, 0), pady=5)

        # 建议框
        self.suggestion_box = tk.Listbox(
            self.root,
            font=("Arial", 14),
            relief="flat",
            bd=0,
            highlightthickness=1,
            bg="#eaf4fc",
            fg="#333333",
            selectbackground="#cce7ff",
            selectforeground="#333333"
        )
        self.suggestion_box.pack(padx=10, pady=(0, 10), fill=tk.BOTH, ipady=10, expand=True)

        # 绑定事件
        self.suggestion_box.bind("<Double-1>", self.on_suggestion_select)
        self.root.bind("<Return>", self.execute_command)
        self.root.bind("<Down>", self.navigate_suggestions)
        self.root.bind("<Tab>", self.navigate_suggestions)
        self.root.bind("<Up>", self.select_previous_suggestion)
        self.entry.bind("<KeyRelease>", self.update_suggestions)

        # 初始化输入框
        self.entry.focus_set()
        self.entry.icursor(tk.END)
        self.entry.focus_force()
        self.entry.insert(0, 'open ')

        # 设置窗口无边框
        self.root.overrideredirect(True)
        self.root.after(50, self.update_suggestions)
        
    def pinyin_match(self, query, item):
        """使用拼音和汉字进行模糊匹配"""
        # 将中文项转换为拼音
        item_pinyin = ''.join([word[0] for word in pypinyin.pinyin(item, style=pypinyin.NORMAL)])
        
        # 使用正则表达式进行模糊匹配，忽略大小写
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        return bool(pattern.search(item_pinyin)) or bool(pattern.search(item)) 
    def navigate_suggestions(self, event):
        """根据 Tab 或 Down 键在 suggestions 列表中移动选择项"""
        if self.suggestion_box.size() > 0:
            current = self.suggestion_box.curselection()
            
            if event.keysym == "Tab":
                # Tab 键循环选择
                next_index = current[0] + 1 if current and current[0] < self.suggestion_box.size() - 1 else 0
            elif event.keysym == "Down":
                # Down 键顺序选择
                next_index = current[0] + 1 if current and current[0] < self.suggestion_box.size() - 1 else 0

            # 更新选择项
            self.suggestion_box.selection_clear(0, tk.END)
            self.suggestion_box.selection_set(next_index)
            self.suggestion_box.activate(next_index)

            # 更新 entry 显示的值为当前选中的建议项
            selected_suggestion = self.suggestion_box.get(next_index)
            self.entry.delete(0, tk.END)
            self.entry.insert(0, f"open {selected_suggestion}")

        return "break"  # 阻止默认 Tab 和 Down 键行为
    def select_previous_suggestion(self, event):
        """选择上一个提示项并更新 entry 显示的值"""
        if self.suggestion_box.size() > 0:
            current = self.suggestion_box.curselection()
            prev_index = (current[0] - 1) % self.suggestion_box.size() if current else self.suggestion_box.size() - 1
            self.suggestion_box.selection_clear(0, tk.END)
            self.suggestion_box.selection_set(prev_index)
            self.suggestion_box.activate(prev_index)

            # 更新 entry 显示的值为当前选中的建议项
            selected_suggestion = self.suggestion_box.get(prev_index)
            self.entry.delete(0, tk.END)
            self.entry.insert(0, f"open {selected_suggestion}")
   
    # def update_listbox():
    #     """更新 Listbox 显示内容"""
    #     self.resource_listbox.delete(0, tk.END)
    #     for name, info in resources.items():
    #         resource_listbox.insert(tk.END, f"{name} ({info['type']})")

    def handle_drop(self, event):
        """处理拖拽事件"""
        # 打印 event.data，调试时查看数据格式
        print("Dropped data:", event.data)
        raw_paths = event.data
        
        # 使用正则表达式智能拆分路径
        raw_paths = re.findall(r'\{[^}]*\}|\S+', raw_paths)
        print("Parsed paths:", raw_paths)

        for raw_path in raw_paths:
            if any(c in raw_path for c in '{}'):
                raw_path = raw_path.strip('{}')
            path = os.path.normpath(raw_path)  # 规范路径格式
            file_name = os.path.basename(path) 
            print("path:", path)
            if os.path.exists(path):
                if os.path.isfile(path):
                    # 如果是文件，直接添加
                    self.update_resource(file_name, path, "file")
                elif os.path.isdir(path):
                    # 如果是目录，递归添加目录下的所有文件
                    for root_dir, _, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root_dir, file)
                            self.update_resource(file_name, file_path, "file")
        self.update_listbox()  # 更新 Listbox 显示
    def open_search_management(self):
        """打开搜索管理页面"""

        # 创建弹窗
        search_management_window = tk.Toplevel(self.root)
        search_management_window.title("搜索管理")

        # 设置窗口大小和位置
        window_width = 400
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        x_position = (screen_width - window_width) // 2 + window_width
        y_position = 100
        search_management_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # 搜索框和标签
        search_label = tk.Label(search_management_window, text="搜索:", font=("Arial", 12))
        search_label.pack(anchor=tk.W, padx=10, pady=(10, 0))
        search_entry = tk.Entry(search_management_window, font=("Arial", 14))
        search_entry.pack(padx=10, pady=5, fill=tk.X)

        # 创建资源列表框和滚动条的容器
        listbox_frame = tk.Frame(search_management_window)
        listbox_frame.pack(padx=10, pady=(5, 10), fill=tk.BOTH, expand=True)

        # 创建滚动条
        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 显示当前资源列表
        resource_listbox = tk.Listbox(
            listbox_frame,
            width=40,
            font=("Arial", 14),
            relief="flat",
            bd=0,
            highlightthickness=1,
            bg="#eaf4fc",
            fg="#333333",
            selectbackground="#cce7ff",
            selectforeground="#333333",
            yscrollcommand=scrollbar.set  # 绑定滚动条
        )
        resource_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=resource_listbox.yview)  # 滚动条控制列表框的视图

        # 填充已有资源到列表
        def update_resource_list(search_query=""):
            """根据搜索查询更新资源列表"""
            resource_listbox.delete(0, tk.END)
            for name in self.resources:
                if search_query.lower() in name.lower():  # 支持不区分大小写的模糊匹配
                    resource_listbox.insert(tk.END, name)

        update_resource_list()  # 初始显示所有资源

        # 资源列表选择事件：启用删除按钮
        def on_select(event):
            cur = resource_listbox.curselection()
            print()
            if cur:
                k = resource_listbox.get(cur)
                v = self.resources[k]
                name_entry.delete(0, tk.END)
                name_entry.insert(0,k)
                path_entry.delete(0, tk.END)
                path_entry.insert(0,v['path'])
                type_entry.delete(0, tk.END) 
                type_entry.insert(0,v['type'])
                # selection = self.suggestion_box.get(self.suggestion_box.curselection())
                # self.entry.insert(tk.END, f"open {selection}")
                if resource_listbox.curselection():
                    remove_button.config(state="normal")  # 启用删除按钮
                else:
                    remove_button.config(state="disabled")  # 禁用删除按钮
                
        # 搜索框绑定实时更新事件
        search_entry.bind("<KeyRelease>", lambda event: update_resource_list(search_entry.get()))

        # 输入框，允许用户输入资源的名称、路径和类型
        name_label = tk.Label(search_management_window, text="资源名称:", font=("Arial", 12))
        name_label.pack(anchor=tk.W, padx=10, pady=(10, 0))
        name_entry = tk.Entry(search_management_window, font=("Arial", 14))
        name_entry.pack(padx=10, pady=5, fill=tk.X)

        path_label = tk.Label(search_management_window, text="资源路径:", font=("Arial", 12))
        path_label.pack(anchor=tk.W, padx=10, pady=(10, 0))

        # 创建资源路径输入框和浏览按钮的容器
        path_frame = tk.Frame(search_management_window)
        path_frame.pack(padx=10, pady=5, fill=tk.X)

        path_entry = tk.Entry(path_frame, font=("Arial", 14))
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def browse_file():
            """弹出文件选择对话框"""
            file_path = filedialog.askopenfilename(title="选择文件", filetypes=[("所有文件", "*.*")])
            if file_path:  # 如果选择了文件
                path_entry.delete(0, tk.END)  # 清空输入框
                path_entry.insert(0, file_path)  # 填入文件路径

        browse_button = tk.Button(
            path_frame,
            text="浏览",
            font=("Arial", 12),
            command=browse_file
        )
        browse_button.pack(side=tk.LEFT, padx=(5, 0))

        type_label = tk.Label(search_management_window, text="资源类型:", font=("Arial", 12))
        type_label.pack(anchor=tk.W, padx=10, pady=(10, 0))
        type_entry = tk.Entry(search_management_window, font=("Arial", 14))
        type_entry.pack(padx=10, pady=5, fill=tk.X)

        # 新增、删除和关闭按钮放在同一行
        button_frame = tk.Frame(search_management_window)
        button_frame.pack(padx=10, pady=10, fill=tk.X)

        add_button = tk.Button(
            button_frame,
            text="更新资源",
            font=("Arial", 14),
            command=lambda: self.on_update_resource(name_entry, path_entry, type_entry)
        )
        add_button.pack(side=tk.LEFT, padx=5)

        remove_button = tk.Button(
            button_frame,
            text="删除资源",
            font=("Arial", 14),
            state="disabled",
            command=lambda: self.on_remove_resource(resource_listbox)
        )
        remove_button.pack(side=tk.LEFT, padx=5)

        close_button = tk.Button(
            button_frame,
            text="关闭",
            font=("Arial", 14),
            command=search_management_window.destroy
        )
        close_button.pack(side=tk.LEFT, padx=5)
        resource_listbox.bind("<<ListboxSelect>>", on_select)
        self.resource_listbox = resource_listbox
        
    def save_resources(self):
        """保存资源配置到 JSON 文件"""
        with open(RESOURCE_FILE, "w", encoding="utf-8") as file:
            json.dump(self.resources, file, ensure_ascii=False, indent=4)
    
    def update_resource(self, name, path, resource_type):
        """新增资源配置"""
        self.resources[name] = {"path": path, "type": resource_type}
        self.save_resources()
        self.update_resources_list()
    
    def remove_resource(self, name):
        """删除资源配置"""
        if name in self.resources:
            del self.resources[name]
            self.save_resources()
            self.update_resources_list()
        else:
            messagebox.showerror("错误", f"资源 '{name}' 不存在！")

    def update_resources_list(self):
        """更新 UI 中的资源列表显示"""
        self.resource_listbox.delete(0, tk.END)
        for name in self.resources:
            self.resource_listbox.insert(tk.END, name)
             
    def on_update_resource(self, name_entry, path_entry, type_entry):
        """处理新增资源按钮点击事件"""
        name = name_entry.get()
        path = path_entry.get()
        type = type_entry.get()
        
        if not name or not path or not type:
            messagebox.showerror("错误", "请输入完整的资源信息！")
            return
        self.update_resource(name, path, type)
        name_entry.delete(0, tk.END)
        path_entry.delete(0, tk.END)
        type_entry.delete(0, tk.END)

    def on_remove_resource(self, resource_listbox):
        """处理删除资源按钮点击事件"""
        selected_resource = resource_listbox.curselection()
        if not selected_resource:
            tk.messagebox.showerror("错误", "请选择要删除的资源！")
            return
        resource_name = resource_listbox.get(selected_resource[0])
        del self.resources[resource_name]
        self.save_resources()
        resource_listbox.delete(selected_resource[0])  # 从列表框中移除


    def update_suggestions(self, event=None):
        """Update suggestion list based on input, excluding function keys and allowing Ctrl+A."""
        if event is not None:
            if event.keysym == "space":
                plain_value = self.entry.get().strip().replace('open','').replace('url','')
                if len(plain_value) > 0 and len(self.suggestions) > 0:
                    self.search_res = self.suggestions
            
            if event.state & 0x0004 and event.keysym == "BackSpace":
                self.entry.delete(0, tk.END)
                self.entry.insert(0, f"open ")
                return

            if event.state & 0x0004 and event.keysym in ("c", "v", "x", "a") or (event.state & 0x0004 and event.keysym == "a"):
                return  # Exclude Ctrl+C, Ctrl+V, Ctrl+X, Ctrl+A
        
            if event.keysym in ("Up", "Down", "Control_L", "Shift_L", "Shift_R", "Control_R", "Alt_L", "Alt_R"):
                return  
        if len(self.suggestions) == 0:
            self.search_res = self.resources

        query = self.entry.get().strip().lower()
        query_key = query.replace('open','').replace('url','').split(' ')[-1]
        if query_key.strip() == '':
            self.search_res = self.resources

        self.suggestion_box.delete(0, tk.END)

        if query.startswith("open"):
            self.suggestions = [key for key in self.search_res if self.pinyin_match(query_key,key.lower())]
        elif query.startswith("url"):
            query = query.replace('open','').replace('url','').strip()
            self.suggestions = [key for key, value in self.resources.items() if value[1] == "url" and  self.pinyin_match(query_key,key.lower())]
        else:
            self.suggestions = [key for key in self.search_res if query_key in key.lower()]

        for suggestion in self.suggestions:
            self.suggestion_box.insert(tk.END, suggestion)

    def on_suggestion_select(self, event=None):
        """Execute the command when a suggestion is selected."""
        selection = self.suggestion_box.get(self.suggestion_box.curselection())
        self.entry.delete(0, tk.END)
        self.entry.insert(tk.END, f"open {selection}")
        self.execute_command(event)

    def execute_command(self, event=None):
        command = self.entry.get().strip()
        
        if any(command.startswith(cmd) for cmd in ["open", "url"]):
            resource_key = command.replace("open",'').replace("url",'').strip()
            if resource_key in self.resources.keys():
                resource_path, resource_type = self.resources[resource_key].values()
                try:
                    if resource_type == "file":
                        os.startfile(resource_path)
                    elif resource_type == "url":
                        webbrowser.open(resource_path)
                except Exception as e:
                    messagebox.showerror("Open Error", str(e))
            else:
                messagebox.showwarning("Not Found", "Resource not found.")
        elif command.startswith(">"):
            cmd = command[1:].strip()
            try:
                output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
                messagebox.showinfo("Command Output", output)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Command Error", e.output)
        else:
            messagebox.showwarning("Invalid Command", "Invalid command. Please enter 'open <resource name>'.")

        self.entry.delete(0, tk.END)
        self.suggestion_box.delete(0, tk.END)
        self.root.withdraw()

    def set_entry_widget(self, entry_widget):
        """Method to set the entry widget from the main app."""
        self.entry = entry_widget
