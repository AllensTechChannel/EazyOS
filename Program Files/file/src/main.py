import tkinter as tk
from tkinter import messagebox as mb
from tkinter import filedialog as fd
import os
import shutil

# ── Windows 98 palette ──────────────────────────────────────────────
WIN98_BG        = "#C0C0C0"   # classic silver
WIN98_TITLE_BG  = "#000080"   # navy title bar
WIN98_TITLE_FG  = "#FFFFFF"
WIN98_BTN_BG    = "#C0C0C0"
WIN98_BTN_FG    = "#000000"
WIN98_SUNKEN_BG = "#FFFFFF"
WIN98_DARK      = "#808080"
WIN98_DARKER    = "#404040"
WIN98_WHITE     = "#FFFFFF"
WIN98_HIGHLIGHT = "#000080"

FONT_MAIN  = ("MS Sans Serif", 8)
FONT_TITLE = ("MS Sans Serif", 8, "bold")
FONT_BTN   = ("MS Sans Serif", 8)

# ── Beveled / raised-relief helper ─────────────────────────────────
def make_win98_button(parent, text, command, width=22):
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        font=FONT_BTN,
        bg=WIN98_BTN_BG,
        fg=WIN98_BTN_FG,
        activebackground=WIN98_BG,
        activeforeground=WIN98_BTN_FG,
        relief="raised",
        bd=2,
        width=width,
        cursor="arrow",
        highlightthickness=0,
    )
    # Simulate Win98 press effect
    def on_press(e):
        btn.config(relief="sunken")
    def on_release(e):
        btn.config(relief="raised")
    btn.bind("<ButtonPress-1>", on_press)
    btn.bind("<ButtonRelease-1>", on_release)
    return btn


def make_win98_frame(parent, label=None):
    """Etched group-box frame."""
    outer = tk.Frame(parent, bg=WIN98_BG, bd=2, relief="groove")
    if label:
        lbl = tk.Label(outer, text=label, font=FONT_MAIN, bg=WIN98_BG, fg=WIN98_BTN_FG)
        lbl.pack(anchor="nw", padx=6, pady=(2, 0))
    return outer


def win98_titlebar(parent, title, icon="📁"):
    bar = tk.Frame(parent, bg=WIN98_TITLE_BG, height=20)
    bar.pack(fill="x")
    bar.pack_propagate(False)
    lbl = tk.Label(
        bar, text=f"  {icon}  {title}", font=FONT_TITLE,
        bg=WIN98_TITLE_BG, fg=WIN98_TITLE_FG, anchor="w"
    )
    lbl.pack(side="left", fill="y", padx=2)
    # Fake close button
    close = tk.Label(
        bar, text=" × ", font=("MS Sans Serif", 8, "bold"),
        bg=WIN98_BG, fg=WIN98_BTN_FG, relief="raised", bd=2, cursor="arrow"
    )
    close.pack(side="right", padx=2, pady=1)
    return bar


# ── Feature functions ───────────────────────────────────────────────

def openAFile():
    files = fd.askopenfilename(
        title="Open", filetypes=[("All files", "*.*")]
    )
    if files:
        os.startfile(os.path.abspath(files))


def copyAFile():
    src = fd.askopenfilename(title="Select file to copy", filetypes=[("All files", "*.*")])
    if not src:
        return
    dst = fd.askdirectory(title="Select destination folder")
    if not dst:
        return
    try:
        shutil.copy(src, dst)
        mb.showinfo("File Manager", "The file has been copied successfully.")
    except Exception as e:
        mb.showerror("Error", f"Could not copy file:\n{e}")


def deleteAFile():
    files = fd.askopenfilename(title="Select file to delete", filetypes=[("All files", "*.*")])
    if not files:
        return
    if mb.askyesno("Confirm Delete", f"Are you sure you want to delete:\n{os.path.basename(files)}?"):
        try:
            os.remove(os.path.abspath(files))
            mb.showinfo("File Manager", "The file has been deleted.")
        except Exception as e:
            mb.showerror("Error", f"Could not delete file:\n{e}")


