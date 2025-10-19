import tkinter as tk
import webview

def open_url():
    url = entry.get()
    if not url.startswith("http"):
        url = "http://" + url  # make sure it's a valid URL
    webview.create_window("Internet Explorer", url)
    webview.start()

root = tk.Tk()
root.title("URL Launcher")

label = tk.Label(root, text="Enter a URL:")
label.pack(pady=5)

entry = tk.Entry(root, width=40)
entry.pack(pady=5)

button = tk.Button(root, text="Open URL", command=open_url)
button.pack(pady=5)

root.mainloop()
