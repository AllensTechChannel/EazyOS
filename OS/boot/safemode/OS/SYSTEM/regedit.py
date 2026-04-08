import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# === PATH CONFIGURATION ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "..", "eazyos_config.json")


class RegEdit:
    def __init__(self, root):
        self.root = root
        self.root.title("Registry Editor")
        self.root.geometry("700x450")
        self.root.configure(bg="#C0C0C0")

        self.config_data = self.load_config()
        self._current_path = []

        # Menu Bar
        self.setup_menu()

        # Paned Window
        self.paned = tk.PanedWindow(self.root, orient="horizontal", bg="#808080", bd=1)
        self.paned.pack(fill="both", expand=True)

        # Left Side: Treeview (The Keys)
        self.tree = ttk.Treeview(self.paned, selectmode="browse")
        self.tree.heading("#0", text="My Computer", anchor="w")
        self.paned.add(self.tree, width=250)

        # Right Side: Value Editor
        self.right_container = tk.Frame(self.paned, bg="white", relief="sunken", bd=2)
        self.paned.add(self.right_container)

        self.setup_editor_ui()

        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = tk.Label(
            self.root, textvariable=self.status_var, bd=1,
            relief="sunken", anchor="w", font=("MS Sans Serif", 8)
        )
        self.status_bar.pack(side="bottom", fill="x")

        self.populate_tree("", self.config_data)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    # ------------------------------------------------------------------ #
    #  MENU                                                                #
    # ------------------------------------------------------------------ #
    def setup_menu(self):
        menu_bar = tk.Menu(self.root)

        reg_menu = tk.Menu(menu_bar, tearoff=0)
        reg_menu.add_command(label="Export Registry File...", command=self.save_to_disk)
        reg_menu.add_separator()
        reg_menu.add_command(label="Exit", command=self.root.destroy)

        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="New Key", command=self.new_key)
        edit_menu.add_command(label="Delete", accelerator="Del", command=self.delete_key)

        menu_bar.add_cascade(label="Registry", menu=reg_menu)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        menu_bar.add_cascade(label="View", menu=tk.Menu(menu_bar, tearoff=0))
        menu_bar.add_cascade(label="Help", menu=tk.Menu(menu_bar, tearoff=0))
        self.root.config(menu=menu_bar)
        self.root.bind("<Delete>", lambda e: self.delete_key())

    # ------------------------------------------------------------------ #
    #  RIGHT-PANEL UI                                                      #
    # ------------------------------------------------------------------ #
    def setup_editor_ui(self):
        tk.Label(
            self.right_container, text="Select a key to edit",
            bg="white", font=("MS Sans Serif", 8)
        ).pack(pady=10)

        edit_frame = tk.Frame(self.right_container, bg="white")
        edit_frame.pack(fill="x", padx=20)

        # Value Name
        tk.Label(edit_frame, text="Value Name:", bg="white",
                 font=("MS Sans Serif", 8)).grid(row=0, column=0, sticky="e", padx=5)
        self.val_name_var = tk.StringVar()
        self.name_entry = tk.Entry(
            edit_frame, textvariable=self.val_name_var,
            state="readonly", bg="#F0F0F0", font=("MS Sans Serif", 8)
        )
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=5)

        # Value Data
        tk.Label(edit_frame, text="Value Data:", bg="white",
                 font=("MS Sans Serif", 8)).grid(row=1, column=0, sticky="e", padx=5)
        self.val_data_var = tk.StringVar()
        self.data_entry = tk.Entry(
            edit_frame, textvariable=self.val_data_var,
            font=("MS Sans Serif", 8)
        )
        self.data_entry.grid(row=1, column=1, sticky="ew", pady=5)

        edit_frame.columnconfigure(1, weight=1)

        btn_frame = tk.Frame(self.right_container, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame, text="Modify", command=self.update_value,
            bg="#C0C0C0", relief="raised", padx=10, font=("MS Sans Serif", 8)
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="Save All", command=self.save_to_disk,
            bg="#C0C0C0", relief="raised", padx=10, font=("MS Sans Serif", 8)
        ).pack(side="left", padx=5)

    # ------------------------------------------------------------------ #
    #  CONFIG I/O                                                          #
    # ------------------------------------------------------------------ #
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        # Sensible defaults if no file found
        return {
            "theme": {
                "type": "color",
                "color": "#008080",
                "wallpaper": "",
                "taskbar_color": "#c0c0c0",
                "window_title_color": "#000080",
            },
            "system": {
                "startup_sound": "true",
                "enable_sounds": "true",
                "show_clock": "true",
                "auto_hide_windows_taskbar": "true",
            }
        }

    def save_to_disk(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config_data, f, indent=4)
            self.status_var.set("Saved successfully — EazyOS will apply changes within 2 seconds.")
            self.root.after(3000, lambda: self.status_var.set("Ready"))
            messagebox.showinfo(
                "RegEdit",
                "Registry saved.\n\nEazyOS will automatically apply the new settings within 2 seconds."
            )
        except Exception as e:
            messagebox.showerror("RegEdit", f"Failed to save registry:\n{e}")

    # ------------------------------------------------------------------ #
    #  TREE POPULATION                                                     #
    # ------------------------------------------------------------------ #
    def populate_tree(self, parent, data):
        for key, value in data.items():
            node = self.tree.insert(parent, "end", text=key, open=True)
            if isinstance(value, dict):
                self.populate_tree(node, value)

    def refresh_tree(self):
        """Wipe and repopulate the tree from current config_data."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.populate_tree("", self.config_data)

    # ------------------------------------------------------------------ #
    #  SELECTION                                                           #
    # ------------------------------------------------------------------ #
    def on_tree_select(self, event):
        item = self.tree.focus()
        path = self.get_path(item)
        self._current_path = path
        self.status_var.set("My Computer\\" + "\\".join(path))

        val = self.config_data
        for p in path:
            if isinstance(val, dict):
                val = val.get(p, {})

        if not isinstance(val, dict):
            self.val_name_var.set(path[-1])
            self.val_data_var.set(str(val) if val is not None else "")
            self.data_entry.config(state="normal")
        else:
            self.val_name_var.set("")
            self.val_data_var.set("")
            self.data_entry.config(state="normal")

    def get_path(self, item):
        path = []
        while item:
            path.insert(0, self.tree.item(item, "text"))
            item = self.tree.parent(item)
        return path

    # ------------------------------------------------------------------ #
    #  EDIT / DELETE / NEW KEY                                             #
    # ------------------------------------------------------------------ #
    def update_value(self):
        """Write the edited value back into config_data."""
        path = self._current_path
        if not path:
            messagebox.showwarning("RegEdit", "No key selected.")
            return

        # Navigate to parent dict
        parent = self.config_data
        for p in path[:-1]:
            parent = parent.get(p, {})

        leaf = path[-1]
        if isinstance(parent.get(leaf), dict):
            messagebox.showwarning("RegEdit", "Cannot edit a key group — select a value leaf.")
            return

        new_value = self.val_data_var.get()
        parent[leaf] = new_value
        self.status_var.set(f"Updated: {'\\'.join(path)}  →  {new_value}")
        self.root.after(2000, lambda: self.status_var.set("Ready"))

    def new_key(self):
        """Add a new value under the currently selected group."""
        item = self.tree.focus()
        path = self.get_path(item)

        # Resolve whether the selected item is a group or a leaf
        node = self.config_data
        for p in path:
            node = node.get(p, {})
        if not isinstance(node, dict):
            # Move up one level – add sibling, not child of a value
            path = path[:-1]
            node = self.config_data
            for p in path:
                node = node.get(p, {})

        dialog = tk.Toplevel(self.root)
        dialog.title("New Value")
        dialog.geometry("320x130")
        dialog.configure(bg="#C0C0C0")
        dialog.grab_set()

        tk.Label(dialog, text="Key Name:", bg="#C0C0C0",
                 font=("MS Sans Serif", 8)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        name_var = tk.StringVar()
        tk.Entry(dialog, textvariable=name_var, width=25).grid(row=0, column=1, padx=5)

        tk.Label(dialog, text="Value:", bg="#C0C0C0",
                 font=("MS Sans Serif", 8)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        val_var = tk.StringVar()
        tk.Entry(dialog, textvariable=val_var, width=25).grid(row=1, column=1, padx=5)

        def confirm():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("RegEdit", "Key name cannot be empty.", parent=dialog)
                return
            if name in node:
                messagebox.showwarning("RegEdit", "A key with that name already exists.", parent=dialog)
                return
            node[name] = val_var.get()
            self.refresh_tree()
            self.status_var.set(f"Created: {'\\'.join(path + [name])}")
            dialog.destroy()

        btn_frame = tk.Frame(dialog, bg="#C0C0C0")
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="OK", command=confirm, bg="#C0C0C0",
                  width=8, relief="raised").pack(side="left", padx=10)
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy, bg="#C0C0C0",
                  width=8, relief="raised").pack(side="left")

    def delete_key(self):
        """Delete the selected leaf value."""
        path = self._current_path
        if not path:
            return

        parent = self.config_data
        for p in path[:-1]:
            parent = parent.get(p, {})

        leaf = path[-1]
        if isinstance(parent.get(leaf), dict):
            if not messagebox.askyesno("RegEdit",
                                       f"Delete the entire group '{leaf}' and all its values?"):
                return
        else:
            if not messagebox.askyesno("RegEdit", f"Delete '{leaf}'?"):
                return

        del parent[leaf]
        self._current_path = []
        self.val_name_var.set("")
        self.val_data_var.set("")
        self.refresh_tree()
        self.status_var.set(f"Deleted: {'\\'.join(path)}")


# ------------------------------------------------------------------ #
#  ENTRY POINT                                                         #
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.configure("Treeview", font=("MS Sans Serif", 8))
    RegEdit(root)
    root.mainloop()