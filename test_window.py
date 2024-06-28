import tkinter as tk
from tkinter import messagebox
import math
from database import Database
from configt import DB_CONFIG

def pixel_to_mm(pixel, dpi, scale):
    return pixel / dpi * 25.4 * scale

class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

class Line:
    def __init__(self, org, direction, length):
        self.org = org
        self.direction = direction
        self.length = length
        self.calculate_end()

    def calculate_end(self):
        self.end = Vector2D(self.org.x + self.direction.x * self.length, self.org.y + self.direction.y * self.length)

    def rotate(self, angle):
        rad = math.radians(angle)
        self.direction = Vector2D(
            self.direction.x * math.cos(rad) - self.direction.y * math.sin(rad),
            self.direction.x * math.sin(rad) + self.direction.y * math.cos(rad)
        )
        self.calculate_end()

    def rotate_around_point(self, angle, point):
        translated_org = Vector2D(self.org.x - point.x, self.org.y - point.y)
        translated_end = Vector2D(self.end.x - point.x, self.end.y - point.y)
        
        rad = math.radians(angle)
        rotated_org = Vector2D(
            translated_org.x * math.cos(rad) - translated_org.y * math.sin(rad),
            translated_org.x * math.sin(rad) + translated_org.y * math.cos(rad)
        )
        rotated_end = Vector2D(
            translated_end.x * math.cos(rad) - translated_end.y * math.sin(rad),
            translated_end.x * math.sin(rad) + translated_end.y * math.cos(rad)
        )
        
        self.org = Vector2D(rotated_org.x + point.x, rotated_org.y + point.y)
        self.end = Vector2D(rotated_end.x + point.x, rotated_end.y + point.y)

    def draw(self, canvas, color='black', width=1):
        canvas.create_line(self.org.x, self.org.y, self.end.x, self.end.y, fill=color, width=width)

    @staticmethod
    def calculate_intersection(line1, line2):
        xdiff = (line1.org.x - line1.end.x, line2.org.x - line2.end.x)
        ydiff = (line1.org.y - line1.end.y, line2.org.y - line2.end.y)

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)
        if div == 0:
            return None

        d = (det([line1.org.x, line1.end.x], [line1.org.y, line1.end.y]), det([line2.org.x, line2.end.x], [line2.org.y, line2.end.y]))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return Vector2D(x, y)

class Illusion:
    def __init__(self, w_param=10, alpha=45, beta=0, vert_length=100):
        self.w_param = w_param
        self.alpha = alpha
        self.beta = beta
        self.vert_length = vert_length

