# 🏋️ AI Form Correction Prototype

## 📌 Deskripsi
AI Form Correction adalah aplikasi berbasis **Computer Vision** yang membantu pengguna dalam melakukan **koreksi gerakan olahraga** (contohnya push-up, squat, dll).  
Aplikasi ini menggunakan **kamera** untuk mendeteksi pose tubuh, lalu memverifikasi apakah gerakan dilakukan dengan benar.

Prototype ini dibuat menggunakan **Python (Flask / Streamlit)** untuk backend, **HTML/CSS/JS** untuk frontend, serta modul AI untuk analisis pose.

---

## 📂 Struktur Folder
```

WEBAPP/
│── Camera/
│   ├── static/                # Asset statis (gambar, video, model AI jika ada)
│   ├── templates/             # Template HTML untuk rendering
│   ├── app.py                 # Main entry point aplikasi (server Flask)
│   ├── PoseModule.py          # Modul deteksi pose (OpenCV, Mediapipe, dsb.)
│   ├── PushUpCounter.py       # Modul perhitungan repetisi push-up
│
│── css/                       # File styling tampilan web
│   ├── about.css
│   ├── core.css
│   ├── Home.css
│   ├── mind.css
│   ├── program.css
│   ├── spirit.css
│   └── subscription.css
│
│── img/                       # Folder gambar/icon
│── Javascript/                # File JS tambahan
│── node\_modules/              # Dependency NodeJS (jika dipakai)
│
│── About.html                 # Halaman About
│── FeatureCore.html           # Halaman fitur inti (AI correction)
│── Featuremind.html           # Halaman fitur "Mind"
│── Featurespirit.html         # Halaman fitur "Spirit"
│── Home.html                  # Halaman utama aplikasi
│── Program.html               # Halaman Program latihan
│── Subscription.html          # Halaman Subscription
│
│── readme.md                  # Dokumentasi project

````

---

## 🛠️ Teknologi yang Digunakan
- **Python** (Flask/Streamlit) – Backend server
- **OpenCV + Mediapipe** – Deteksi pose tubuh
- **HTML, CSS, JavaScript** – Frontend aplikasi
- **Node.js (opsional)** – Untuk dependency frontend
- **GitHub** – Version control

---

## 🚀 Cara Menjalankan
1. Clone repository:
   ```bash
   git clone https://github.com/username/AI-Form-Correction.git
   cd AI-Form-Correction/WEBAPP
    ````
2. Install dependencies:
    ```bash
   pip install -r requirements.txt
   ````

3. Jalankan server:

   ```bash
   python Camera/app.py
   ```

4. Buka di browser:

   ```
   http://127.0.0.1:5000
   ```

---

## 📊 Fitur Utama

* **Pose Detection** → Mendeteksi posisi tubuh secara real-time melalui kamera.
* **Form Correction** → Memberi feedback apakah gerakan sudah benar.
* **Push-Up Counter** → Menghitung jumlah repetisi secara otomatis.
* **Program Latihan** → Menyediakan halaman dengan program latihan sesuai kebutuhan.
* **Subscription Page** → Halaman untuk layanan premium.

---

## 👥 Tim Pengembang

* Developer AI: M. Arsal Ranjana Utama, Natanael Oktavianus Partahan Sihombing & Ghozi Alvin Karim
* Frontend Developer: Ghozi Alvin Karim
* Backend Developer: Ghozi Alvin Karim

---

## 📚 Catatan

* Prototype masih dalam tahap pengembangan.
* Model AI dapat dikembangkan lebih lanjut untuk mendukung lebih banyak jenis olahraga.