def renameAFile():
    rename_win = tk.Toplevel(win_root)
    rename_win.title("Rename File")
    rename_win.geometry("310x140+400+300")
    rename_win.resizable(False, False)
    rename_win.configure(bg=WIN98_BG)
    rename_win.grab_set()

    win98_titlebar(rename_win, "Rename File", icon="✏️")

    body = tk.Frame(rename_win, bg=WIN98_BG)
    body.pack(fill="both", expand=True, padx=10, pady=8)

    tk.Label(body, text="New file name (without extension):",
             font=FONT_MAIN, bg=WIN98_BG).pack(anchor="w", pady=(4, 2))

    entry_var = tk.StringVar()
    entry = tk.Entry(
        body, textvariable=entry_var, font=FONT_MAIN,
        bg=WIN98_SUNKEN_BG, fg="#000000", relief="sunken", bd=2, width=32
    )
    entry.pack(fill="x", pady=2)
    entry.focus_set()

    btn_row = tk.Frame(body, bg=WIN98_BG)
    btn_row.pack(pady=8)

    def do_rename():
        new_name = entry_var.get().strip()
        if not new_name:
            mb.showwarning("Rename", "Please enter a file name.", parent=rename_win)
            return
        files = fd.askopenfilename(title="Select file to rename", filetypes=[("All files", "*.*")])
        if not files:
            return
        ext = os.path.splitext(files)[1]
        new_path = os.path.join(os.path.dirname(files), new_name + ext)
        try:
            os.rename(files, new_path)
            mb.showinfo("File Manager", "File renamed successfully.", parent=rename_win)
            rename_win.destroy()
        except Exception as e:
            mb.showerror("Error", f"Could not rename file:\n{e}", parent=rename_win)

    ok_btn = make_win98_button(btn_row, "OK", do_rename, width=10)
    ok_btn.pack(side="left", padx=4)
    cancel_btn = make_win98_button(btn_row, "Cancel", rename_win.destroy, width=10)
    cancel_btn.pack(side="left", padx=4)


def openAFolder():
    folder = fd.askdirectory(title="Select folder to open")
    if folder:
        os.startfile(folder)


def deleteAFolder():
    folder = fd.askdirectory(title="Select folder to delete")
    if not folder:
        return
    if mb.askyesno("Confirm Delete", f"Delete this folder?\n{folder}"):
        try:
            os.rmdir(folder)
            mb.showinfo("File Manager", "Folder deleted.")
        except Exception as e:
            mb.showerror("Error", f"Could not delete folder:\n{e}")


def moveAFolder():
    src = fd.askdirectory(title="Select folder to move")
    if not src:
        return
    mb.showinfo("Move Folder", "Folder selected. Now choose the destination.")
    dst = fd.askdirectory(title="Select destination")
    if not dst:
        return
    try:
        shutil.move(src, dst)
        mb.showinfo("File Manager", "Folder moved successfully.")
    except Exception as e:
        mb.showerror("Error", f"Could not move folder:\n{e}")


def listFilesInFolder():
    folder = fd.askdirectory(title="Select folder to list")
    if not folder:
        return
    files = os.listdir(os.path.abspath(folder))

    list_win = tk.Toplevel(win_root)
    list_win.title("Directory Listing")
    list_win.geometry("360x480+420+200")
    list_win.resizable(False, False)
    list_win.configure(bg=WIN98_BG)

    win98_titlebar(list_win, f"Contents of: {os.path.basename(folder)}", icon="📂")

    # Address bar
    addr_frame = tk.Frame(list_win, bg=WIN98_BG)
    addr_frame.pack(fill="x", padx=6, pady=(6, 2))
    tk.Label(addr_frame, text="Folder:", font=FONT_MAIN, bg=WIN98_BG).pack(side="left")
    addr_entry = tk.Entry(
        addr_frame, font=FONT_MAIN, bg=WIN98_SUNKEN_BG,
        relief="sunken", bd=2, fg="#000080"
    )
    addr_entry.insert(0, folder)
    addr_entry.config(state="readonly")
    addr_entry.pack(side="left", fill="x", expand=True, padx=(4, 0))

    # Status label
    status_var = tk.StringVar(value=f"{len(files)} object(s)")

    # Listbox with scrollbar
    lb_frame = tk.Frame(list_win, bg=WIN98_BG, bd=2, relief="sunken")
    lb_frame.pack(fill="both", expand=True, padx=6, pady=4)

    scrollbar = tk.Scrollbar(lb_frame, orient="vertical")
    listbox = tk.Listbox(
        lb_frame,
        font=FONT_MAIN,
        bg=WIN98_SUNKEN_BG,
        fg="#000000",
        selectbackground=WIN98_HIGHLIGHT,
        selectforeground=WIN98_WHITE,
        bd=0,
        highlightthickness=0,
        yscrollcommand=scrollbar.set,
    )
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side="right", fill="y")
    listbox.pack(side="left", fill="both", expand=True)

    for i, f in enumerate(sorted(files)):
        icon = "📁 " if os.path.isdir(os.path.join(folder, f)) else "📄 "
        listbox.insert("end", f"  {icon}{f}")

    # Status bar
    status_bar = tk.Frame(list_win, bg=WIN98_BG, bd=1, relief="sunken", height=20)
    status_bar.pack(fill="x", side="bottom")
    tk.Label(status_bar, textvariable=status_var, font=FONT_MAIN,
             bg=WIN98_BG, anchor="w").pack(side="left", padx=4)

    close_btn = make_win98_button(list_win, "Close", list_win.destroy, width=10)
    close_btn.pack(pady=6)


