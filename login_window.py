import tkinter as tk
from tkinter import messagebox
from database import Database
from config import config
from configt import DB_CONFIG

class LoginWindow:
    def __init__(self, root, next_window_callback):
        self.root = root
        self.next_window_callback = next_window_callback
        self.db = Database(DB_CONFIG)
        self.db.create_tables()  # Убедитесь, что таблицы создаются при инициализации
        self.is_admin = False  # Локальная переменная для отслеживания состояния администратора
        self.create_widgets()

    def create_widgets(self):
        self.frame = tk.Frame(self.root)
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(self.frame, text="Фамилия:", font=('Helvetica', 18)).grid(row=0, column=0, padx=10, pady=10)
        self.surname_entry = tk.Entry(self.frame, font=('Helvetica', 18))
        self.surname_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.frame, text="Имя:", font=('Helvetica', 18)).grid(row=1, column=0, padx=10, pady=10)
        self.name_entry = tk.Entry(self.frame, font=('Helvetica', 18))
        self.name_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.frame, text="Отчество:", font=('Helvetica', 18)).grid(row=2, column=0, padx=10, pady=10)
        self.patronymic_entry = tk.Entry(self.frame, font=('Helvetica', 18))
        self.patronymic_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(self.frame, text="Пол:", font=('Helvetica', 18)).grid(row=3, column=0, padx=10, pady=10)
        self.gender_var = tk.StringVar()
        self.gender_entry = tk.OptionMenu(self.frame, self.gender_var, "Мужской", "Женский")
        self.gender_entry.config(font=('Helvetica', 18))
        self.gender_entry.grid(row=3, column=1, padx=10, pady=10)

        tk.Label(self.frame, text="Возраст:", font=('Helvetica', 18)).grid(row=4, column=0, padx=10, pady=10)
        self.age_entry = tk.Entry(self.frame, font=('Helvetica', 18))
        self.age_entry.grid(row=4, column=1, padx=10, pady=10)

        tk.Button(self.frame, text="Далее", command=self.next_window, font=('Helvetica', 18)).grid(row=5, column=1, padx=10, pady=20)
        tk.Button(self.frame, text="Настройки", command=self.show_admin_settings, font=('Helvetica', 18)).grid(row=5, column=0, padx=10, pady=20)

    def next_window(self):
        if self.validate_entries():
            surname = self.surname_entry.get()
            name = self.name_entry.get()
            patronymic = self.patronymic_entry.get()
            gender = self.gender_var.get()
            age = int(self.age_entry.get())
            user_id = self.db.insert_user(surname, name, patronymic, gender, age)
            self.next_window_callback(user_id, self.is_admin)
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")

    def validate_entries(self):
        return all([self.surname_entry.get(), self.name_entry.get(), self.patronymic_entry.get(), self.gender_var.get(), self.age_entry.get()])

    def show_admin_settings(self):
        self.admin_window = tk.Toplevel(self.root)
        self.admin_window.title("Настройки администратора")

        tk.Label(self.admin_window, text="Логин:", font=('Helvetica', 18)).grid(row=0, column=0, padx=10, pady=10)
        self.login_entry = tk.Entry(self.admin_window, font=('Helvetica', 18))
        self.login_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.admin_window, text="Пароль:", font=('Helvetica', 18)).grid(row=1, column=0, padx=10, pady=10)
        self.password_entry = tk.Entry(self.admin_window, show="*", font=('Helvetica', 18))
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(self.admin_window, text="Войти", command=self.validate_admin, font=('Helvetica', 18)).grid(row=2, column=1, padx=10, pady=20)

    def validate_admin(self):
        login = self.login_entry.get()
        password = self.password_entry.get()
        if login == config["ADMIN_LOGIN"] and password == config["ADMIN_PASSWORD"]:
            messagebox.showinfo("Успех", "Вы вошли в режим настроек.")
            self.is_admin = True
            self.admin_window.destroy()
        else:
            messagebox.showerror("Ошибка", "Неправильный логин или пароль.")

# Пример использования
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1920x1080")  # Устанавливаем размеры окна
    LoginWindow(root, lambda user_id, is_admin: messagebox.showinfo("Информация", f"User ID: {user_id}, Is Admin: {is_admin}"))
    root.mainloop()
