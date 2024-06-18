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
    illusions = [
        {
            "r_param": 10,
            "d_param": 45,
            "alpha": 0,
            "circle_fill": ["blue", "blue", "red"],
            "circle_outline": ["black", "black", "black"],
            "repeat": 2
        },
        {
            "r_param": 5,
            "d_param": 23,
            "alpha": 0,
            "circle_fill": ["blue", "blue", "red"],
            "circle_outline": ["black", "black", "black"],
            "repeat": 2
        },
        {
            "r_param": 24,
            "d_param": 63,
            "alpha": 0,
            "circle_fill": ["blue", "blue", "red"],
            "circle_outline": ["black", "black", "black"],
            "repeat": 2
        }
    ]
    illNum = 0
    r_param = 10
    d_param = 45
    alpha = 0
    user_id = None
    circles_fill = ['blue', 'blue', 'red']
    circles_outline = ['black', 'black', 'black']

    def __init__(self, master, user_id: int, next_window_callback):
        super().__init__(master)
        self.user_id = user_id
        self.next_window_callback = next_window_callback
        self.pack(fill='both', expand=True)

        self.illusions = [
            {"r_param": 10, "d_param": 45, "alpha": 0, "circle_fill": ["blue", "blue", "red"], "circle_outline": ["black", "black", "black"], "repeat": 2},
            {"r_param": 5, "d_param": 23, "alpha": 0, "circle_fill": ["blue", "blue", "red"], "circle_outline": ["black", "black", "black"], "repeat": 2},
            {"r_param": 24, "d_param": 63, "alpha": 0, "circle_fill": ["blue", "blue", "red"], "circle_outline": ["black", "black", "black"], "repeat": 2}
        ]
        self.illusion_index = 0
        self.load_next_illusion()

        self.canvas = tk.Canvas(self, bg="white", width=800, height=600)
        self.canvas.pack(side='left', fill='both', expand=True)

        self.interaction_panel = tk.Frame(self)
        self.interaction_panel.pack(side='right', fill='y', expand=True)

        self.create_widgets()
        self.draw_illusion()

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
        self.timer = tk.Label(self.interaction_panel, font=('Helvetica', 48), text="00:00:00")
        self.timer.pack(fill='x')
        self.counter = tk.Label(self.interaction_panel, text=f'Test number {self.illNum + 1} out of {len(self.illusions)}')
        self.counter.pack(fill='x')

        self.NextButton = tk.Button(self.interaction_panel, text='Submit', command=self.submit_data)
        self.NextButton.pack(fill='x', pady=24)

        tk.Label(self.interaction_panel, text='Radius of the circles').pack(pady=5)
        self.slider_r = tk.Scale(self.interaction_panel, from_=5, to=30, orient='horizontal', command=self.adjust_r)
        self.slider_r.set(self.r_param)
        self.slider_r.pack(fill='x', pady=5)

        tk.Label(self.interaction_panel, text='Distance between circles').pack(pady=5)
        self.slider_d = tk.Scale(self.interaction_panel, from_=20, to=100, orient='horizontal', command=self.adjust_d)
        self.slider_d.set(self.d_param)
        self.slider_d.pack(fill='x', pady=5)

        tk.Label(self.interaction_panel, text='Adjust circle position').pack(pady=5)
        self.slider_circle = tk.Scale(self.interaction_panel, from_=256 - self.d_param, to=0, orient='horizontal', command=self.adjust_circle)
        self.slider_circle.set(70)
        self.slider_circle.pack(fill='x', pady=5)

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
        self.r_param = int(value)
        self.draw_illusion()

    def adjust_d(self, value):
        self.d_param = int(value)
        self.draw_illusion()

    def adjust_circle(self, value):
        self.draw_illusion(int(value))

    def submit_data(self):
        dpi = self.winfo_fpixels('1i')
        
        L_ref = 2 * self.d_param
        L_test = (self.subject_response.x - self.r_param) - (self.ill_center.x + self.r_param)
        
        absolute_error = L_ref - L_test
        absolute_error_mm = pixel_to_mm(absolute_error, dpi, 2)

        messagebox.showinfo("Result", f'ΔS = {absolute_error:.2f} pixels ({absolute_error_mm:.2f} mm)')

        print(f'ΔS = {absolute_error:.2f} pixels ({absolute_error_mm:.2f} mm)')
    
        self.illusion_index += 1
        self.load_next_illusion()

        if self.illusion_index < len(self.illusions):
            self.draw_illusion()
            self.illNum += 1
            self.counter.configure(text=f'Test number {self.illNum + 1} out of {len(self.illusions)}')
        else:
            self.switchPage()

    def switchPage(self):
        self.pack_forget()
        self.next_window_callback()
