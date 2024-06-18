import tkinter as tk
from tkinter import messagebox
import config

class LoginWindow:
    def __init__(self, root, next_window_callback):
        self.root = root
        self.next_window_callback = next_window_callback
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Фамилия:").grid(row=0, column=0)
        self.surname_entry = tk.Entry(self.root)
        self.surname_entry.grid(row=0, column=1)

        tk.Label(self.root, text="Имя:").grid(row=1, column=0)
        self.name_entry = tk.Entry(self.root)
        self.name_entry.grid(row=1, column=1)

        tk.Label(self.root, text="Отчество:").grid(row=2, column=0)
        self.patronymic_entry = tk.Entry(self.root)
        self.patronymic_entry.grid(row=2, column=1)

        tk.Label(self.root, text="Пол:").grid(row=3, column=0)
        self.gender_entry = tk.Entry(self.root)
        self.gender_entry.grid(row=3, column=1)

        tk.Label(self.root, text="Возраст:").grid(row=4, column=0)
        self.age_entry = tk.Entry(self.root)
        self.age_entry.grid(row=4, column=1)

        tk.Button(self.root, text="Далее", command=self.next_window).grid(row=5, column=1)
        tk.Button(self.root, text="Настройки", command=self.show_admin_settings).grid(row=5, column=0)

    def next_window(self):
        if self.validate_entries():
            self.next_window_callback()
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")

    def validate_entries(self):
        return all([self.surname_entry.get(), self.name_entry.get(), self.patronymic_entry.get(), self.gender_entry.get(), self.age_entry.get()])

    def show_admin_settings(self):
        self.admin_window = tk.Toplevel(self.root)
        self.admin_window.title("Настройки администратора")

        tk.Label(self.admin_window, text="Логин:").grid(row=0, column=0)
        self.login_entry = tk.Entry(self.admin_window)
        self.login_entry.grid(row=0, column=1)

        tk.Label(self.admin_window, text="Пароль:").grid(row=1, column=0)
        self.password_entry = tk.Entry(self.admin_window, show="*")
        self.password_entry.grid(row=1, column=1)

        tk.Button(self.admin_window, text="Войти", command=self.validate_admin).grid(row=2, column=1)

    def validate_admin(self):
        login = self.login_entry.get()
        password = self.password_entry.get()
        if login == config.ADMIN_LOGIN and password == config.ADMIN_PASSWORD:
            messagebox.showinfo("Успех", "Вы вошли в режим настроек.")
            self.admin_window.destroy()
        else:
            messagebox.showerror("Ошибка", "Неправильный логин или пароль.")
