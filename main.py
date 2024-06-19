# main.py

import tkinter as tk
from login_window import LoginWindow
from test_selection_window import TestSelectionWindow
from result_window import ResultsWindow
from test_window import PoggendorffIllusion
from verticalhorisonatl import VerticalHorizontalIllusion
from muller_lyer_illusion import MullerLyerIllusion
from database import Database
from configt import DB_CONFIG

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Иллюзии")
        self.db = Database(DB_CONFIG)
        self.show_login_window()

    def show_login_window(self):
        self.clear_window()
        self.login_window = LoginWindow(self.root, self.show_test_selection_window)

    def show_test_selection_window(self, user_id, is_admin=False):
        self.clear_window()
        TestSelectionWindow(self.root, self.show_test_window, self.show_results_window, user_id, is_admin)

    def show_test_window(self, test_name, user_id, is_admin=False):
        self.clear_window()
        if test_name == "Poggendorff":
            PoggendorffIllusion(self.root, self, user_id, is_admin)
        elif test_name == "VerticalHorizontal":
            VerticalHorizontalIllusion(self.root, self, user_id, is_admin)
        elif test_name == "MullerLyer":
            MullerLyerIllusion(self.root, self, user_id, is_admin)
        else:
            tk.messagebox.showerror("Ошибка", "Неизвестный тип теста")

    def show_results_window(self, user_id):
        self.clear_window()
        ResultsWindow(self.root, self, user_id)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# Пример использования
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1920x1080")  # Устанавливаем размеры окна
    app = App(root)
    root.mainloop()
