import tkinter as tk
from tkinter import messagebox
from utils.geometry_utils import Vector2D, Line, Circle, pixel_to_mm

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
            "alpha": -13,
            "circle_fill": ["blue", "blue", "red"],
            "circle_outline": ["black", "black", "black"],
            "repeat": 2
        },
        {
            "r_param": 24,
            "d_param": 63,
            "alpha": 24,
            "circle_fill": ["blue", "blue", "red"],
            "circle_outline": ["black", "black", "black"],
            "repeat": 2
        }
    ]
    illNum = 0
    r_param = 10
    d_param = 45
    alpha = 0
    desired_point = Vector2D(4 * r_param + 2 * d_param, 128)
    subject_response = Vector2D(0, 0)
    user_id = None
    circles_fill = ['blue', 'blue', 'red']
    circles_outline = ['black', 'black', 'black']

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

        # Load the first illusion
        self.load_next_illusion()

        # Timer (not needed, but kept for completeness)
        self.timer = tk.Label(self, font=('Helvetica', 48), text="15:00")
        self.timer.grid(row=0, column=0, sticky='nsew')
        self.timer.grid_forget()
        self.countdown_running = False

        # Create canvas
        self.canvas = tk.Canvas(self, width=512, height=512)
        self.canvas.grid(row=1, column=0, sticky='nsew')

        # Configure the row and column weights where the canvas is placed
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.draw_illusion()

        self.counter = tk.Label(self, text=self.illNum)
        self.counter.grid()

        # Create slider to adjust the circle position
        self.slider = tk.Scale(self, from_=256 - self.d_param, to=0, orient='horizontal', command=self.adjust_circle)
        self.slider.set(70)
        self.slider.grid()
        
        self.NextButton = tk.Button(self, text='Submit', command=self.submit_data)
        self.NextButton.grid()

    def load_next_illusion(self):
        if self.illNum < len(self.illusions):
            illusion = self.illusions[self.illNum]
            self.r_param = illusion["r_param"]
            self.d_param = illusion["d_param"]
            self.alpha = illusion["alpha"]
            self.circles_fill = illusion["circle_fill"]
            self.circles_outline = illusion["circle_outline"]
        else:
            self.switchPage()

    def draw_illusion(self, circle_pos=0):
        self.canvas.delete('all')

        self.ill_center = Vector2D(128, 128)
        self.desired_point = Vector2D(3 * self.r_param + 2 * self.d_param, 128)
        
        # calculate the position of the circles
        first_circle_pos = Vector2D(self.r_param, self.ill_center.y)
        second_circle_pos = Vector2D(self.r_param + self.d_param, self.ill_center.y)
        third_circle_pos = Vector2D(256 - self.r_param - 2 - circle_pos, self.ill_center.y)

        # draw the circles
        first_circle = Circle(first_circle_pos, self.r_param)
        second_circle = Circle(second_circle_pos, self.r_param)
        third_circle = Circle(third_circle_pos, self.r_param)

        first_circle.rotate_around_point(self.alpha, self.ill_center)
        second_circle.rotate_around_point(self.alpha, self.ill_center)
        third_circle.rotate_around_point(self.alpha, self.ill_center)

        self.subject_response = third_circle_pos

        first_circle.draw(self.canvas, color=self.circles_outline[0], fill=self.circles_fill[0], width=1)
        second_circle.draw(self.canvas, color=self.circles_outline[1], fill=self.circles_fill[1], width=1)
        third_circle.draw(self.canvas, color=self.circles_outline[2], fill=self.circles_fill[2], width=1)

        self.canvas.scale('all', 0, 0, 2, 2)

    def adjust_alpha(self, value):
        self.alpha = int(value)
        self.draw_illusion()

    def adjust_d(self, value):
        self.d_param = int(value)
        self.draw_illusion()

    def adjust_r(self, value):
        self.r_param = int(value)
        self.draw_illusion()

    def adjust_circle(self, value):
        self.draw_illusion(int(value))

    def submit_data(self):
        dpi = self.winfo_fpixels('1i')
        
        # Calculate the error in pixels and mm
        absolute_error = (self.desired_point - self.subject_response).magnitude()
        max_error_pixel = (self.desired_point - Vector2D(256 - self.r_param - 2, self.ill_center.y)).magnitude()
        
        absolute_error_mm = pixel_to_mm(absolute_error, dpi, 2)  # 2 is a magic number, it is the scale of the illusion
        max_error_mm = pixel_to_mm(max_error_pixel, dpi, 2)  # 2 is a magic number, it is the scale of the illusion

        print(f'ΔS = {absolute_error:.2f} pixels ({absolute_error_mm:.2f} mm)')
    
        self.illNum += 1
        self.load_next_illusion()

        if self.illNum < len(self.illusions):
            self.draw_illusion()
            self.counter.configure(text=self.illNum)
        else:
            self.switchPage()

    def switchPage(self):
        self.stop_countdown()
        self.grid_forget()
        tk.Label(self.master, text="Test completed").grid(row=0, column=0, sticky="nsew")

    def stop_countdown(self):
        self.countdown_running = False

    def countdown(self, time_remaining):
        if time_remaining > 0 and self.countdown_running:
            mins, secs = divmod(time_remaining, 60)
            timeformat = '{:02d}:{:02d}'.format(mins, secs)
            self.timer.configure(text=timeformat)
            self.after(1000, self.countdown, time_remaining-1)
        elif not self.countdown_running:
            self.timer.configure(text="Timer stopped")
        else:
            self.timer.configure(text="Time's up!")
            self.times_up()

    def times_up(self):
        messagebox.showinfo("Timer", "Time's up!")
