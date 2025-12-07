# ⚙️ Silo-Monitoring-System
Sistem sederhana untuk memonitor level silo menggunakan Arduino Nano + sensor ultrasonic HC-SR04, dan menampilkan jarak serta level pada Python GUI (Tkinter).

## 📝 Ringkasan
Sistem ini membaca jarak aktual (cm) dari sensor HC-SR04 yang dipasang di bagian atas silo. Data dikirim lewat serial USB ke komputer yang menjalankan aplikasi Python. Aplikasi menampilkan jarak (cm) dan persentase level (0–100%) dengan logika industri:
- 280 cm = 0% (silo kosong)
- ≤ 10 cm = 100% (silo penuh)
- Mapping linear antara 10 – 280 cm
- Indikator visual berubah warna dari hijau (normal) menjadi merah saat level ≥ 90%.

## 📦 Hardware
- Arduino Nano (atau board kompatibel)
- HC-SR04 ultrasonic sensor
- Kabel jumper, breadboard (opsional)
- Kabel USB untuk serial

## 🔌 Wiring (HC-SR04 ↔ Arduino)

| HC-SR04 Pin | Arduino Pin |
| --- | --- |
| VCC | 5V |
| GND | GND |
| TRIG | D2 |
| ECHO | D3 |

## 💾 Arduino Code (silo_monitor.ino)
```cpp
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
