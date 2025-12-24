# Import Required Library
from tkinter import *
import datetime
import time
import winsound
from threading import Thread

# Create Object
root = Tk()

# Set geometry
root.geometry("420x220")
root.title("12 Hour Alarm Clock")

# Use Threading
def Threading():
    t1 = Thread(target=alarm)
    t1.daemon = True
    t1.start()

def alarm():
    while True:
        # Set Alarm Time (12-hour format)
        set_alarm_time = f"{hour.get()}:{minute.get()}:{second.get()} {ampm.get()}"

        time.sleep(1)

        # Get current time in 12-hour format
        current_time = datetime.datetime.now().strftime("%I:%M:%S %p")

        print(current_time, set_alarm_time)

        # Check alarm
        if current_time == set_alarm_time:
            print("Time to Wake up!")
            winsound.PlaySound("sound.wav", winsound.SND_LOOP)
            break

# Labels
Label(root, text="Alarm Clock", font=("Helvetica", 20, "bold"), fg="red").pack(pady=10)
Label(root, text="Set Time (12 Hour)", font=("Helvetica", 14)).pack()

frame = Frame(root)
frame.pack(pady=5)

# Hour (01–12)
hour = StringVar(root)
hours = tuple(f"{i:02d}" for i in range(1, 13))
hour.set(hours[0])
OptionMenu(frame, hour, *hours).pack(side=LEFT)

# Minute (00–59)
minute = StringVar(root)
minutes = tuple(f"{i:02d}" for i in range(60))
minute.set(minutes[0])
OptionMenu(frame, minute, *minutes).pack(side=LEFT)

# Second (00–59)
second = StringVar(root)
seconds = tuple(f"{i:02d}" for i in range(60))
second.set(seconds[0])
OptionMenu(frame, second, *seconds).pack(side=LEFT)

# AM / PM
ampm = StringVar(root)
ampm.set("AM")
OptionMenu(frame, ampm, "AM", "PM").pack(side=LEFT)

# Button
Button(root, text="Set Alarm", font=("Helvetica", 14), command=Threading).pack(pady=20)

# Execute Tkinter
root.mainloop()
