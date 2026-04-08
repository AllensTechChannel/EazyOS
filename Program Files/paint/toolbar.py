from tkinter import *
from PIL import Image, ImageTk
import os


class Toolbar:
    """
    Windows 7–style MS Paint toolbar.
    Now includes a callback to change the brush color in main.py.
    """

    def __init__(
        self,
        root,
        canvas_wrapper,
        shape_manager,
        pick_color,
        brush_mode,
        eraser_mode,
        text_mode,
        bucket_mode,
        undo,
        redo,
        open_image,
        save_image,
        set_color_callback         # NEW
    ):
        self.root = root
        self.canvas_wrapper = canvas_wrapper
        self.shape_manager = shape_manager

        # callbacks
        self.pick_color = pick_color
        self.brush_mode = brush_mode
        self.eraser_mode = eraser_mode
        self.text_mode = text_mode
        self.bucket_mode = bucket_mode
        self.undo = undo
        self.redo = redo
        self.open_image = open_image
        self.save_image = save_image
        self.set_color_callback = set_color_callback  # NEW

        self.icons = {}

        self.bar = Frame(root, height=120, bg="#e5e5e5")
        self.bar.pack(fill=X, side=TOP)

        self.build_file_section()
        self.build_tools_section()
        self.build_shapes_section()
        self.build_color_section()

    # ========== Icon loader ==========
    def load_icon(self, name, size=(32, 32)):
        path = os.path.join("pics", name)
        if os.path.exists(path):
            img = Image.open(path).resize(size, Image.LANCZOS)
            icon = ImageTk.PhotoImage(img)
            self.icons[name] = icon
            return icon
        return None

    # ========== File ==========
    def build_file_section(self):
        frame = Frame(self.bar, bg="#d7d7d7", bd=1, relief=GROOVE, padx=5, pady=5)
        frame.pack(side=LEFT, padx=5)

        Label(frame, text="File", bg="#d7d7d7").pack()

        def add_btn(txt, icon, cmd):
            Button(frame, text=(txt if not icon else ""),
                   image=icon,
                   compound=TOP,
                   width=60, height=60,
                   command=cmd).pack(pady=2)

        add_btn("Open", self.load_icon("open.png"), self.open_image)
        add_btn("Save", self.load_icon("save.png"), self.save_image)

    # ========== Tools ==========
    def build_tools_section(self):
        frame = Frame(self.bar, bg="#d7d7d7", bd=1, relief=GROOVE, padx=5, pady=5)
        frame.pack(side=LEFT, padx=5)

        Label(frame, text="Tools", bg="#d7d7d7").pack()

        def add(txt, icon, cmd):
            Button(frame, text=(txt if not icon else ""), image=icon, compound=TOP,
                   width=60, height=60, command=cmd).pack(side=LEFT, padx=3)

        add("Brush", self.load_icon("brush.png"), self.brush_mode)
        add("Eraser", self.load_icon("eraser.png"), self.eraser_mode)
        add("Fill", self.load_icon("bucket.png"), self.bucket_mode)
        add("Text", self.load_icon("text.png"), self.text_mode)
        add("Pick", self.load_icon("picker.png"), self.pick_color)
        add("Undo", self.load_icon("undo.png"), self.undo)
        add("Redo", self.load_icon("redo.png"), self.redo)

    # ========== Shapes ==========
    def build_shapes_section(self):
        frame = Frame(self.bar, bg="#d7d7d7", bd=1, relief=GROOVE, padx=5, pady=5)
        frame.pack(side=LEFT, padx=5)

        Label(frame, text="Shapes", bg="#d7d7d7").pack()

        def bind_shape(draw_func):
            canvas = self.canvas_wrapper.canvas
            canvas.bind("<Button-1>", self.shape_manager.begin)
            canvas.bind("<B1-Motion>", lambda e: draw_func(e))
            canvas.bind("<ButtonRelease-1>", self.shape_manager.end)

        def add(txt, icon, func):
            Button(frame, text=(txt if not icon else ""), image=icon, compound=TOP,
                   width=60, height=60,
                   command=lambda: bind_shape(func)
                   ).pack(side=LEFT, padx=3)

        add("Rect", self.load_icon("rectangle.png"),
            lambda e: self.shape_manager.rectangle(e, "black", 2))

        add("Circle", self.load_icon("circle.png"),
            lambda e: self.shape_manager.circle(e, "black", 2))

        add("Tri", self.load_icon("triangle.png"),
            lambda e: self.shape_manager.triangle(e, "black", 2))

    # ========== Colors ==========
    def build_color_section(self):
        frame = Frame(self.bar, bg="#d7d7d7", bd=1, relief=GROOVE, padx=5, pady=5)
        frame.pack(side=LEFT, padx=5)

        Label(frame, text="Colors", bg="#d7d7d7").pack()

        colors = [
            "#000000", "#444444", "#888888", "#CCCCCC",
            "#FF0000", "#FFA500", "#FFFF00", "#008000",
            "#00FFFF", "#0000FF", "#800080", "#FF00FF"
        ]

        def choose(color):
            self.set_color_callback(color)

        for c in colors:
            Button(
                frame, bg=c, width=3, height=1,
                command=lambda col=c: choose(col)
            ).pack(side=LEFT, padx=2)
