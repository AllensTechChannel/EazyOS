import tkinter as tk
from tkinter import font
import subprocess

class BiosSimulator:
    def __init__(self, master):
        self.master = master
        self.master.title("BIOS Simulator")
        self.master.configure(bg="#00008B")  # Dark blue background
        self.master.geometry("800x600")

        # Monospaced font for a retro BIOS look
        self.bios_font = font.Font(family="Courier", size=14)
        self.selected_row = 0

        # Define menu structure and options
        self.menus = {
            "Main": [
                {"label": "System Time", "value": "22:30:00"},
                {"label": "System Date", "value": "10/29/2025"},
                {"label": "Legacy USB Support", "value": "Enabled"},
                {"label": "HDD S.M.A.R.T. Capability", "value": "Enabled"},
            ],
            "Advanced": [
                {"label": "CPU Configuration", "value": ""},
                {"label": "Onboard Device Configuration", "value": ""},
                {"label": "Power Management Setup", "value": ""},
            ],
            "Boot": [
                {"label": "Boot Option #1", "value": "Hard Disk"},
                {"label": "Boot Option #2", "value": "CD/DVD Drive"},
            ],
            "Exit": [
                {"label": "Exit Saving Changes", "value": ""},
                {"label": "Exit Discarding Changes", "value": ""},
            ],
        }

        self.current_menu_name = "Main"

        # Create GUI frames
        self.create_widgets()

        # Bind keyboard events
        self.master.bind("<Up>", self.navigate_up)
        self.master.bind("<Down>", self.navigate_down)
        self.master.bind("<Return>", self.select_option)
        self.master.bind("<Left>", self.change_menu_left)
        self.master.bind("<Right>", self.change_menu_right)

        # Draw initial menu
        self.draw_menu()

    # === Run boot.py ===
    def run_boot(self):
        """Run boot.py when 'Exit Saving Changes' is selected."""
        try:
            self.master.destroy()
            subprocess.Popen(["python", "boot.py"])
        except Exception as e:
            print(f"Error launching boot.py: {e}")

    # === Create GUI widgets ===
    def create_widgets(self):
        # Top menu bar
        self.menu_frame = tk.Frame(self.master, bg="dark blue")
        self.menu_frame.pack(pady=10)

        # Tab labels for menus
        self.menu_labels = {}
        for i, menu_name in enumerate(self.menus.keys()):
            label = tk.Label(
                self.menu_frame, text=menu_name, bg="dark blue",
                fg="white", font=self.bios_font
            )
            label.pack(side="left", padx=20)
            self.menu_labels[menu_name] = label

        # Main content
        self.content_frame = tk.Frame(self.master, bg="#00008B", padx=20, pady=20)
        self.content_frame.pack(fill="both", expand=True)

        # Help text area
        self.help_frame = tk.Frame(self.master, bg="dark gray", bd=2, relief="sunken")
        self.help_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        self.help_text = tk.Label(
            self.help_frame, text="", bg="dark gray", fg="white",
            font=self.bios_font, wraplength=780, justify="left"
        )
        self.help_text.pack(fill="x", padx=5, pady=5)

    # === Draw current menu ===
    def draw_menu(self):
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Update tab highlights
        for name, label in self.menu_labels.items():
            if name == self.current_menu_name:
                label.configure(bg="#4d4d4d")  # Highlighted tab
            else:
                label.configure(bg="dark blue")

        # Display options for this menu
        current_options = self.menus[self.current_menu_name]
        for i, option in enumerate(current_options):
            label_text = option["label"]
            value_text = option["value"]

            row = tk.Frame(self.content_frame, bg="#00008B")
            row.pack(fill="x", pady=2)

            label = tk.Label(row, text=label_text, font=self.bios_font, bg="#00008B", fg="white", anchor="w")
            label.pack(side="left", padx=10, fill="x", expand=True)

            if value_text:
                val = tk.Label(row, text=value_text, font=self.bios_font, bg="#00008B", fg="white", anchor="e")
                val.pack(side="right", padx=10, fill="x", expand=True)

            # Highlight selected row
            if i == self.selected_row:
                label.configure(bg="cyan", fg="black")
                self.update_help_text(option["label"])

    # === Navigation ===
    def navigate_up(self, event):
        if self.selected_row > 0:
            self.selected_row -= 1
            self.draw_menu()

    def navigate_down(self, event):
        if self.selected_row < len(self.menus[self.current_menu_name]) - 1:
            self.selected_row += 1
            self.draw_menu()

    def change_menu_left(self, event):
        menu_names = list(self.menus.keys())
        idx = menu_names.index(self.current_menu_name)
        if idx > 0:
            self.current_menu_name = menu_names[idx - 1]
            self.selected_row = 0
            self.draw_menu()

    def change_menu_right(self, event):
        menu_names = list(self.menus.keys())
        idx = menu_names.index(self.current_menu_name)
        if idx < len(menu_names) - 1:
            self.current_menu_name = menu_names[idx + 1]
            self.selected_row = 0
            self.draw_menu()

    # === Selection handler ===
    def select_option(self, event):
        current_menu = self.menus[self.current_menu_name]
        selected_option = current_menu[self.selected_row]

        if self.current_menu_name == "Exit":
            if selected_option["label"] == "Exit Saving Changes":
                print("Saving and launching boot.py...")
                self.run_boot()
            elif selected_option["label"] == "Exit Discarding Changes":
                print("Exiting without saving.")
                self.master.destroy()
        else:
            # Toggle options like Enabled/Disabled
            if selected_option["value"] in ("Enabled", "Disabled"):
                selected_option["value"] = (
                    "Disabled" if selected_option["value"] == "Enabled" else "Enabled"
                )
                self.draw_menu()

    # === Help text ===
    def update_help_text(self, option_label):
        help_texts = {
            "System Time": "Sets the system clock time.",
            "System Date": "Sets the system calendar date.",
            "Legacy USB Support": "Enables or disables support for legacy USB devices.",
            "HDD S.M.A.R.T. Capability": "Enables or disables S.M.A.R.T. (Self-Monitoring, Analysis and Reporting Technology) for your hard disk.",
            "CPU Configuration": "Displays CPU details and allows for configuration.",
            "Onboard Device Configuration": "Configures settings for integrated devices like network adapters.",
            "Power Management Setup": "Configures power saving and wake-up settings.",
            "Boot Option #1": "Select the primary boot device.",
            "Boot Option #2": "Select the secondary boot device.",
            "Exit Saving Changes": "Save all changes and boot the system.",
            "Exit Discarding Changes": "Exit setup without saving any changes.",
        }
        self.help_text.config(
            text=f"Selected: {option_label}\n\n{help_texts.get(option_label, 'No help available.')}"
        )


def main():
    root = tk.Tk()
    app = BiosSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
