# result_window.py

import tkinter as tk
from database import Database
from configt import DB_CONFIG

class ResultsWindow(tk.Frame):
    def __init__(self, root, app, user_id):
        super().__init__(root)
        self.app = app
        self.user_id = user_id
        self.db = Database(DB_CONFIG)
        self.create_widgets()
        self.pack(fill='both', expand=True)

    def create_widgets(self):
        tk.Label(self, text="Результаты тестов").pack(pady=10)
        self.tests = [
            ("Иллюзия Поггендорфа", self.show_poggendorff_results),
            ("Вертикально-горизонтальная иллюзия", self.show_vertical_horizontal_results),
            ("Иллюзия расстояния между краями окружностей", self.show_muller_lyer_results)
        ]
        for test_name, command in self.tests:
            tk.Button(self, text=test_name, command=command).pack(fill='x', pady=5)

        self.back_button = tk.Button(self, text="Назад", command=self.back_to_selection)
        self.back_button.pack(pady=10)

    def show_poggendorff_results(self):
        results = self.db.fetch_poggendorff_results(self.user_id)
        self.show_results(results, "Результаты иллюзии Поггендорфа", ["Индекс иллюзии", "Абсолютная ошибка"])

    def show_vertical_horizontal_results(self):
        results = self.db.fetch_vertical_horizontal_results(self.user_id)
        self.show_results(results, "Результаты вертикально-горизонтальной иллюзии", ["Индекс иллюзии", "Абсолютная ошибка"])

    def show_muller_lyer_results(self):
        results = self.db.fetch_muller_lyer_results(self.user_id)
        self.show_results(results, "Результаты иллюзии расстояния между краями окружностей", ["Индекс иллюзии", "Абсолютная ошибка"])

    def show_results(self, results, title, columns):
        self.clear_frame()
        tk.Label(self, text=title, font=('Helvetica', 16)).pack(pady=10)

        if results:
            for row in results:
                text = ", ".join([f"{columns[i]}: {row[i]}" for i in range(len(row))])
                tk.Label(self, text=text).pack()
        else:
            tk.Label(self, text="Результаты отсутствуют.", font=('Helvetica', 14)).pack(pady=10)

        tk.Button(self, text="Назад", command=self.back_to_test_results).pack(pady=10)

    def back_to_test_results(self):
        self.clear_frame()
        self.create_widgets()

    def back_to_selection(self):
        self.pack_forget()
        self.app.show_test_selection_window(self.user_id)

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

# Пример использования
if __name__ == "__main__":
    root = tk.Tk()
    app = ResultsWindow(root, None, user_id=1)  # Передаем None вместо app, так как нет экземпляра App
    app.pack(fill="both", expand=True)
    root.mainloop()
