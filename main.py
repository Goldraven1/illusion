import tkinter as tk
from login_window import LoginWindow
from test_selection_window import TestSelectionWindow
from test_window import PoggendorffIllusion ,Vector2D

class App:
    def __init__(self, root):
        self.root = root
        self.show_login_window()

    def show_login_window(self):
        self.clear_window()
        self.login_window = LoginWindow(self.root, self.show_test_selection_window)

    def show_test_selection_window(self):
        self.clear_window()
        self.test_selection_window = TestSelectionWindow(self.root, self.show_test_window)

    def show_test_window(self, test_type):
        self.clear_window()
        self.test_window = PoggendorffIllusion(self.root, user_id=1)  # Передаем только root и user_id
        self.test_window.pack(fill='both', expand=True)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
