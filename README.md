# face-recog-anshar 1.0
Adalah program absensi berbasis wajah atau face recognition. Dengan menggunakan OpenCV dan Face-Recognition module

## Installation
Pastikan bootstrapper sudah diberi izin execute. Run bootstrapper
```bash
chmod +x ./bootstrap_linux.sh
./bootstrap_linux.sh
```

## Usage
Klik ikon di desktop atau run langsung run.sh
```bash
./run.sh
```

DB ->
Export table MySQL users ke json, atau gunakan template di folder db yang disediakan

NEW_IMAGES ->
Masukkan foto sesuai id yang ada di dalam users.json E.g. : 12345.png

BIN ->
Jalankan multi_encode.py untuk menghasilkan known_face_encodings.pkl

CRONTAB ->
Buka crontab untuk mengautomatisasi program
```bash
crontab -e
```
Copy dan paste dari crontab.txt

## Display
Icon centang - terabsen
Icon info - sudah terabsen

Belum terdaftar - wajah belum terdaftar
None in database - tidak ditemukan id tersebut di database

Border Biru - sudah terabsen
Border Oren - tidak ditemukan
