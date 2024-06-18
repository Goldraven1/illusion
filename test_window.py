import tkinter as tk
from tkinter import Canvas, messagebox
import math

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

class PoggendorffIllusion(tk.Frame):
    w_param = 10
    alpha = 45
    beta = 0
    vert_length = 100
    illNum = 0
    intersection = Vector2D(0, 0)
    subject_response = Vector2D(0, 0)
    canvas_size = Vector2D(1024 * 1.5, 1024)
    user_id = None

    scale = 7
    line_colours = ['red', 'blue']

    def __init__(self, master, user_id):
        super().__init__(master)
        self.pack(fill='both', expand=True)

        self.debug = False
        self.timerOpt = False
        self.showTimer = False

        self.user_id = user_id

        self.illusions = [
            {"w_param": 10, "alpha": 45, "beta": 0, "vert_length": 100, "repeat": 3},
            {"w_param": 20, "alpha": 32, "beta": 0.78, "vert_length": 50, "repeat": 1},
            {"w_param": 30, "alpha": 25, "beta": 0.92, "vert_length": 78, "repeat": 2}
        ]

        self.illusion_index = 0
        self.load_next_illusion()

        screen_width = self.master.winfo_screenwidth() - 512
        screen_height = self.master.winfo_screenheight()

        self.canvas = tk.Canvas(self, width=screen_width, height=screen_height, bg="white")
        self.canvas.pack(side='left', fill='both', expand=True)

        self.interaction_panel = tk.Frame(self)
        self.interaction_panel.pack(side='right', fill='y', expand=True)

        self.countdown_running = False

        self.continuous_line_y = self.canvas_size.y / 2  # Initialize continuous line's Y position
        self.create_widgets()
        self.draw_illusion(sliderCreate=True)

    def load_next_illusion(self):
        if self.illusion_index < len(self.illusions):
            illusion = self.illusions[self.illusion_index]
            self.w_param = illusion["w_param"]
            self.alpha = illusion["alpha"]
            self.beta = illusion["beta"]
            self.vert_length = illusion["vert_length"]
        else:
            self.switchPage()

    def create_widgets(self):
        self.timer = tk.Label(self.interaction_panel, font=('Helvetica', 48), text="00:00:00")
        self.timer.pack(fill='x')
        self.counter = tk.Label(self.interaction_panel, text=f'Test number {self.illNum + 1} out of {len(self.illusions)}')
        self.counter.pack(fill='x')
        
        self.NextButton = tk.Button(self.interaction_panel, text='Submit', command=self.submit_data)
        self.NextButton.pack(fill='x', pady=24)

        tk.Label(self.interaction_panel, text='Width of the wall').pack(pady=5)
        self.slider_w = tk.Scale(self.interaction_panel, from_=10, to=100, orient='horizontal', command=self.adjust_w)
        self.slider_w.set(self.w_param)
        self.slider_w.pack(fill='x', pady=5)

        tk.Label(self.interaction_panel, text='Angle of the diagonal line').pack(pady=5)
        self.slider_alpha = tk.Scale(self.interaction_panel, from_=-90, to=90, orient='horizontal', command=self.adjust_alpha)
        self.slider_alpha.set(self.alpha)
        self.slider_alpha.pack(fill='x', pady=5)

        tk.Label(self.interaction_panel, text='Angle of the illusion').pack(pady=5)
        self.slider_beta = tk.Scale(self.interaction_panel, from_=0, to=360, orient='horizontal', command=self.adjust_beta)
        self.slider_beta.set(self.beta)
        self.slider_beta.pack(fill='x', pady=5)

    def draw_illusion(self, sliderCreate=False):
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

        self.intersection = Line.calculate_intersection(main_line, self.line2)
        if self.intersection is None:
            self.debug_square = None
            if self.debug:
                messagebox.showinfo('Error', 'Lines do not intersect')
        else:
            self.debug_square = self.canvas.create_rectangle(self.intersection.x - 1, self.intersection.y - 1, self.intersection.x + 1, self.intersection.y + 1, fill='green')

            if not self.debug:
                self.canvas.itemconfig(self.debug_square, state='hidden')

        self.canvas.scale('all', self.canvas_center.x, self.canvas_center.y, self.scale, self.scale)
        self.canvas.update()

        if sliderCreate:
            self.slider = tk.Scale(self.interaction_panel, from_=0 + self.canvas_center.y - self.vert_length / 2, to=self.canvas_center.y + self.vert_length / 2, orient='horizontal', command=self.adjust_line)
            self.slider.set(self.continuous_line_y)
            self.slider.pack(fill='x', pady=24)
            self.slider.takefocus = True

    def adjust_alpha(self, value):
        self.alpha = int(value)
        self.draw_illusion()

    def adjust_beta(self, value):
        self.beta = int(value)
        self.draw_illusion()

    def adjust_w(self, value):
        self.w_param = int(value)
        self.draw_illusion()

    def adjust_line(self, value):
        self.continuous_line_y = int(value)
        self.draw_illusion()

    def submit_data(self):
        if self.intersection is None:
            messagebox.showinfo('Error', 'Cannot calculate error, lines do not intersect')
            return

        absolute_error = (self.intersection - self.subject_response).magnitude()
        messagebox.showinfo('Error Calculation', f'ΔL = {absolute_error:.2f}')
    
        self.illusion_index += 1
        self.load_next_illusion()

        if self.illusion_index < len(self.illusions):
            self.slider.destroy()
            self.draw_illusion(sliderCreate=True)
            self.illNum += 1
            self.counter.configure(text=f'Test number {self.illNum + 1} out of {len(self.illusions)}')
        else:
            self.switchPage()

    def switchPage(self):
        self.stop_countdown()
        self.grid_forget()
        self.pack_forget()
        # Здесь вы можете добавить код для переключения на другую страницу, например:
        # newPage = testsPage.testsGUI(self.master, self.user_id, True, "Poggendorf Illusion")
        # newPage.grid(row=0, column=0, sticky="nsew")

    def stop_countdown(self):
        self.countdown_running = False

    def countdown(self, time_remaining):
        if self.timerOpt:
            if time_remaining > 0 and self.countdown_running:
                mins, secs = divmod(time_remaining, 60)
                timeformat = '{:02d}:{:02d}'.format(mins, secs)
                self.timer.configure(text=timeformat)
                self.after(1000, self.countdown, time_remaining - 1)
            elif not self.countdown_running:
                self.timer.configure(text="Timer stopped")
            else:
                self.timer.configure(text="Time's up!")
                self.times_up()
        else: 
            if self.countdown_running:
                mins, secs = divmod(time_remaining, 60)
                timeformat = '{:02d}:{:02d}'.format(mins, secs)
                self.timer.configure(text=timeformat)
                self.after(1000, self.countdown, time_remaining + 1)

    def times_up(self):
        messagebox.showinfo("Timer", "Time's up!")
