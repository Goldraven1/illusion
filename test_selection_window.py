import tkinter as tk

class TestSelectionWindow:
    def __init__(self, root, next_window_callback):
        self.root = root
        self.next_window_callback = next_window_callback
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Выберите тип теста:").grid(row=0, column=0, columnspan=2)

        self.tests = ["Иллюзия Поггендорфа", "Вертикально-горизонтальная иллюзия", "Иллюзия расстояния между краями окружностей"]
        self.test_var = tk.StringVar(value=self.tests[0])

        for i, test in enumerate(self.tests):
            tk.Radiobutton(self.root, text=test, variable=self.test_var, value=test).grid(row=i+1, column=0, columnspan=2)

        tk.Button(self.root, text="Далее", command=self.next_window).grid(row=len(self.tests)+1, column=1)

    def next_window(self):
        selected_test = self.test_var.get()
        self.next_window_callback(selected_test)
