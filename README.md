# Doc-to-Interactive 🚀
> **AI-Powered Interactive E-Learning Module Builder & Skill**  
> Ubah dokumen materi, SOP, silabus, dan slide statis menjadi aplikasi web e-learning interaktif mandiri (*single-file HTML*) berstandar industri.

[![HTML5](https://img.shields.io/badge/HTML5-Single--File-E34F26?logo=html5&logoColor=white)](#)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v3.x-38B2AC?logo=tailwind-css&logoColor=white)](#)
[![Web Audio API](https://img.shields.io/badge/Web_Audio_API-Synthesized_FX-005571)](#)
[![Google Sheets Sync](https://img.shields.io/badge/Google_Sheets-Webhook_Sync-34A853?logo=google-sheets&logoColor=white)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](#)

---

## 📖 Ringkasan (Overview)

**Doc-to-Interactive** adalah skill AI agent dan builder engine yang mengonversi dokumen kurikulum, modul training, SOP kerja, serta slide statis menjadi modul e-learning interaktif yang modern, responsif, dan siap produksi.

Hasil akhir berupa **satu file `.html` mandiri (standalone)** yang dapat langsung dibuka di browser tanpa server lokal (`file://`), di-host di static web hosting (GitHub Pages, Vercel, Netlify), maupun disematkan ke dalam LMS (Moodle, Canvas, Blackboard) via iframe atau SCORM package.

---

## ✨ Fitur Unggulan

### 1. ⏱️ 10-Second Slide Gating Timer
- Mencegah peserta melakukan *skipping* materi tanpa membaca.
- Tombol **Lanjut (Next)** otomatis terkunci (`disabled`) selama 10 detik saat slide baru dibuka, lengkap dengan hitung mundur dinamis (`Tunggu (10s)` $\rightarrow$ `Tunggu (1s)`).
- Menampilkan countdown badge di bar durasi atas (`⏳ Selesaikan materi dalam Xs...`).
- Notifikasi peringatan jika user mencoba melompat lewat daftar isi/sidebar.
- Dilengkapi efek *unlock chime* (Web Audio) dan animasi pulse glow saat waktu tuntas.
- Slide yang sudah tuntas dipelajari tidak dikunci ulang saat dibuka kembali.

### 2. 📝 Native In-App Quiz & Anti-Spam (Maksimal 5 Attempt)
- Formulir identitas peserta langsung di aplikasi: Nama, NIP/NRP, Jabatan, dan Divisi.
- Mendukung MCQ, Benar/Salah, dan Isian Singkat dengan pengacakan opsi dan pembahasan kunci jawaban.
- **Batas Percobaan**: Maksimal 5 kali percobaan kuis (`maxQuizAttempts: 5`).
- **Gating Kelulusan**:
  - Skor $\ge 80$: Membuka gembok halaman Sertifikat Resmi, selebrasi konfeti, dan pengiriman nilai ke server analitik.
  - Skor $< 80$ & Attempt $< 5$: Menampilkan evaluasi remedial dan tombol ulangi kuis. Data gagal **tidak dikirim** ke sheet untuk mencegah polusi data.
  - Skor $< 80$ & Attempt $= 5$: Kuis terkunci permanen dengan instruksi menghubungi Tim HC / PIC Pelatihan.

### 3. 📊 Google Sheets Serverless Webhook Sync (Upsert Nilai Tertinggi)
- Endpoint serverless gratis menggunakan Google Apps Script (GAS).
- **Aman Beban Serentak**: Menggunakan `LockService.getScriptLock()` untuk menangani antrean pengiriman 50+ peserta secara bersamaan tanpa *race condition*.
- **Mekanisme Upsert**: Jika NIP sudah tercatat, data baris lama **hanya ditimpa jika nilai baru lebih tinggi** dari nilai sebelumnya.

### 4. 🧩 18 Tipe Slide Interaktif
1. `cover`: Hero title, badge versi, deskripsi, dan CTA mulai.
2. `cardList`: Kartu interaktif grid dengan icon, detail modal, dan status.
3. `treeCanvas`: Alur proses flowchart interaktif dengan zoom/pan, filter peran (role), dan modal hotspot.
4. `scenarioPicker`: Simulasi pengambilan keputusan / dilema etika dengan umpan balik instan.
5. `tabbedAccordion`: Navigasi tab konten berbasis pilar/tahapan.
6. `verificationMatrix`: Matriks verifikasi dokumen dengan status lulus/tinjau.
7. `twoCardAccordion`: Komparasi 2 kartu interaktif (sebelum vs sesudah, do vs don't).
8. `docTabs`: Tampilan dokumen acuan/formulir resmi dengan tab berkas.
9. `kpiDashboard`: Dashboard metriks kuantitatif dengan indikator pencapaian.
10. `riskCards`: Matriks evaluasi risiko dengan mitigasi operasional.
11. `quiz`: Mesin kuis komprehensif dengan grading instan.
12. `summaryCertificate`: Rangkuman poin kunci + generator sertifikat resmi siap cetak A4 landscape ke PDF.
13. `imageGallery`: Galeri visual dokumentasi.
14. `videoEmbed`: Pemutar video terintegrasi dengan caption.
15. `calloutBox`: Kotak peringatan/peringatan kepatuhan penting.
16. `stepByStep`: Prosedur langkah demi langkah sekuensial.
17. `comparisonTable`: Tabel komparasi multi-kolom responsif.
18. `faqAccordion`: Tanya jawab interaktif.

### 5. 🎨 Multi-Brand Presets & Dark/Light Mode
- Mendukung preset tema visual bawaan: `corporate`, `ptpp`, `education`, `tech-startup`, atau palet warna `custom`.
- Toggle instan Dark / Light mode dengan kontras warna terkalibrasi WCAG 2.2 AA.

---

## 📁 Struktur Repositori

```text
doc-to-interactive/
├── SKILL.md                          # Spesifikasi AI Agent Skill (Antigravity, Gemini, Claude)
├── README.md                         # Dokumentasi lengkap repositori
├── assets/
│   ├── shell.template.html           # Template shell player modular (~2900 baris)
│   ├── content.schema.json           # JSON Schema validator untuk modul
│   ├── brand.profiles.json           # Definisi palet warna 4 preset tema
│   ├── sample.content.json           # Contoh data modul lengkap siap build
│   └── sample.slide_breakdown.md     # Contoh format input breakdown slide
├── references/
│   ├── slide_types.md                # Dokumentasi detail spesifikasi 18 tipe slide
│   ├── input_format.md               # Pedoman penulisan prompt materi oleh pengguna
│   ├── brand_profiles.md             # Konfigurasi custom branding & tema
│   ├── pedagogical_patterns.md       # Pola instruksional & variasi interaksi edukatif
│   └── gas_webhook_setup.md          # Panduan integrasi Google Apps Script & Sheets
└── scripts/
    ├── build_module.py               # Script kompilasi (content.json -> standalone HTML)
    ├── validate_content.py           # Script validasi integritas struktur content.json
    ├── smoke_test_module.py          # Script headless browser QA test
    └── build_shell_template.py       # Builder template shell hulu
```

---

## 🚀 Cara Penggunaan

### A. Sebagai AI Agent Skill (Antigravity / Gemini CLI / Claude Code)
1. Salin folder repositori ini ke direktori skills agent Anda:
   - Antigravity / Gemini: `~/.gemini/config/skills/doc-to-interactive/`
   - Claude Code: `~/.claude/skills/doc-to-interactive/`
2. Panggil skill melalui prompt atau slash command:
   ```text
   /doc-to-interactive
   "Tolong buatkan modul e-learning interaktif dari dokumen SOP ini..."
   ```

### B. Menggunakan Script Kompilasi (CLI / Manual)
1. Buat atau sesuaikan file konfigurasi materi Anda (misal `kursus.json`):
   ```json
   {
     "course": {
       "code": "TRAIN-01",
       "title": "Pelatihan Tata Kelola Kerja",
       "totalUnits": 3,
       "passingScore": 80,
       "totalQuestions": 5
     },
     "brand": { "preset": "corporate" },
     "units": [ ... ],
     "slides": [ ... ]
   }
   ```
2. Validasi struktur JSON:
   ```bash
   python scripts/validate_content.py kursus.json
   ```
3. Kompilasi menjadi satu file HTML:
   ```bash
   python scripts/build_module.py --content kursus.json --output dist/kursus_interaktif.html --validate
   ```
4. Buka file `dist/kursus_interaktif.html` di browser pilihan Anda!

---

## 🛠️ Integrasi Google Apps Script (Webhook Nilai)

Untuk mencatat hasil nilai peserta secara terpusat ke spreadsheet Google:
1. Buat Google Sheet dengan header kolom:
   `Timestamp | Nama | NIP | Jabatan | Divisi | Skor | Status | Attempt`
2. Buka **Extensions > Apps Script**, masukkan template kode dari [`references/gas_webhook_setup.md`](references/gas_webhook_setup.md).
3. Deploy sebagai **Web App** dengan akses `Anyone`.
4. Masukkan URL hasil deployment ke konfigurasi modul e-learning Anda.

---

## 📄 Lisensi
Proyek ini didistribusikan di bawah lisensi [MIT](LICENSE). Bebas digunakan untuk keperluan komersial, pelatihan korporat, maupun institusi pendidikan.
