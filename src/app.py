import tkinter as tk
from res.resources_manager import load_and_process_resources
from service.suggestion_manager import SuggestionManager
import keyboard

class Adex:
    def center_top_window(self):
        """将窗口置于屏幕上方并留出一些空隙"""
        window_width = 400
        window_height = 400
        screen_width = self.root.winfo_screenwidth()
        x_position = (screen_width - window_width) // 2
        y_position = 100  
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    def __init__(self, root):
        self.root = root
        self.suggestions = []
        self.lock = False
        self.resources = load_and_process_resources()
        self.root.title("Adex App")
        self.root.configure(bg="#f0f0f0")  
        self.root.attributes("-topmost", True)

        self.center_top_window()
        self.root.overrideredirect(True)
        self.suggestion_manager = SuggestionManager(self.root, self.resources)
        keyboard.add_hotkey("ctrl+alt+space", self.toggle_visibility)

        
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
        self.suggestion_manager.entry.focus_set()
        self.suggestion_manager.entry.icursor(tk.END)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = Adex(root)
    root.mainloop()