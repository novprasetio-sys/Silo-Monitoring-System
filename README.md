# ESP32 Silo Monitoring System

Stand-alone **Silo Monitoring System** berbasis ESP32 + MicroPython + Python di Android (Pydroid). Sistem ini memungkinkan operator memantau jarak level silo secara realtime melalui HP yang terkoneksi ke ESP32 Access Point dan menyimpan data log ke CSV.

---

## **1. ESP32 MicroPython Web Server**

Baca sensor Ultrasonik HC-SR04 dan tampilkan data jarak realtime melalui web server (Access Point).

### Wiring

* **VCC → 5V**
* **GND → GND**
* **Trig → GPIO 5**
* **Echo → GPIO 18**

### MicroPython Code (ESP32)

```python
import network
import socket
import machine
import time

# Setup Ultrasonic HC-SR04
trig = machine.Pin(5, machine.Pin.OUT)
echo = machine.Pin(18, machine.Pin.IN)

def distance_cm():
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    pulse_time = machine.time_pulse_us(echo, 1, 30000)
    if pulse_time < 0:
        return -1
    return pulse_time / 58

# Setup Access Point
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='ESP32_AP', authmode=network.AUTH_WPA_WPA2_PSK, password='12345678')
print('Access Point Active')
print(ap.ifconfig())

# Setup Web Server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print('Listening on', addr)

html_template = """
<!DOCTYPE html>
<html>
<head>
<title>ESP32 Ultrasonic</title>
<style>
body {{ font-family: Arial; text-align:center; margin-top:50px; }}
.distance {{ font-size: 48px; }}
.notice {{ color: red; font-weight: bold; font-size: 36px; }}
.normal {{ color: green; font-weight: bold; font-size: 24px; }}
</style>
<meta http-equiv="refresh" content="1">
</head>
<body>
<h1>ESP32 Ultrasonic Sensor</h1>
<p class="distance"> {dist} </p>
<p class="{status_class}">{status_text}</p>
</body>
</html>
"""

while True:
    cl, addr = s.accept()
    print('Client connected from', addr)
    request = cl.recv(1024)
    d = distance_cm()
    if d >= 0 and d < 10:
        status_text = "NOTICE: Object too close!"
        status_class = "notice"
    else:
        status_text = "Distance normal"
        status_class = "normal"
    response = html_template.format(dist=d, status_text=status_text, status_class=status_class)
    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    cl.send(response)
    cl.close()
```

---

## **2. Python Logging App di Android (Pydroid)**

Membaca data jarak dari ESP32 AP dan menyimpan ke CSV secara realtime.

### Final Pydroid Python Code

```python
import requests
import csv
import time
from datetime import datetime
import re

ESP_IP = '192.168.4.1'  # IP default ESP32 AP
CSV_FILE = 'silo_log.csv'
POLL_INTERVAL = 1  # detik

# Buat header CSV
with open(CSV_FILE, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Timestamp', 'Distance_cm'])

print("Logging started... Ctrl+C untuk stop")

try:
    while True:
        try:
            r = requests.get(f'http://{ESP_IP}/')
            data = r.text

            # Robust parsing angka
            match = re.search(r'class="distance">\s*([\d.]+)\s*<', data)
            if match:
                distance = float(match.group(1))
                print(f"Distance: {distance} cm")

                with open(CSV_FILE, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([datetime.now(), distance])
            else:
                print("Failed to parse distance")

        except Exception as e:
            print("Error:", e)

        time.sleep(POLL_INTERVAL)

except KeyboardInterrupt:
    print("Logging stopped")
```

### **Cara Pakai**

1. Nyalakan ESP32 → AP + Web Server aktif
2. Connect HP ke Wi-Fi ESP32 (`ESP32_AP`)
3. Jalankan script Python di Pydroid
4. CSV `silo_log.csv` tersimpan di folder Pydroid (`/storage/emulated/0/Pydroid3/`)
5. Data jarak realtime tersimpan otomatis, bisa di-export ke Excel/Sheets

---

Repo ini bisa dikembangkan oleh maker lain untuk:

* GUI interaktif di Pydroid (progress bar + indikator warna)
* Multi-sensor logging
* Export/analisis data realtime

---

**Catatan:** Sistem ini sepenuhnya offline, HP hanya perlu connect ke ESP32 AP, cocok untuk monitoring silo secara independen.
