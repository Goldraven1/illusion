import tkinter as tk
import math
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
    def __init__(self, master, app, user_id: int, is_admin=False):
        super().__init__(master)
        self.app = app
        self.user_id = user_id
        self.is_admin = is_admin
        self.admin_controls_visible = is_admin
        self.test_started = False
        self.total_time_limit = 20
        self.num_tests = 5
        self.pack(fill='both', expand=True)

        self.illusions = self.generate_illusions()
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

    def generate_illusions(self):
        illusions = []
        
        S_ref_values = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]
        D_values = [5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25]
        phi_values = [22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5]

        for i in range(len(S_ref_values)):
            illusion = {
                "S_ref": S_ref_values[i],
                "D": D_values[i % len(D_values)],
                "phi": phi_values[i % len(phi_values)],
                "circle_fill": ["blue", "blue", "red"],
                "circle_outline": ["black", "black", "black"]
            }
            illusions.append(illusion)
        return illusions[:self.num_tests]

    def load_next_illusion(self):
        if self.illusion_index < len(self.illusions):
            illusion = self.illusions[self.illusion_index]
            self.S_ref = illusion["S_ref"]
            self.D = illusion["D"]
            self.phi = illusion["phi"]
            self.circles_fill = illusion["circle_fill"]
            self.circles_outline = illusion["circle_outline"]
        else:
            self.switchPage()

    def create_widgets(self):
        self.timer = tk.Label(self.interaction_panel, font=('Helvetica', 48), text=f"00:{self.total_time_limit:02d}")
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

        self.admin_controls.append(tk.Label(self.interaction_panel, text='Количество тестов'))
        self.admin_controls.append(tk.Scale(self.interaction_panel, from_=1, to=10, orient='horizontal', command=self.adjust_num_tests))
        self.admin_controls[-1].set(self.num_tests)

        self.admin_controls.append(tk.Label(self.interaction_panel, text='Лимит времени (секунды)'))
        self.admin_controls.append(tk.Scale(self.interaction_panel, from_=10, to=300, orient='horizontal', command=self.adjust_time_limit))
        self.admin_controls[-1].set(self.total_time_limit)

        self.admin_controls.append(tk.Label(self.interaction_panel, text='Радиус окружностей'))
        self.admin_controls.append(tk.Scale(self.interaction_panel, from_=10, to=25, orient='horizontal', command=self.adjust_radius))
        self.admin_controls[-1].set(20)

        self.admin_controls.append(tk.Label(self.interaction_panel, text='Расстояние между окружностями'))
        self.admin_controls.append(tk.Scale(self.interaction_panel, from_=20, to=50, orient='horizontal', command=self.adjust_D))
        self.admin_controls[-1].set(self.D)

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

    def adjust_num_tests(self, value):
        self.num_tests = int(value)
        self.illusions = self.generate_illusions()
        self.counter.configure(text=f'Тест номер {self.illusion_index + 1} из {len(self.illusions)}')

    def adjust_time_limit(self, value):
        self.total_time_limit = int(value)
        self.timer.configure(text=f"00:{self.total_time_limit:02d}")

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
        
        first_circle_pos = Vector2D(self.ill_center.x - self.S_ref / 2 - self.D, self.ill_center.y)
        second_circle_pos = Vector2D(self.ill_center.x + self.S_ref / 2, self.ill_center.y)
        third_circle_pos = Vector2D(self.ill_center.x + self.S_ref / 2 + self.D + circle_pos, self.ill_center.y)

        first_circle = Circle(first_circle_pos, self.S_ref / 2)
        second_circle = Circle(second_circle_pos, self.S_ref / 2)
        third_circle = Circle(third_circle_pos, self.S_ref / 2)

        self.subject_response = third_circle_pos

        first_circle.draw(self.canvas, color=self.circles_outline[0], fill=self.circles_fill[0], width=1)
        second_circle.draw(self.canvas, color=self.circles_outline[1], fill=self.circles_fill[1], width=1)
        third_circle.draw(self.canvas, color=self.circles_outline[2], fill=self.circles_fill[2], width=1)

    def adjust_radius(self, value):
        if self.test_started:
            self.S_ref = int(value) * 2
            self.draw_illusion()

    def adjust_D(self, value):
        if self.test_started:
            self.D = int(value)
            self.draw_illusion()

    def adjust_circle(self, value):
        if self.test_started:
            self.draw_illusion(int(value))

    def submit_data(self):
        dpi = self.winfo_fpixels('1i')
        
        L_ref = self.S_ref
        L_test = (self.subject_response.x - self.S_ref / 2) - (self.ill_center.x + self.S_ref / 2)
        
        absolute_error = L_ref - L_test
        absolute_error_mm = pixel_to_mm(absolute_error, dpi, 2)

        self.db.insert_muller_lyer_result(self.user_id, self.illusion_index, absolute_error_mm)
    
        self.illusion_index += 1
        self.load_next_illusion()

        if self.illusion_index < len(self.illusions):
            self.draw_illusion()
            self.counter.configure(text=f'Тест номер {self.illusion_index + 1} из {len(self.illusions)}')
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
    app = MullerLyerIllusion(root, None, user_id=1, is_admin=True)
    app.pack(fill="both", expand=True)
    root.mainloop()
