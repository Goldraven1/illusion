import tkinter as tk

class TestSelectionWindow:
    def __init__(self, root, next_window_callback):
        self.root = root
        self.next_window_callback = next_window_callback
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Выберите тип теста:").grid(row=0, column=0, columnspan=2)

        self.tests = [
            ("Иллюзия Поггендорфа", "Poggendorff"),
            ("Вертикально-горизонтальная иллюзия", "VerticalHorizontal"),
            ("Иллюзия расстояния между краями окружностей", "MullerLyer")
        ]
        self.test_var = tk.StringVar(value=self.tests[0][1])

        for i, (test_label, test_value) in enumerate(self.tests):
            tk.Radiobutton(self.root, text=test_label, variable=self.test_var, value=test_value).grid(row=i+1, column=0, columnspan=2)

        tk.Button(self.root, text="Далее", command=self.next_window).grid(row=len(self.tests)+1, column=1)

    def next_window(self):
        selected_test = self.test_var.get()
        self.next_window_callback(selected_test)
