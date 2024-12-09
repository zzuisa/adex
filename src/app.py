import tkinter as tk
from res.resources_manager import load_and_process_resources, RESOURCE_FILE
from service.suggestion_manager import SuggestionManager
import keyboard
import json

class Adex:
    def center_top_window(self):
        """将窗口置于屏幕上方并留出一些空隙"""
        window_width = 400
        window_height = 800
        screen_width = self.root.winfo_screenwidth()
        x_position = (screen_width - window_width) // 2
        y_position = 50  
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    def __init__(self, root):
        self.root = root
        self.suggestions = []
        self.lock = False
        self.resources = load_and_process_resources()
        self.resources_file = RESOURCE_FILE  # 资源文件路径
        self.root.title("Adex App")
        self.root.configure(bg="#f0f0f0")  
        self.root.attributes("-topmost", True)

        self.center_top_window()
        self.root.overrideredirect(True)
        # 创建 UI 控件
        self.create_ui()
        # 输入框
        self.entry = tk.Entry(
            root, 
            font=("Arial", 16), 
            relief="flat", 
            bd=0, 
            highlightthickness=1, 
            highlightbackground="#d0d0d0",  
            bg="#ffffff",  
            fg="#333333"  
        )
        self.entry.pack(padx=10, pady=10, fill=tk.BOTH, ipady=5)
        self.suggestion_manager = SuggestionManager(self.root, self.entry, self.resources)
        self.root.bind("<Return>", self.suggestion_manager.execute_command)
        self.root.bind("<Down>", self.suggestion_manager.navigate_suggestions)
        self.root.bind("<Tab>", self.suggestion_manager.navigate_suggestions)
        self.root.bind("<Up>", self.suggestion_manager.select_previous_suggestion)
        self.entry.bind("<KeyRelease>", self.suggestion_manager.update_suggestions)
        self.entry.focus_set()
        self.entry.icursor(tk.END)
        self.entry.focus_force()
        self.entry.insert(0,'open ')
        self.root.after(50,self.suggestion_manager.update_suggestions)
        
        
        keyboard.add_hotkey("ctrl+alt+space", self.toggle_visibility)
        
    def load_resources(self):
        """从 JSON 文件加载资源配置"""
        try:
            with open(self.resources_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}  # 如果文件不存在，返回空字典
        except json.JSONDecodeError:
            return {}  # 如果文件内容格式不正确，返回空字典
    
    def save_resources(self):
        """保存资源配置到 JSON 文件"""
        with open(self.resources_file, "w", encoding="utf-8") as file:
            json.dump(self.resources, file, ensure_ascii=False, indent=4)
    
    def add_resource(self, name, path, resource_type):
        """新增资源配置"""
        if name in self.resources:
            messagebox.showerror("错误", f"资源 '{name}' 已存在！")
            return
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
        
    def toggle_visibility(self):
        if self.lock:
            return
        self.lock = True
        if self.root.state() == "withdrawn":
            self.root.deiconify()
            self.root.lift()
            self.root.after(30, self.activate_entry_with_focus)
        else:
            self.root.withdraw()
        self.root.after(500, lambda: setattr(self, 'lock', False))  # 防止重复触发

            
    def activate_entry_with_focus(self):
        self.root.focus_force()
        keyboard.send("alt")
        self.entry.focus_set()
        self.entry.icursor(tk.END)
        
    def create_ui(self):
        # 显示当前资源列表
        self.resource_listbox = tk.Listbox(self.root, width=40, height=10)
        self.resource_listbox.pack(padx=10, pady=10)
        self.update_resources_list()  # 加载现有资源

        # 输入框，允许用户输入资源的名称、路径和类型
        self.name_entry = tk.Entry(self.root, font=("Arial", 14))
        self.name_entry.pack(padx=10, pady=5)
        self.name_entry.insert(0, "输入资源名称")

        self.path_entry = tk.Entry(self.root, font=("Arial", 14))
        self.path_entry.pack(padx=10, pady=5)
        self.path_entry.insert(0, "输入资源路径")

        self.type_entry = tk.Entry(self.root, font=("Arial", 14))
        self.type_entry.pack(padx=10, pady=5)
        self.type_entry.insert(0, "输入资源类型")

        # 新增资源按钮
        self.add_button = tk.Button(self.root, text="新增资源", font=("Arial", 14), command=self.on_add_resource)
        self.add_button.pack(padx=10, pady=10)

        # 删除资源按钮
        self.remove_button = tk.Button(self.root, text="删除资源", font=("Arial", 14), command=self.on_remove_resource)
        self.remove_button.pack(padx=10, pady=10)

    def on_add_resource(self):
        """处理新增资源按钮点击事件"""
        name = self.name_entry.get().strip()
        path = self.path_entry.get().strip()
        resource_type = self.type_entry.get().strip()
        
        if not name or not path or not resource_type:
            messagebox.showerror("错误", "请输入完整的资源信息！")
            return
        
        self.add_resource(name, path, resource_type)
        self.name_entry.delete(0, tk.END)
        self.path_entry.delete(0, tk.END)
        self.type_entry.delete(0, tk.END)

    def on_remove_resource(self):
        """处理删除资源按钮点击事件"""
        selected_resource = self.resource_listbox.curselection()
        if not selected_resource:
            messagebox.showerror("错误", "请选择要删除的资源！")
            return
        resource_name = self.resource_listbox.get(selected_resource[0])
        self.remove_resource(resource_name)

        
if __name__ == "__main__":
    root = tk.Tk()
    app = Adex(root)
    root.mainloop()
    
    
    
