import serial
import tkinter as tk
import sys

# Ubah PORT sesuai OS: 'COM5' (Windows) atau '/dev/ttyUSB0' (Linux)
PORT = 'COM5'
BAUD = 9600
MAX_DIST = 280.0 # cm -> 0%
FULL_DIST = 10.0 # cm -> 100%
smoothed = 0.0
alpha = 0.3 # smoothing factor (0-1)

# Serial init
try:
    ser = serial.Serial(PORT, BAUD, timeout=0.5)
except Exception as e:
    ser = None
    print(f"Warning: cannot open serial port {PORT}: {e}", file=sys.stderr)

def parse_distance(line):
    if not line:
        return None
    line = line.strip()
    if not line:
        return None
    if line.upper() == "ERR":
        return None
    try:
        if line.endswith('cm'):
            line = line[:-2]
            return float(line)
    except Exception:
        return None

def convert_to_percent(distance):
    if distance is None:
        return 0
    if distance >= MAX_DIST:
        return 0
    if distance <= FULL_DIST:
        return 100
    
    level = (MAX_DIST - distance) / (MAX_DIST - FULL_DIST) * 100
    level = max(0.0, min(100.0, level))
    return level

def update():
    global smoothed
    raw_line = ''
    if ser and ser.in_waiting:
        try:
            raw_line = ser.readline().decode(errors='ignore').strip()
        except Exception:
            raw_line = ''

    dist = parse_distance(raw_line)
    percent = convert_to_percent(dist)
    
    smoothed = smoothed + alpha * (percent - smoothed)
    p_show = int(smoothed + 0.5)

    if dist is None:
        label_distance.config(text="ERR")
    else:
        label_distance.config(text=f"{dist:.1f} cm")

    label_percent.config(text=f"{p_show}%")
    
    if p_show >= 90:
        canvas.itemconfig(circle, fill="#FF4C4C")
    else:
        canvas.itemconfig(circle, fill="#4CFF72")
        
    root.after(50, update)

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Silo Monitoring – Real Mode")
    root.config(bg="#1e1e1e")

    tk.Label(root, text="Distance:", fg="white", bg="#1e1e1e", font=("Segoe UI", 14)).pack(pady=(10, 0))
    label_distance = tk.Label(root, text="- cm", fg="cyan", bg="#1e1e1e", font=("Segoe UI", 28))
    label_distance.pack()

    tk.Label(root, text="Level:", fg="white", bg="#1e1e1e", font=("Segoe UI", 14)).pack(pady=(15, 0))
    label_percent = tk.Label(root, text="0%", fg="cyan", bg="#1e1e1e", font=("Segoe UI", 44, "bold"))
    label_percent.pack(pady=5)

    canvas = tk.Canvas(root, width=160, height=160, bg="#1e1e1e", highlightthickness=0)
    canvas.pack(pady=10)
    circle = canvas.create_oval(10, 10, 150, 150, fill="#4CFF72", outline="")

    root.after(100, update)
    root.mainloop()