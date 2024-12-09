import tkinter as tk
from tkinter import messagebox
import webbrowser
import subprocess
import os

class SuggestionManager:
    def __init__(self, root, entry, resources):
        self.root = root
        self.resources = resources
        self.suggestions = []
        self.entry = entry
        self.search_res = resources

        # Create suggestion_box within the class
        self.suggestion_box = tk.Listbox(
            root,
            font=("Arial", 14),
            relief="flat",
            bd=0,
            highlightthickness=1,
            bg="#eaf4fc",
            fg="#333333",
            selectbackground="#cce7ff",
            selectforeground="#333333"
        )
        
        self.suggestion_box.pack(padx=10, pady=(0, 10), fill=tk.BOTH, ipady=5)
        self.suggestion_box.bind("<Double-1>", self.on_suggestion_select)
        
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
                print('!!!')
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
            self.suggestions = [key for key in self.search_res if query_key in key.lower()]
        elif query.startswith("url"):
            query = query.replace('open','').replace('url','').strip()
            self.suggestions = [key for key, value in self.resources.items() if value[1] == "url" and query_key in key.lower()]
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
