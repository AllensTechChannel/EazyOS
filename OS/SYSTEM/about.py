import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import tkinter.font as tkFont

root = tk.Tk()
root.title("About EazyOS")
root.geometry("480x480")
root.resizable(False, False)

# --- Image ---
img = Image.open("python-logo.png")
tk_img = ImageTk.PhotoImage(img)
image_label = tk.Label(root, image=tk_img)
image_label.image = tk_img  # prevent garbage collection
image_label.pack(pady=5)
# --- Divider line ---
horizontal_line = tk.Frame(root, height=1, bg="black")
horizontal_line.pack(fill="x", padx=10, pady=10)
# --- Title ---
title_font = tkFont.Font(family="Arial", size=20)
ttk.Label(root, text="EazyOS 3", font=title_font).pack(padx=10)

# --- Divider line ---
horizontal_line = tk.Frame(root, height=1, bg="black")
horizontal_line.pack(fill="x", padx=10, pady=10)

# --- Version info ---
info_font = tkFont.Font(family="Arial", size=10)
ttk.Label(root, text="Version: EazyOS 3.2 Pre-Release Version 1", font=info_font).pack(pady=2,padx=10)
# --- Divider line ---
horizontal_line = tk.Frame(root, height=1, bg="gray")
horizontal_line.pack(fill="x", padx=40, pady=10)

ttk.Label(root, text="Made Possible By: Python 3.14.5", font=info_font).pack(pady=2,padx=10)

# --- Divider line ---
horizontal_line = tk.Frame(root, height=1, bg="gray")
horizontal_line.pack(fill="x", padx=40, pady=10)

ttk.Label(root, text="Copyright: All programs and icons are property of their respective owners.",
          font=info_font, wraplength=400, justify="center").pack(pady=2,padx=10)

horizontal_line = tk.Frame(root, height=1, bg="gray")
horizontal_line.pack(fill="x", padx=40, pady=10)


# --- OK button ---
bottom_button = tk.Button(root, text="OK", command=root.destroy)
bottom_button.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)

root.mainloop()

