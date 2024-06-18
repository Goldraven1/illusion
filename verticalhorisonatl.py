import tkinter as tk
from tkinter import messagebox
import math

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
    illusions = [
        {
            "l_param": 200,
            "h_param": 200,
            "d_param": 0,
            "alpha": 0,
            "beta": 0,
            "lines_colour": ["blue", "red"]
        },
        {
            "l_param": 100,
            "h_param": 150,
            "d_param": 20,
            "alpha": 15,
            "beta": 30,
            "lines_colour": ["green", "blue"]
        },
        {
            "l_param": 250,
            "h_param": 100,
            "d_param": -30,
            "alpha": 45,
            "beta": 60,
            "lines_colour": ["blue", "red"]
        }
    ]
    
    def __init__(self, master, user_id: int, next_window_callback):
        super().__init__(master)
        self.user_id = user_id
        self.next_window_callback = next_window_callback
        self.pack(fill='both', expand=True)

        self.illusion_index = 0
        self.load_next_illusion()

        self.canvas = tk.Canvas(self, bg="white", width=1200, height=800)
        self.canvas.pack(side='left', fill='both', expand=True)

        self.interaction_panel = tk.Frame(self)
        self.interaction_panel.pack(side='right', fill='y', expand=True)

        self.create_widgets()
        self.draw_illusion()

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
        self.timer = tk.Label(self.interaction_panel, font=('Helvetica', 48), text="00:00:00")
        self.timer.pack(fill='x')
        self.counter = tk.Label(self.interaction_panel, text=f'Test number {self.illusion_index + 1} out of {len(self.illusions)}')
        self.counter.pack(fill='x')

        self.NextButton = tk.Button(self.interaction_panel, text='Submit', command=self.submit_data)
        self.NextButton.pack(fill='x', pady=24)

        tk.Label(self.interaction_panel, text='Length of the vertical line').pack(pady=5)
        self.slider_length = tk.Scale(self.interaction_panel, from_=10, to=400, orient='horizontal', command=self.adjust_length)
        self.slider_length.set(35)
        self.slider_length.pack(fill='x', pady=5)

    def draw_illusion(self, length=35):
        self.canvas.delete('all')

        canvas_width = 700
        canvas_height = 500
        self.ill_center = Vector2D(canvas_width // 2, canvas_height // 2)

        horizontal_line = Line(Vector2D(self.ill_center.x - self.l_param / 2, self.ill_center.y), Vector2D(1, 0), self.l_param)
        self.vertical_line = Line(Vector2D(self.ill_center.x + self.d_param, self.ill_center.y), Vector2D(0, -1), length)

        self.vertical_line.rotate_around_point(self.alpha, Vector2D(self.ill_center.x + self.d_param, self.ill_center.y))
        horizontal_line.rotate_around_point(self.beta, self.ill_center)
        self.vertical_line.rotate_around_point(self.beta, self.ill_center)

        self.subject_response = self.vertical_line.secn

        horizontal_line.draw(self.canvas, color=self.lines_colour[0], width=2)
        self.vertical_line.draw(self.canvas, color=self.lines_colour[1], width=2)

        self.canvas.scale('all', 0, 0, 2, 2)

    def adjust_length(self, value):
        self.draw_illusion(int(value))

    def submit_data(self):
        dpi = self.winfo_fpixels('1i')
        
        L_hor = self.l_param
        L_vert = self.vertical_line.len
        
        absolute_error = L_hor - L_vert
        absolute_error_mm = pixel_to_mm(absolute_error, dpi, 2)

        messagebox.showinfo("Result", f'Δl = {absolute_error:.2f} pixels ({absolute_error_mm:.2f} mm)')

        print(f'Δl = {absolute_error:.2f} pixels ({absolute_error_mm:.2f} mm)')
    
        self.illusion_index += 1
        self.load_next_illusion()

        if self.illusion_index < len(self.illusions):
            self.draw_illusion()
            self.counter.configure(text=f'Test number {self.illusion_index + 1} out of {len(self.illusions)}')
        else:
            self.switchPage()

    def switchPage(self):
        self.pack_forget()
        self.next_window_callback()

if __name__ == "__main__":
    def show_test_selection_window():
        root = tk.Tk()
        tk.Label(root, text="Выберите тест").pack()
        root.mainloop()

    root = tk.Tk()
    app = VerticalHorizontalIllusion(master=root, user_id=1, next_window_callback=show_test_selection_window)
    app.pack(fill="both", expand=True)
    root.mainloop()
