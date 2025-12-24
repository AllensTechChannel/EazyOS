from tkinter import *
from tkinter import messagebox, filedialog, colorchooser, simpledialog
from PIL import ImageGrab, Image, ImageTk
import os

from basic_canvas import CanvasWrapper
from shapes import ShapeManager
from toolbar import Toolbar


class PaintApp:
    def __init__(self, width=1400, height=800):
        self.root = Tk()
        self.root.title("EazyOS Paint")
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(False, False)

        # =========================================================
        # CANVAS + MANAGERS
        # =========================================================
        self.canvas_wrapper = CanvasWrapper(self.root, width, height - 120)
        self.canvas = self.canvas_wrapper.canvas
        self.shape_manager = ShapeManager(self.canvas, self.canvas_wrapper.push_undo)

        # =========================================================
        # TOOLBAR (now includes color callback)
        # =========================================================
        self.toolbar = Toolbar(
            self.root,
            self.canvas_wrapper,
            self.shape_manager,
            self.pick_color,
            self.brush_mode,
            self.eraser_mode,
            self.text_mode,
            self.bucket_mode,
            self.undo,
            self.redo,
            self.open_image,
            self.save_image,
            self.set_color              # NEW callback
        )

        # =========================================================
        # PAINT STATE
        # =========================================================
        self.current_color = "#000000"
        self.eraser_color = "#FFFFFF"
        self.brush_size = 3
        self.brush_active = True
        self.bucket_active = False
        self.text_active = False

        self.last_x = None
        self.last_y = None

        # Bind drawing
        self.canvas.bind("<B1-Motion>", self.brush_draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)

    # =====================================================
    # COLOR UPDATE CALLBACK (Used by toolbar)
    # =====================================================
    def set_color(self, color):
        self.current_color = color
        self.brush_active = True

    # =====================================================
    # BRUSH
    # =====================================================
    def brush_mode(self):
        self.brush_active = True
        self.bucket_active = False
        self.text_active = False

    def eraser_mode(self):
        self.current_color = self.eraser_color
        self.brush_active = True

    def brush_draw(self, event):
        if not self.brush_active:
            return

        if self.last_x is None:
            self.last_x, self.last_y = event.x, event.y
            return

        self.canvas.create_line(
            self.last_x, self.last_y, event.x, event.y,
            fill=self.current_color,
            width=self.brush_size,
            capstyle=ROUND
        )
        self.canvas_wrapper.push_undo()

        self.last_x, self.last_y = event.x, event.y

    def stop_draw(self, event):
        self.last_x = None
        self.last_y = None

    # =====================================================
    # TEXT TOOL
    # =====================================================
    def text_mode(self):
        self.text_active = True
        self.canvas.bind("<Button-1>", self.place_text)

    def place_text(self, event):
        if not self.text_active:
            return

        text = simpledialog.askstring("Text", "Enter text:")
        if not text:
            return

        self.canvas.create_text(event.x, event.y, text=text, fill=self.current_color)
        self.canvas_wrapper.push_undo()

    # =====================================================
    # COLOR PICKER
    # =====================================================
    def pick_color(self):
        def on_click(ev):
            x0 = self.canvas.winfo_rootx() + ev.x
            y0 = self.canvas.winfo_rooty() + ev.y
            pixel = ImageGrab.grab((x0, y0, x0 + 1, y0 + 1))
            r, g, b = pixel.getpixel((0, 0))
            self.current_color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.unbind("<Button-1>")
        self.canvas.bind("<Button-1>", on_click)

    # =====================================================
    # BUCKET / FLOOD FILL
    # =====================================================
    def bucket_mode(self):
        self.bucket_active = True
        self.brush_active = False
        self.text_active = False
        self.canvas.bind("<Button-1>", self.flood_fill_start)

    def flood_fill_start(self, event):
        self.canvas.unbind("<Button-1>")
        self.bucket_fill(event.x, event.y)

    def bucket_fill(self, x, y):
        cx = self.canvas.winfo_rootx()
        cy = self.canvas.winfo_rooty()
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        img = ImageGrab.grab((cx, cy, cx + w, cy + h))
        px = img.load()
        target = px[x, y]

        r_new, g_new, b_new = self.hex_to_rgb(self.current_color)

        if target == (r_new, g_new, b_new):
            return

        stack = [(x, y)]
        while stack:
            px_x, px_y = stack.pop()
            if px_x < 0 or px_x >= w or px_y < 0 or px_y >= h:
                continue
            if px[px_x, px_y] != target:
                continue

            px[px_x, px_y] = (r_new, g_new, b_new)
            stack.extend([(px_x + 1, px_y), (px_x - 1, px_y), (px_x, px_y + 1), (px_x, px_y - 1)])

        tk_img = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=tk_img, anchor="nw")
        self.canvas_wrapper._image_refs.append(tk_img)
        self.canvas_wrapper.push_undo()

    def hex_to_rgb(self, hexcolor):
        hexcolor = hexcolor.lstrip("#")
        return tuple(int(hexcolor[i:i+2], 16) for i in (0, 2, 4))

    # =====================================================
    # UNDO / REDO
    # =====================================================
    def undo(self):
        self.canvas_wrapper.undo()

    def redo(self):
        self.canvas_wrapper.redo()

    # =====================================================
    # FILE OPERATIONS
    # =====================================================
    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("All Files", "*.*")]
        )
        if not path:
            return

        img = Image.open(path).convert("RGBA")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        img = img.resize((w, h), Image.LANCZOS)

        tk_img = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=tk_img, anchor="nw")
        self.canvas_wrapper._image_refs.append(tk_img)
        self.canvas_wrapper.push_undo()

    def save_image(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png")]
        )
        if not path:
            return

        cx = self.canvas.winfo_rootx()
        cy = self.canvas.winfo_rooty()
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        img = ImageGrab.grab((cx, cy, cx + w, cy + h))
        img.save(path)

    # =====================================================
    # RUN
    # =====================================================
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    PaintApp().run()
