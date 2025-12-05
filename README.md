​⚙️ Silo-Monitoring-System
​Sistem sederhana untuk memonitor level silo menggunakan Arduino Nano + sensor ultrasonic HC-SR04, dan menampilkan jarak serta level pada Python GUI (Tkinter).

Mode Sensor GUI Mapping
Real Mode HC-SR04 Tkinter Linear industrial (\mathbf{10} \text{–} \mathbf{280 \text{ cm}})


📝 Ringkasan
​Sistem ini membaca jarak aktual (\text{cm}) dari sensor HC-SR04 yang dipasang di bagian atas silo. Data dikirim lewat serial USB ke komputer yang menjalankan aplikasi Python. Aplikasi menampilkan jarak (\text{cm}) dan persentase level (0\text{–}100\%) dengan logika industri:

​280 cm = 0\% (silo kosong)
​\le 10 \text{ cm} = 100\% (silo penuh)
​Mapping linear antara 10 \text{ –} 280 \text{ cm}

​Indikator visual berubah warna dari hijau (normal) menjadi merah saat level \ge 90\%.
​Tujuan: implementasi yang sederhana, stabil, dan mudah didokumentasikan di repository.


​📦 Hardware
​Arduino Nano (atau board kompatibel)
​HC-SR04 ultrasonic sensor
​Kabel jumper, breadboard (opsional)
​Kabel USB untuk serial
​🔌 Wiring (HC-SR04 ↔ Arduino)


HC-SR04 Pin Arduino Pin
VCC 5V
GND GND
TRIG D2
ECHO D3


​Catatan: Pastikan sensor dipasang tegak lurus ke permukaan material dan tidak terlalu dekat ke dinding silo yang dapat memantulkan gelombang.



​💾 Arduino Code (Satu file: silo_monitor.ino)
​Kode ini membaca jarak, menghitung jarak dalam \text{cm}, dan mengirimkan melalui serial.


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

  duration = pulseIn(ECHO, HIGH, 30000); // timeout 30ms (~5m)

  if (duration == 0) return -1; // tidak ada echo (out of range)

  float dist = duration * 0.0343 / 2;
  return dist;
}

void loop() {
  distance_cm = getDistance();
  if (distance_cm < 0) {
    Serial.println("ERR");
  } else {
    Serial.print(distance_cm, 1);
    Serial.println("cm");
  }
  delay(50); // 20 Hz sampling
}



Catatan kode Arduino:
​pulseIn menggunakan timeout 30 \text{ ms} untuk menghindari blocking terlalu lama.
​Output berupa ERR jika tidak terdeteksi echo; format jarak misal 123.4cm.


​🖥️ Python GUI Code (Satu file: silo_gui.py)
​Aplikasi Python membaca serial, mem-parse data, memetakan ke persen, dan menampilkan GUI sederhana.

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


Catatan Python:
​Ubah variabel PORT sesuai port serial di sistem anda.
​Jika serial tidak tersedia, aplikasi tetap jalan (akan menampilkan ERR).
​Parameter alpha mengatur smoothing; nilai kecil \to lebih lambat merespon, nilai besar \to respons cepat tapi lebih noisy.
​root.after(50, update) \approx 20 \text{ FPS} GUI update. Sesuaikan jika perlu.

