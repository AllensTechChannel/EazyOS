from tkinter import *
import math


class ShapeManager:
    """
    Central controller for drawing all shapes.
    Allows:
    - Rectangle
    - Square
    - Oval
    - Circle
    - Line Arrow
    - Triangle
    - Pentagon
    - Hexagon
    - Octagon
    - Custom N-Polygon
    """

    def __init__(self, canvas, push_undo_callback):
        self.canvas = canvas
        self.push_undo = push_undo_callback

        # draw state
        self.start_x = None
        self.start_y = None
        self.temp_shape = None

        # number of polygon points
        self.n_polygon_points = 6

    # =====================================================
    # START DRAW
    # =====================================================
    def begin(self, event):
        self.start_x = event.x
        self.start_y = event.y

    # =====================================================
    # END DRAW
    # =====================================================
    def end(self, event):
        if self.temp_shape:
            self.push_undo()
        self.temp_shape = None
        self.start_x = None
        self.start_y = None

    # =====================================================
    # GENERIC DRAW WRAPPER
    # =====================================================
    def draw_temp(self, event, create_func):
        """Deletes the last temp shape and redraws."""
        if self.temp_shape:
            self.canvas.delete(self.temp_shape)

        self.temp_shape = create_func(event)

    # =====================================================
    # RECTANGLE
    # =====================================================
    def rectangle(self, event, color, width):
        def create(event):
            return self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y,
                outline=color,
                width=width
            )
        self.draw_temp(event, create)

    # =====================================================
    # SQUARE
    # =====================================================
    def square(self, event, color, width):
        def create(event):
            side = max(abs(event.x - self.start_x), abs(event.y - self.start_y))

            # determine correct direction
            x2 = self.start_x + side if event.x >= self.start_x else self.start_x - side
            y2 = self.start_y + side if event.y >= self.start_y else self.start_y - side

            return self.canvas.create_rectangle(
                self.start_x, self.start_y, x2, y2,
                outline=color,
                width=width
            )
        self.draw_temp(event, create)

    # =====================================================
    # OVAL
    # =====================================================
    def oval(self, event, color, width):
        def create(event):
            return self.canvas.create_oval(
                self.start_x, self.start_y, event.x, event.y,
                outline=color,
                width=width
            )
        self.draw_temp(event, create)

    # =====================================================
    # CIRCLE
    # =====================================================
    def circle(self, event, color, width):
        def create(event):
            radius = int(((event.x - self.start_x) ** 2 + (event.y - self.start_y) ** 2) ** 0.5)

            return self.canvas.create_oval(
                self.start_x - radius,
                self.start_y - radius,
                self.start_x + radius,
                self.start_y + radius,
                outline=color,
                width=width
            )
        self.draw_temp(event, create)

    # =====================================================
    # TRIANGLE
    # =====================================================
    def triangle(self, event, color, width):
        def create(event):
            return self.canvas.create_polygon(
                self.start_x, self.start_y,   # top
                event.x, event.y,             # bottom right
                self.start_x - (event.x - self.start_x), event.y,  # bottom left
                outline=color,
                fill="",
                width=width
            )
        self.draw_temp(event, create)

    # =====================================================
    # PENTAGON
    # =====================================================
    def pentagon(self, event, color, width):
        def create(event):
            radius = int(((event.x - self.start_x) ** 2 + (event.y - self.start_y) ** 2) ** 0.5)
            points = []
            for i in range(5):
                ang = math.radians(90 + 72 * i)
                x = self.start_x + radius * math.cos(ang)
                y = self.start_y - radius * math.sin(ang)
                points.extend((x, y))
            return self.canvas.create_polygon(points, outline=color, fill="", width=width)
        self.draw_temp(event, create)

    # =====================================================
    # HEXAGON
    # =====================================================
    def hexagon(self, event, color, width):
        def create(event):
            radius = int(((event.x - self.start_x) ** 2 + (event.y - self.start_y) ** 2) ** 0.5)
            points = []
            for i in range(6):
                ang = math.radians(90 + 60 * i)
                x = self.start_x + radius * math.cos(ang)
                y = self.start_y - radius * math.sin(ang)
                points.extend((x, y))
            return self.canvas.create_polygon(points, outline=color, fill="", width=width)
        self.draw_temp(event, create)

    # =====================================================
    # OCTAGON
    # =====================================================
    def octagon(self, event, color, width):
        def create(event):
            radius = int(((event.x - self.start_x) ** 2 + (event.y - self.start_y) ** 2) ** 0.5)
            points = []
            for i in range(8):
                ang = math.radians(90 + 45 * i)
                x = self.start_x + radius * math.cos(ang)
                y = self.start_y - radius * math.sin(ang)
                points.extend((x, y))
            return self.canvas.create_polygon(points, outline=color, fill="", width=width)
        self.draw_temp(event, create)

    # =====================================================
    # N-POLYGON (Custom)
    # =====================================================
    def n_polygon(self, event, color, width):
        def create(event):
            radius = int(((event.x - self.start_x) ** 2 + (event.y - self.start_y) ** 2) ** 0.5)
            points = []
            for i in range(self.n_polygon_points):
                ang = math.radians(90 + (360 / self.n_polygon_points) * i)
                x = self.start_x + radius * math.cos(ang)
                y = self.start_y - radius * math.sin(ang)
                points.extend((x, y))
            return self.canvas.create_polygon(points, outline=color, fill="", width=width)
        self.draw_temp(event, create)

    # =====================================================
    # ARROW LINE
    # =====================================================
    def arrow(self, event, color, width):
        def create(event):
            return self.canvas.create_line(
                self.start_x, self.start_y, event.x, event.y,
                arrow=LAST,
                fill=color,
                width=width
            )
        self.draw_temp(event, create)
