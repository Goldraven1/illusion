# muller_lyer_illusion.py

import tkinter as tk
import math
import random
from database import Database
from configt import DB_CONFIG

def pixel_to_mm(pixel, dpi, scale):
    return pixel / dpi * 25.4 * scale

class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + self.y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - self.y)

    def __mul__(self, param):
        if isinstance(param, Vector2D):
            return self.x * param.y - self.y * param.x 
        return Vector2D(self.x * param, self.y * param)

    def __str__(self):
        return f"({self.x}, {self.y})"
    
    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

class Circle:
    def __init__(self, center: Vector2D, radius: float):
        self.center = center
        self.radius = radius
    
    def __str__(self):
        return f"({self.center}, {self.radius})"
    
    def get_points_for_oval(self):
        return Vector2D(self.center.x - self.radius, self.center.y - self.radius), Vector2D(self.center.x + self.radius, self.center.y + self.radius)
    
    def draw(self, canvas, color='black', fill='white', width=1):
        points = self.get_points_for_oval()
        canvas.create_oval(points[0].x, points[0].y, points[1].x, points[1].y, outline=color, fill=fill, width=width)

class MullerLyerIllusion(tk.Frame):
    total_time_limit = 20  # Общий лимит времени в секундах

    def __init__(self, master, app, user_id: int, is_admin=False):
        super().__init__(master)
        self.app = app
        self.user_id = user_id
        self.is_admin = is_admin
        self.admin_controls_visible = is_admin
        self.test_started = False  # Флаг для отслеживания начала теста
        self.pack(fill='both', expand=True)

        self.illusions = self.generate_random_illusions(3)
        self.illusion_index = 0
        self.load_next_illusion()

        self.canvas = tk.Canvas(self, bg="white", width=800, height=600)
        self.canvas.pack(side='left', fill='both', expand=True)

        self.interaction_panel = tk.Frame(self)
        self.interaction_panel.pack(side='right', fill='y', expand=True)

        self.db = Database(DB_CONFIG)
        self.db.create_tables()

        self.countdown_running = False

        self.create_widgets()
        self.draw_illusion()

    def generate_random_illusions(self, num_illusions):
        illusions = []
        for _ in range(num_illusions):
            illusion = {
                "r_param": random.randint(10, 25),
                "d_param": random.randint(20, 50),
                "alpha": 0,
                "circle_fill": ["blue", "blue", "red"],
                "circle_outline": ["black", "black", "black"],
                "repeat": 2
            }
            illusions.append(illusion)
        return illusions

    def load_next_illusion(self):
        if self.illusion_index < len(self.illusions):
            illusion = self.illusions[self.illusion_index]
            self.r_param = illusion["r_param"]
            self.d_param = illusion["d_param"]
            self.alpha = illusion["alpha"]
            self.circles_fill = illusion["circle_fill"]
            self.circles_outline = illusion["circle_outline"]
        else:
            self.switchPage()

    def create_widgets(self):
        self.timer = tk.Label(self.interaction_panel, font=('Helvetica', 48), text="00:20")
        self.timer.pack(fill='x')
        self.counter = tk.Label(self.interaction_panel, text=f'Тест номер {self.illusion_index + 1} из {len(self.illusions)}')
        self.counter.pack(fill='x')

        self.StartButton = tk.Button(self.interaction_panel, text='Начать тест', command=self.start_test)
        self.StartButton.pack(fill='x', pady=24)

        self.NextButton = tk.Button(self.interaction_panel, text='Отправить', command=self.submit_data, state=tk.DISABLED)
        self.NextButton.pack(fill='x', pady=24)

        self.admin_toggle_button = tk.Button(self.interaction_panel, text='Переключить режим админа', command=self.toggle_admin_controls)
        self.admin_toggle_button.pack(fill='x', pady=5)

        self.circle_pos_label = tk.Label(self.interaction_panel, text='Положение окружности')
        self.circle_pos_label.pack(pady=5)
        self.slider_circle = tk.Scale(self.interaction_panel, from_=0, to=200, orient='horizontal', command=self.adjust_circle)
        self.slider_circle.pack(fill='x', pady=5)

        self.admin_controls = []

        self.admin_controls.append(tk.Label(self.interaction_panel, text='Радиус окружностей'))
        self.admin_controls.append(tk.Scale(self.interaction_panel, from_=10, to=25, orient='horizontal', command=self.adjust_r))
        self.admin_controls[-1].set(self.r_param)

        self.admin_controls.append(tk.Label(self.interaction_panel, text='Расстояние между окружностями'))
        self.admin_controls.append(tk.Scale(self.interaction_panel, from_=20, to=50, orient='horizontal', command=self.adjust_d))
        self.admin_controls[-1].set(self.d_param)

        self.update_admin_controls_visibility()

    def toggle_admin_controls(self):
        if self.is_admin:
            self.admin_controls_visible = not self.admin_controls_visible
            self.update_admin_controls_visibility()
        else:
            tk.messagebox.showerror("Ошибка", "Вы не имеете прав администратора!")

    def update_admin_controls_visibility(self):
        for control in self.admin_controls:
            if self.admin_controls_visible:
                control.pack(fill='x', pady=5)
            else:
                control.pack_forget()

    def start_test(self):
        self.test_started = True
        self.StartButton.config(state=tk.DISABLED)
        self.NextButton.config(state=tk.NORMAL)
        self.start_countdown(self.total_time_limit)

    def draw_illusion(self, circle_pos=0):
        self.canvas.delete('all')

        canvas_width = 800
        canvas_height = 600
        self.ill_center = Vector2D(canvas_width // 2, canvas_height // 2)
        
        first_circle_pos = Vector2D(self.ill_center.x - self.r_param - self.d_param, self.ill_center.y)
        second_circle_pos = Vector2D(self.ill_center.x, self.ill_center.y)
        third_circle_pos = Vector2D(self.ill_center.x + self.d_param + circle_pos, self.ill_center.y)

        first_circle = Circle(first_circle_pos, self.r_param)
        second_circle = Circle(second_circle_pos, self.r_param)
        third_circle = Circle(third_circle_pos, self.r_param)

        self.subject_response = third_circle_pos

        first_circle.draw(self.canvas, color=self.circles_outline[0], fill=self.circles_fill[0], width=1)
        second_circle.draw(self.canvas, color=self.circles_outline[1], fill=self.circles_fill[1], width=1)
        third_circle.draw(self.canvas, color=self.circles_outline[2], fill=self.circles_fill[2], width=1)

    def adjust_r(self, value):
        if self.test_started:
            self.r_param = int(value)
            self.draw_illusion()

    def adjust_d(self, value):
        if self.test_started:
            self.d_param = int(value)
            self.draw_illusion()

    def adjust_circle(self, value):
        if self.test_started:
            self.draw_illusion(int(value))

    def submit_data(self):
        dpi = self.winfo_fpixels('1i')
        
        L_ref = 2 * self.d_param
        L_test = (self.subject_response.x - self.r_param) - (self.ill_center.x + self.r_param)
        
        absolute_error = L_ref - L_test
        absolute_error_mm = pixel_to_mm(absolute_error, dpi, 2)

        self.db.insert_muller_lyer_result(self.user_id, self.illusion_index, absolute_error_mm)
    
        self.illusion_index += 1
        self.load_next_illusion()

        if self.illusion_index < len(self.illusions):
            self.draw_illusion()
            self.illNum += 1
            self.counter.configure(text=f'Тест номер {self.illNum + 1} из {len(self.illusions)}')
        else:
            self.switchPage()

    def switchPage(self):
        self.stop_countdown()
        self.pack_forget()
        self.db.close()
        self.app.show_test_selection_window(self.user_id)

    def start_countdown(self, time_remaining):
        self.countdown_running = True
        self.countdown(time_remaining)

    def stop_countdown(self):
        self.countdown_running = False

    def countdown(self, time_remaining):
        if time_remaining > 0 and self.countdown_running:
            mins, secs = divmod(time_remaining, 60)
            timeformat = '{:02d}:{:02d}'.format(mins, secs)
            self.timer.configure(text=timeformat)
            self.after(1000, self.countdown, time_remaining - 1)
        elif not self.countdown_running:
            self.timer.configure(text="Таймер остановлен")
        else:
            self.timer.configure(text="Время вышло!")
            self.times_up()

    def times_up(self):
        self.switchPage()

# Пример использования
if __name__ == "__main__":
    root = tk.Tk()
    app = MullerLyerIllusion(root, None, user_id=1, is_admin=True)  # Передаем None вместо app, так как нет экземпляра App
    app.pack(fill="both", expand=True)
    root.mainloop()
