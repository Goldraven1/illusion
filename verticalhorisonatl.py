# vertical_horizontal_illusion.py

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
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, param):
        if isinstance(param, Vector2D):
            return self.x * param.y - self.y * param.x 
        return Vector2D(self.x * param, self.y * param)

    def __str__(self):
        return f"({self.x}, {self.y})"
    
    def rotate(self, angle):
        angle = math.radians(angle)
        x = self.x * math.cos(angle) - self.y * math.sin(angle)
        y = self.x * math.sin(angle) + self.y * math.cos(angle)
        return Vector2D(x, y)
    
    def rotate_around_point(self, angle, point):
        self.x -= point.x
        self.y -= point.y
        self.x, self.y = self.rotate(angle).x, self.rotate(angle).y
        self.x += point.x
        self.y += point.y
    
    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

class Line:
    def __init__(self, org: Vector2D, dir: Vector2D, len: float):
        self.org = org
        self.dir = dir
        self.len = len
        
        self.calculate_second()

    def calculate_second(self):
        self.secn = self.dir * self.len + self.org
    
    def rotate(self, angle):
        self.dir = self.dir.rotate(angle)
        self.calculate_second()

    def rotate_around_point(self, angle, point: Vector2D):
        self.org = self.org - point
        self.secn = self.secn - point
        self.org = self.org.rotate(angle)
        self.secn = self.secn.rotate(angle)
        self.org = self.org + point
        self.secn = self.secn + point
        self.dir = self.secn - self.org

    def __str__(self):
        return f"({self.org}, {self.secn}, {self.dir}, {self.len})"
    
    def calculate_intersection(self, line1, line2):
        a1 = line1.secn.y - line1.org.y
        b1 = line1.org.x - line1.secn.x
        c1 = a1 * line1.org.x + b1 * line1.org.y

        a2 = line2.secn.y - line2.org.y
        b2 = line2.org.x - line2.secn.x
        c2 = a2 * line2.org.x + b2 * line2.org.y

        det = a1 * b2 - a2 * b1

        if det == 0:
            return False
        else:
            x = (b2 * c1 - b1 * c2) / det
            y = (a1 * c2 - a2 * c1) / det
            return Vector2D(x, y)
        
    def draw(self, canvas, color='black', width=1):
        return canvas.create_line(self.org.x, self.org.y, self.secn.x, self.secn.y, fill=color, width=width)

class Circle:
    def __init__(self, center: Vector2D, radius: float):
        self.center = center
        self.radius = radius
    
    def __str__(self):
        return f"({self.center}, {self.radius})"
    
    def rotate_around_point(self, angle, point: Vector2D):
        self.center = self.center - point
        self.center = self.center.rotate(angle)
        self.center = self.center + point
    
    def get_points_for_oval(self):
        return Vector2D(self.center.x - self.radius, self.center.y - self.radius), Vector2D(self.center.x + self.radius, self.center.y + self.radius)
    
    def draw(self, canvas, color='black', fill='white', width=1):
        points = self.get_points_for_oval()
        canvas.create_oval(points[0].x, points[0].y, points[1].x, points[1].y, outline=color, fill=fill, width=width)

