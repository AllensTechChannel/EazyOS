from tkinter import *
from PIL import ImageGrab, ImageTk

class CanvasWrapper:
    """
    Provides a stable canvas wrapper with:
    - Snapshot-based undo/redo
    - Transparent PNG support
    - Canvas restore function
    - Push-undo hooks for all tools
    """

    def __init__(self, root, width, height):
        self.root = root

        # Canvas container frame
        self.frame = Frame(root, bg="white")
        self.frame.pack(fill=BOTH, expand=False)

        # The actual drawing canvas
        self.canvas = Canvas(
            self.frame,
            width=width,
            height=height,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack()

        # Undo/redo stacks
        self.undo_stack = []
        self.redo_stack = []

        # Tkinter must keep references to these to avoid garbage collection
        self._image_refs = []

        # Push initial blank snapshot
        self.push_undo()

    # =====================================================
    # SNAPSHOT FUNCTIONS
    # =====================================================
    def snapshot_canvas(self):
        """Captures the canvas as an image object."""
        self.canvas.update()

        x = self.canvas.winfo_rootx()
        y = self.canvas.winfo_rooty()
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        img = ImageGrab.grab((x, y, x + w, y + h))
        return img

    def push_undo(self):
        """Stores a snapshot in undo history."""
        img = self.snapshot_canvas()
        self.undo_stack.append(img)
        self.redo_stack.clear()  # clear redo when drawing

    # =====================================================
    # RESTORE SNAPSHOT
    # =====================================================
    def restore_from_image(self, img):
        """Restores a canvas from an image snapshot."""
        tk_img = ImageTk.PhotoImage(img)

        # Clear screen then draw image
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=tk_img, anchor="nw")

        # Keep reference alive
        self._image_refs.append(tk_img)

        self.canvas.update()

    # =====================================================
    # UNDO / REDO
    # =====================================================
    def undo(self):
        if len(self.undo_stack) > 1:
            last_img = self.undo_stack.pop()  # remove current
            self.redo_stack.append(last_img)

            img = self.undo_stack[-1]
            self.restore_from_image(img)

    def redo(self):
        if self.redo_stack:
            img = self.redo_stack.pop()
            self.undo_stack.append(img)
            self.restore_from_image(img)