# ── Main window ─────────────────────────────────────────────────────

if __name__ == "__main__":
    win_root = tk.Tk()
    win_root.title("File Manager")
    win_root.geometry("800x900")
    win_root.resizable(True,True)
    win_root.configure(bg=WIN98_BG)

    # Custom title bar look (inside Tk frame)
    win98_titlebar(win_root, "File Manager", icon="📁")

    # ── Menu bar simulation ─────────────────────────────────────────
    menubar_frame = tk.Frame(win_root, bg=WIN98_BG, bd=0)
    menubar_frame.pack(fill="x", padx=2)
    for item in ["File", "Edit", "View", "Help"]:
        lbl = tk.Label(
            menubar_frame, text=item, font=FONT_MAIN,
            bg=WIN98_BG, fg="#000000", padx=6, pady=1,
            cursor="arrow"
        )
        lbl.pack(side="left")
        lbl.bind("<Enter>", lambda e, l=lbl: l.config(bg=WIN98_HIGHLIGHT, fg=WIN98_WHITE))
        lbl.bind("<Leave>", lambda e, l=lbl: l.config(bg=WIN98_BG, fg="#000000"))

    # ── Toolbar separator ────────────────────────────────────────────
    sep = tk.Frame(win_root, bg=WIN98_DARK, height=1)
    sep.pack(fill="x")
    sep2 = tk.Frame(win_root, bg=WIN98_WHITE, height=1)
    sep2.pack(fill="x")

    # ── File operations group ────────────────────────────────────────
    file_group = make_win98_frame(win_root, "  File Operations  ")
    file_group.pack(fill="x", padx=8, pady=(8, 4))

    for label, cmd in [
        ("📄  Open a File",    openAFile),
        ("✏️   Rename a File",  renameAFile),
        ("📋  Copy a File",    copyAFile),
        ("🗑️   Delete a File",  deleteAFile),
    ]:
        btn = make_win98_button(file_group, label, cmd, width=24)
        btn.pack(pady=3, padx=8)

    # ── Folder operations group ──────────────────────────────────────
    folder_group = make_win98_frame(win_root, "  Folder Operations  ")
    folder_group.pack(fill="x", padx=8, pady=4)

    for label, cmd in [
        ("📂  Open a Folder",    openAFolder),
        ("🗑️   Delete a Folder",  deleteAFolder),
        ("🚚  Move a Folder",     moveAFolder),
        ("📋  List Files",        listFilesInFolder),
    ]:
        btn = make_win98_button(folder_group, label, cmd, width=24)
        btn.pack(pady=3, padx=8)

    # ── Status bar ───────────────────────────────────────────────────
    sep3 = tk.Frame(win_root, bg=WIN98_DARK, height=1)
    sep3.pack(fill="x", side="bottom")
    status = tk.Frame(win_root, bg=WIN98_BG, height=20)
    status.pack(fill="x", side="bottom")
    status.pack_propagate(False)
    tk.Label(
        status, text="Ready", font=FONT_MAIN,
        bg=WIN98_BG, fg="#000000", anchor="w"
    ).pack(side="left", padx=6)

    win_root.mainloop()