class VerticalHorizontalIllusion(tk.Frame):
    def __init__(self, master, app, user_id: int, is_admin=False):
        super().__init__(master)
        self.app = app
        self.user_id = user_id
        self.is_admin = is_admin
        self.admin_controls_visible = is_admin
        self.test_started = False  # Флаг для отслеживания начала теста
        self.pack(fill='both', expand=True)

        self.num_illusions = 5
        self.total_time_limit = 20  # Общий лимит времени в секундах

        self.illusions = self.generate_random_illusions(self.num_illusions)
        self.illusion_index = 0
        self.load_next_illusion()

        self.canvas = tk.Canvas(self, bg="white", width=1200, height=800)
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
                "l_param": random.randint(50, 150),
                "h_param": random.randint(50, 150),
                "d_param": random.randint(-30, 30),
                "alpha": random.uniform(-20, 20),
                "beta": random.uniform(-20, 20),
                "lines_colour": [random.choice(["blue", "green", "red"]), random.choice(["blue", "green", "red"])]
            }
            illusions.append(illusion)
        return illusions

    def load_next_illusion(self):
        if self.illusion_index < len(self.illusions):
            illusion = self.illusions[self.illusion_index]
            self.l_param = illusion["l_param"]
            self.h_param = illusion["h_param"]
            self.d_param = illusion["d_param"]
            self.alpha = illusion["alpha"]
            self.beta = illusion["beta"]
            self.lines_colour = illusion["lines_colour"]
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

        self.admin_controls = []

        self.admin_controls.append(tk.Label(self.interaction_panel, text='Количество тестов'))
        self.num_tests_scale = tk.Scale(self.interaction_panel, from_=1, to=10, orient='horizontal', command=self.adjust_num_illusions)
        self.num_tests_scale.set(self.num_illusions)
        self.admin_controls.append(self.num_tests_scale)

        self.admin_controls.append(tk.Label(self.interaction_panel, text='Лимит времени (секунды)'))
        self.time_limit_scale = tk.Scale(self.interaction_panel, from_=10, to=60, orient='horizontal', command=self.adjust_time_limit)
        self.time_limit_scale.set(self.total_time_limit)
        self.admin_controls.append(self.time_limit_scale)

        self.height_label = tk.Label(self.interaction_panel, text='Высота вертикальной линии')
        self.height_label.pack(pady=5)
        self.slider_height = tk.Scale(self.interaction_panel, from_=50, to=400, orient='horizontal', command=self.adjust_vertical_height)
        self.slider_height.set(self.h_param)
        self.slider_height.pack(fill='x', pady=5)

        self.admin_controls.append(tk.Label(self.interaction_panel, text='Длина горизонтальной линии'))
        self.admin_controls.append(tk.Scale(self.interaction_panel, from_=50, to=400, orient='horizontal', command=self.adjust_horizontal_length))
        self.admin_controls[-1].set(self.l_param)

        self.admin_controls.append(tk.Label(self.interaction_panel, text='Положение вертикальной линии'))
        self.admin_controls.append(tk.Scale(self.interaction_panel, from_=-100, to=100, orient='horizontal', command=self.adjust_vertical_position))
        self.admin_controls[-1].set(self.d_param)

        self.admin_controls.append(tk.Label(self.interaction_panel, text='Угол вертикальной линии'))
        self.admin_controls.append(tk.Scale(self.interaction_panel, from_=-90, to=90, orient='horizontal', command=self.adjust_vertical_angle))
        self.admin_controls[-1].set(self.alpha)

        self.admin_controls.append(tk.Label(self.interaction_panel, text='Угол иллюзии'))
        self.admin_controls.append(tk.Scale(self.interaction_panel, from_=-90, to=90, orient='horizontal', command=self.adjust_illusion_angle))
        self.admin_controls[-1].set(self.beta)

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

    def draw_illusion(self, length=None):
        self.canvas.delete('all')

        canvas_width = 700
        canvas_height = 500
        self.ill_center = Vector2D(canvas_width // 2, canvas_height // 2)

        if length is None:
            length = self.h_param

        horizontal_line = Line(Vector2D(self.ill_center.x - self.l_param / 2, self.ill_center.y), Vector2D(1, 0), self.l_param)
        self.vertical_line = Line(Vector2D(self.ill_center.x + self.d_param, self.ill_center.y), Vector2D(0, -1), length)

        self.vertical_line.rotate_around_point(self.alpha, Vector2D(self.ill_center.x + self.d_param, self.ill_center.y))
        horizontal_line.rotate_around_point(self.beta, self.ill_center)
        self.vertical_line.rotate_around_point(self.beta, self.ill_center)

        self.subject_response = self.vertical_line.secn

        horizontal_line.draw(self.canvas, color=self.lines_colour[0], width=2)
        self.vertical_line.draw(self.canvas, color=self.lines_colour[1], width=2)

        self.canvas.scale('all', 0, 0, 2, 2)

    def adjust_horizontal_length(self, value):
        if self.test_started:
            self.l_param = int(value)
            self.draw_illusion()

    def adjust_vertical_height(self, value):
        if self.test_started:
            self.h_param = int(value)
            self.draw_illusion()

    def adjust_vertical_position(self, value):
        if self.test_started:
            self.d_param = int(value)
            self.draw_illusion()

    def adjust_vertical_angle(self, value):
        if self.test_started:
            self.alpha = int(value)
            self.draw_illusion()

    def adjust_illusion_angle(self, value):
        if self.test_started:
            self.beta = int(value)
            self.draw_illusion()

    def adjust_num_illusions(self, value):
        self.num_illusions = int(value)
        self.illusions = self.generate_random_illusions(self.num_illusions)
        self.illusion_index = 0
        self.load_next_illusion()
        self.counter.configure(text=f'Тест номер {self.illusion_index + 1} из {len(self.illusions)}')

    def adjust_time_limit(self, value):
        self.total_time_limit = int(value)
        self.timer.configure(text=f"{self.total_time_limit:02d}:00")

    def submit_data(self):
        dpi = self.winfo_fpixels('1i')
        
        L_hor = self.l_param
        L_vert = self.vertical_line.len
        
        absolute_error = L_hor - L_vert
        absolute_error_mm = pixel_to_mm(absolute_error, dpi, 2)

        self.db.insert_vertical_horizontal_result(self.user_id, self.illusion_index, absolute_error_mm)
    
        self.illusion_index += 1
        self.load_next_illusion()

        if self.illusion_index < len(self.illusions):
            self.draw_illusion()
            self.counter.configure(text=f'Tест номер {self.illusion_index + 1} из {len(self.illusions)}')
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
    app = VerticalHorizontalIllusion(root, None, user_id=1, is_admin=True)  # Передаем None вместо app, так как нет экземпляра App
    app.pack(fill="both", expand=True)
    root.mainloop()