class PoggendorffIllusion(tk.Frame):
    # Заданные параметры
    width_params = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55]  # мм
    angle_params = [15, 30, 45, 60, 75, 90, 105, 120, 135, 150]  # градусов
    rotation_params = [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5]  # градусов

    def __init__(self, master, app, user_id, is_admin=False):
        super().__init__(master)
        self.app = app
        self.user_id = user_id
        self.is_admin = is_admin

        self.num_tests = 5
        self.time_limit = 20
        self.current_test_index = 0
        self.scale = 7
        self.line_colours = ['red', 'blue']

        self.debug = False
        self.timer_enabled = True
        self.show_timer = True
        self.test_started = False
        self.admin_controls_visible = is_admin

        self.canvas_size = Vector2D(1024 * 1.5, 1024)
        self.continuous_line_y = self.canvas_size.y / 2
        self.intersection_point = Vector2D(0, 0)
        self.subject_response = Vector2D(0, 0)

        self.illusions = self.generate_predefined_illusions()
        self.illusion_index = 0
        self.load_next_illusion()

        self.pack(fill='both', expand=True)
        screen_width = self.master.winfo_screenwidth() - 512
        screen_height = self.master.winfo_screenheight()

        self.canvas = tk.Canvas(self, width=screen_width, height=screen_height, bg="white")
        self.canvas.pack(side='left', fill='both', expand=True)
        self.interaction_panel = tk.Frame(self)
        self.interaction_panel.pack(side='right', fill='y', expand=True)

        self.db = Database(DB_CONFIG)
        self.db.create_tables()

        self.countdown_running = False

        self.create_widgets()
        self.draw_illusion(create_slider=True)

    def generate_predefined_illusions(self):
        illusions = []
        for i in range(self.num_tests):
            w = self.width_params[i % len(self.width_params)]
            alpha = self.angle_params[i % len(self.angle_params)]
            beta = self.rotation_params[i % len(self.rotation_params)]
            illusion = Illusion(w, alpha, beta, 100)
            illusions.append(illusion)
            print(f"Generated illusion with w_param: {w}, alpha: {alpha}, beta: {beta}")
        return illusions

    def load_next_illusion(self):
        if self.illusion_index < len(self.illusions):
            illusion = self.illusions[self.illusion_index]
            self.w_param = illusion.w_param
            self.alpha = illusion.alpha
            self.beta = illusion.beta
            self.vert_length = illusion.vert_length
        else:
            self.switch_page()

    def create_widgets(self):
        self.timer_label = tk.Label(self.interaction_panel, font=('Helvetica', 48), text="00:20")
        self.timer_label.pack(fill='x')
        self.counter_label = tk.Label(self.interaction_panel, text=f'Тест номер {self.current_test_index + 1} из {len(self.illusions)}')
        self.counter_label.pack(fill='x')

        self.start_button = tk.Button(self.interaction_panel, text='Начать тест', command=self.start_test)
        self.start_button.pack(fill='x', pady=24)

        self.submit_button = tk.Button(self.interaction_panel, text='Отправить', command=self.submit_data, state=tk.DISABLED)
        self.submit_button.pack(fill='x', pady=24)

        self.admin_toggle_button = tk.Button(self.interaction_panel, text='Переключить режим админа', command=self.toggle_admin_controls)
        self.admin_toggle_button.pack(fill='x', pady=5)

        self.admin_controls = []

        self.admin_controls.append(tk.Label(self.interaction_panel, text='Количество тестов'))
        self.admin_controls.append(tk.Scale(self.interaction_panel, from_=1, to=10, orient='horizontal', command=self.adjust_num_tests))
        self.admin_controls[-1].set(self.num_tests)

        self.admin_controls.append(tk.Label(self.interaction_panel, text='Лимит времени (секунды)'))
        self.admin_controls.append(tk.Scale(self.interaction_panel, from_=10, to=300, orient='horizontal', command=self.adjust_time_limit))
        self.admin_controls[-1].set(self.time_limit)

        self.admin_controls.append(tk.Label(self.interaction_panel, text='Ширина стены'))
        self.admin_controls.append(tk.Scale(self.interaction_panel, from_=10, to=60, orient='horizontal', command=self.adjust_width_param))
        self.admin_controls[-1].set(self.w_param)

        self.admin_controls.append(tk.Label(self.interaction_panel, text='Угол наклона диагонали'))
        self.admin_controls.append(tk.Scale(self.interaction_panel, from_=-90, to=90, orient='horizontal', command=self.adjust_alpha_angle))
        self.admin_controls[-1].set(self.alpha)

        self.admin_controls.append(tk.Label(self.interaction_panel, text='Угол иллюзии'))
        self.admin_controls.append(tk.Scale(self.interaction_panel, from_=0, to=360, orient='horizontal', resolution=22.5, command=self.adjust_beta_angle))
        self.admin_controls[-1].set(self.beta)

        self.update_admin_controls_visibility()

    def toggle_admin_controls(self):
        if self.is_admin:
            self.admin_controls_visible = not self.admin_controls_visible
            self.update_admin_controls_visibility()
        else:
            messagebox.showerror("Ошибка", "Вы не имеете прав администратора!")

    def update_admin_controls_visibility(self):
        for control in self.admin_controls:
            if self.admin_controls_visible:
                control.pack(fill='x', pady=5)
            else:
                control.pack_forget()

    def adjust_num_tests(self, value):
        self.num_tests = int(value)
        self.illusions = self.generate_predefined_illusions()
        self.counter_label.configure(text=f'Тест номер {self.current_test_index + 1} из {len(self.illusions)}')

    def adjust_time_limit(self, value):
        self.time_limit = int(value)

    def start_test(self):
        self.test_started = True
        self.start_button.config(state=tk.DISABLED)
        self.submit_button.config(state=tk.NORMAL)
        self.start_countdown(self.time_limit)

    def draw_illusion(self, create_slider=False):
        self.canvas.delete('all')
        self.canvas_center = Vector2D(self.canvas_size.x / 2, self.canvas_size.y / 2)

        line1 = Line(Vector2D(self.canvas_center.x, self.canvas_center.y - self.vert_length / 2), Vector2D(0, 1), self.vert_length)
        self.line2 = Line(Vector2D(self.canvas_center.x + self.w_param, self.canvas_center.y - self.vert_length / 2), Vector2D(0, 1), self.vert_length)

        line1.rotate_around_point(self.beta, self.canvas_center)
        self.line2.rotate_around_point(self.beta, self.canvas_center)

        line1.draw(self.canvas, color='black', width=1)
        self.line2.draw(self.canvas, color='black', width=1)

        main_line = Line(Vector2D(self.canvas_center.x, self.canvas_center.y), Vector2D(-1, 0), 50)
        main_line.rotate(self.alpha)
        main_line.rotate_around_point(self.beta, self.canvas_center)
        main_line.draw(self.canvas, color=self.line_colours[0], width=2)

        self.continuous_line = Line(Vector2D(self.canvas_center.x + self.w_param, self.continuous_line_y), Vector2D(1, 0), 50)
        self.continuous_line.rotate(self.alpha)
        self.continuous_line.rotate_around_point(self.beta, self.canvas_center)
        self.subject_response = self.continuous_line.org
        self.continuous_line.draw(self.canvas, color=self.line_colours[0], width=2)

        self.intersection_point = Line.calculate_intersection(main_line, self.line2)
        if self.intersection_point is None:
            self.debug_square = None
            if self.debug:
                messagebox.showinfo('Ошибка', 'Линии не пересекаются')
        else:
            self.debug_square = self.canvas.create_rectangle(self.intersection_point.x - 1, self.intersection_point.y - 1, self.intersection_point.x + 1, self.intersection_point.y + 1, fill='green')

            if not self.debug:
                self.canvas.itemconfig(self.debug_square, state='hidden')

        self.canvas.scale('all', self.canvas_center.x, self.canvas_center.y, self.scale, self.scale)
        self.canvas.update()

        if create_slider:
            self.position_slider = tk.Scale(self.interaction_panel, from_=0 + self.canvas_center.y - self.vert_length / 2, to=self.canvas_center.y + self.vert_length / 2, orient='horizontal', command=self.adjust_line_position)
            self.position_slider.set(self.continuous_line_y)
            self.position_slider.pack(fill='x', pady=24)
            self.position_slider.takefocus = True

    def adjust_alpha_angle(self, value):
        if self.test_started:
            self.alpha = int(value)
            self.draw_illusion()

    def adjust_beta_angle(self, value):
        if self.test_started:
            self.beta = int(value)
            self.draw_illusion()

    def adjust_width_param(self, value):
        if self.test_started:
            self.w_param = int(value)
            self.draw_illusion()

    def adjust_line_position(self, value):
        if self.test_started:
            self.continuous_line_y = int(value)
            self.draw_illusion()

    def submit_data(self):
        if self.intersection_point is None:
            messagebox.showinfo('Ошибка', 'Невозможно вычислить ошибку, линии не пересекаются')
            return

        absolute_error = (self.intersection_point - self.subject_response).magnitude()

        self.db.insert_poggendorff_result(self.user_id, self.illusion_index, absolute_error)

        self.illusion_index += 1
        self.load_next_illusion()

        if self.illusion_index < len(self.illusions):
            self.position_slider.destroy()
            self.draw_illusion(create_slider=True)
            self.current_test_index += 1
            self.counter_label.configure(text=f'Тест номер {self.current_test_index + 1} из {len(self.illusions)}')
        else:
            self.switch_page()

    def switch_page(self):
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
            time_format = '{:02d}:{:02d}'.format(mins, secs)
            self.timer_label.configure(text=time_format)
            self.after(1000, self.countdown, time_remaining - 1)
        elif not self.countdown_running:
            self.timer_label.configure(text="Таймер остановлен")
        else:
            self.timer_label.configure(text="Время вышло!")
            self.times_up()

    def times_up(self):
        self.switch_page()

# Пример использования
if __name__ == "__main__":
    root = tk.Tk()
    app = PoggendorffIllusion(root, None, user_id=1, is_admin=True)  # Передаем None вместо app, так как нет экземпляра App
    app.pack(fill="both", expand=True)
    root.mainloop()
