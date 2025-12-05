# Silo-Monitoring-System
This system for allerting and notify the silo level. Using arduino nano + ultrasonic sensor and display the measurement to Python GUI

Silo Ultrasonic Monitoring – Arduino + Python GUI

Real-Mode · HC-SR04 · Tkinter GUI · Industrial Mapping


---

Sistem monitoring level silo berbasis sensor ultrasonic HC-SR04.
Arduino membaca jarak aktual (cm), Python menampilkan:

Distance (cm)

Level (%) dengan logika real industri

280 cm = 0% (kosong)

≤10 cm = 100% (penuh)

Linear mapping 10–280 cm


Indikator Hijau (normal) → Merah (≥90%)


Proyek ini dirancang untuk implementasi sederhana, stabil, dan mudah untuk dokumentasi hardware.

// Arduino Codes

#define TRIG 2
#define ECHO 3

long duration;
float distance_cm;

void setup() {
  Serial.begin(9600);
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
}

float getDistance() {
  digitalWrite(TRIG, LOW);
  delayMicroseconds(3);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  duration = pulseIn(ECHO, HIGH, 30000);  // timeout 30ms (~5m)
  if (duration == 0) return -1;           // tidak ada echo

  float dist = duration * 0.0343 / 2;
  return dist;
}

void loop() {
  distance_cm = getDistance();

  if (distance_cm < 0) {
    Serial.println("ERR");
  } else {
    Serial.print(distance_cm);
    Serial.println("cm");
  }

  delay(50);
}


# Python Codes

import serial
import tkinter as tk

try:
    ser = serial.Serial('COM5', 9600, timeout=0.5)
except:
    ser = None

MAX_DIST = 280.0  # silo kosong
FULL_DIST = 10.0  # silo penuh

smoothed = 0.0
alpha = 0.3


def parse_distance(line):
    if not line:
        return None

    line = line.strip()
    if line.upper() == "ERR":
        return None

    try:
        if "cm" in line:
            line = line.replace("cm", "")
        return float(line)
    except:
        return None


def convert_to_percent(distance):
    if distance is None:
        return 0

    if distance >= MAX_DIST:
        return 0

    if distance <= FULL_DIST:
        return 100

    level = (MAX_DIST - distance) / (MAX_DIST - FULL_DIST) * 100

    if level < 0: level = 0
    if level > 100: level = 100

    return level


def update():
    global smoothed

    raw_line = ""
    if ser and ser.in_waiting:
        raw_line = ser.readline().decode(errors='ignore').strip()

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


root = tk.Tk()
root.title("Silo Monitoring – Real Mode")
root.config(bg="#1e1e1e")

tk.Label(root, text="Distance:", fg="white", bg="#1e1e1e",
         font=("Segoe UI", 14)).pack(pady=(10, 0))
label_distance = tk.Label(root, text="- cm", fg="cyan", bg="#1e1e1e",
                          font=("Segoe UI", 28))
label_distance.pack()

tk.Label(root, text="Level:", fg="white", bg="#1e1e1e",
         font=("Segoe UI", 14)).pack(pady=(15, 0))
label_percent = tk.Label(root, text="0%", fg="cyan", bg="#1e1e1e",
                         font=("Segoe UI", 44, "bold"))
label_percent.pack(pady=5)

canvas = tk.Canvas(root, width=160, height=160, bg="#1e1e1e", highlightthickness=0)
canvas.pack(pady=10)
circle = canvas.create_oval(10, 10, 150, 150, fill="#4CFF72", outline="")

root.after(100, update)
root.mainloop()
