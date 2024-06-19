import tkinter as tk
from PIL import Image, ImageTk  # Импортируем необходимые модули для работы с изображениями
import os

class TestSelectionWindow:
    def __init__(self, root, next_window_callback, show_results_callback, user_id, is_admin=False):
        self.root = root
        self.next_window_callback = next_window_callback
        self.show_results_callback = show_results_callback
        self.user_id = user_id
        self.is_admin = is_admin
        self.completed_tests = self.load_completed_tests()
        self.create_widgets()

    def load_completed_tests(self):
        # Проверяем существование файла с пройденными тестами и загружаем данные
        if os.path.exists(f'completed_tests_{self.user_id}.txt'):
            with open(f'completed_tests_{self.user_id}.txt', 'r') as file:
                return set(file.read().splitlines())
        return set()

    def save_completed_tests(self):
        with open(f'completed_tests_{self.user_id}.txt', 'w') as file:
            file.write("\n".join(self.completed_tests))

    def create_widgets(self):
        # Создаем рамку для центрирования содержимого
        self.frame = tk.Frame(self.root)
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(self.frame, text="Выберите тип теста:", font=('Helvetica', 24)).grid(row=0, column=0, columnspan=6, pady=30)

        self.tests = [
            ("Иллюзия Поггендорфа", "Poggendorff", "C:/Users/Profil1/Desktop/проект/illusion/POGGENDORF.png"),
            ("Вертикально-горизонтальная иллюзия", "VerticalHorizontal", "C:/Users/Profil1/Desktop/проект/illusion/VERTICAL.png"),
            ("Иллюзия расстояния между краями окружностей", "MullerLyer", "C:/Users/Profil1/Desktop/проект/illusion/MULLER.png")
        ]
        self.test_var = tk.StringVar(value=self.tests[0][1])

        for i, (test_label, test_value, img_path) in enumerate(self.tests):
            self.add_test_option(i, test_label, test_value, img_path)

        tk.Button(self.frame, text="Далее", command=self.next_window, font=('Helvetica', 18)).grid(row=3, column=5, pady=30)
        tk.Button(self.frame, text="Результаты теста", command=self.show_results, font=('Helvetica', 18)).grid(row=3, column=0, pady=30)

    def add_test_option(self, index, test_label, test_value, img_path):
        try:
            img = Image.open(img_path)
            img = img.resize((200, 200), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(self.frame, image=photo)
            label.image = photo  # Сохраняем ссылку на изображение, чтобы избежать его удаления
            label.grid(row=1, column=index*2, padx=30, pady=20)
        except Exception as e:
            print(f"Не удалось загрузить изображение {img_path}: {e}")

        rb = tk.Radiobutton(self.frame, text=test_label, variable=self.test_var, value=test_value, font=('Helvetica', 18))
        rb.grid(row=2, column=index*2, padx=30, pady=20)
        
        if test_value in self.completed_tests:
            rb.config(state=tk.DISABLED)

    def next_window(self):
        selected_test = self.test_var.get()
        if selected_test not in self.completed_tests:
            self.next_window_callback(selected_test, self.user_id, self.is_admin)
            self.completed_tests.add(selected_test)
            self.save_completed_tests()
        else:
            tk.messagebox.showinfo("Информация", "Вы уже прошли этот тест.")

    def show_results(self):
        self.show_results_callback(self.user_id)

# Пример использования
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1600x1000")  # Устанавливаем размеры окна
    TestSelectionWindow(root, None, None, 1, True)
    root.mainloop()
