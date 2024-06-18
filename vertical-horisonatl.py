import tkinter as tk
from tkinter import messagebox
import math

def pixel_to_mm(pixel, dpi, scale):
    return pixel / dpi * 25.4 * scale

class Vector2D():
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

class Line():
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

    def draw(self, canvas, color='black', width=1):
        return canvas.create_line(self.org.x, self.org.y, self.secn.x, self.secn.y, fill=color, width=width)

class Circle():
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

class verticalHorizontalIllusion(tk.Frame):
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

        # Данные из JSON вручную
        self.illusions = [
            {
                "l_param": 64,
                "h_param": 75,
                "d_param": 0,
                "alpha": 0,
                "beta": 0,
                "lines_colour": ["blue", "red"],
                "repeat": 2
            },
            {
                "l_param": 35,
                "h_param": 10,
                "d_param": 14,
                "alpha": 4,
                "beta": 3,
                "lines_colour": ["green", "blue"],
                "repeat": 2
            },
            {
                "l_param": 104,
                "h_param": 23,
                "d_param": -4,
                "alpha": 55,
                "beta": 3,
                "lines_colour": ["blue", "red"],
                "repeat": 2
            }
        ]
        self.isTimeLimited = False
        self.timeLimitInSec = 60

        self.current_illusion_index = 0
        self.current_repeat_count = 0
        self.load_next_illusion()

        self.canvas = tk.Canvas(self, width=512, height=512)
        self.canvas.grid(row=1, column=0, sticky='nsew')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.draw_illusion()

        self.counter = tk.Label(self, text=self.current_illusion_index)
        self.counter.grid()

        self.slider = tk.Scale(self, from_=0, to=128, orient='horizontal', command=self.adjust_line)
        self.slider.set(35)
        self.slider.grid()

        self.NextButton = tk.Button(self, text='Submit', command=self.submit_data)
        self.NextButton.grid()

    def load_next_illusion(self):
        if self.current_repeat_count < self.illusions[self.current_illusion_index]["repeat"]:
            self.current_repeat_count += 1
        else:
            self.current_repeat_count = 1
            self.current_illusion_index += 1

        if self.current_illusion_index < len(self.illusions):
            illusion = self.illusions[self.current_illusion_index]
            self.l_param = illusion["l_param"]
            self.h_param = illusion["h_param"]
            self.d_param = illusion["d_param"]
            self.alpha = illusion["alpha"]
            self.beta = illusion["beta"]
            self.lines_colour = illusion["lines_colour"]
        else:
            self.switchPage()

    def draw_illusion(self, length=35):
        self.canvas.delete('all')
        self.ill_center = Vector2D(128, 128)
        self.desired_point = Vector2D(self.ill_center.x, self.h_param)
        horizontal_line = Line(Vector2D(self.ill_center.x - self.l_param / 2, self.ill_center.y), Vector2D(1, 0), self.l_param)
        self.vertical_line = Line(Vector2D(self.ill_center.x + self.d_param, self.ill_center.y), Vector2D(0, -1), length)

        self.vertical_line.rotate_around_point(self.alpha, Vector2D(self.ill_center.x + self.d_param, self.ill_center.y))
        horizontal_line.rotate_around_point(self.beta, self.ill_center)
        self.vertical_line.rotate_around_point(self.beta, self.ill_center)

        self.desired_point.rotate_around_point(self.alpha, Vector2D(self.ill_center.x + self.d_param, self.ill_center.y))
        self.desired_point.rotate_around_point(self.beta, self.ill_center)

        self.subject_response = self.vertical_line.secn

        horizontal_line.draw(self.canvas, color=self.lines_colour[0], width=1)
        self.vertical_line.draw(self.canvas, color=self.lines_colour[1], width=1)

        if self.debug:
            self.circle = Circle(self.desired_point, 1)
            self.circle.draw(self.canvas, color='white', width=1)

            self.center_circle = Circle(self.ill_center, 1)
            self.center_circle.draw(self.canvas, color='white', width=1)
            
        self.canvas.scale('all', 0, 0, 2, 2)

    def adjust_alpha(self, value):
        self.alpha = int(value)
        self.draw_illusion()

    def adjust_beta(self, value):
        self.beta = int(value)
        self.draw_illusion()
    
    def adjust_h(self, value):
        self.h_param = int(value)
        self.draw_illusion()
    
    def adjust_d(self, value):
        self.d_param = int(value)
        self.draw_illusion()

    def adjust_l(self, value):
        self.l_param = int(value)
        self.draw_illusion()

    def adjust_line(self, value):
        self.draw_illusion(int(value))

    def submit_data(self):
        dpi = self.winfo_fpixels('1i')
        absolute_error = (self.desired_point - self.subject_response).magnitude()
        absolute_error_mm = pixel_to_mm(absolute_error, dpi, 2)
        max_error_pixel = (self.desired_point - self.vertical_line.org).magnitude()
        max_error_mm = pixel_to_mm(max_error_pixel, dpi, 2)
        
        # Генерация новой иллюзии
        self.load_next_illusion()

        if self.current_illusion_index < len(self.illusions):
            self.draw_illusion()
            self.illNum += 1
            self.counter.configure(text=self.illNum)
        else:
            self.switchPage()

# Пример использования
if __name__ == "__main__":
    root = tk.Tk()
    app = verticalHorizontalIllusion(user_id=1)
    app.pack(fill="both", expand=True)
    root.mainloop()
