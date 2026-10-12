# Doc-to-Interactive 🚀
> **AI-Powered Interactive E-Learning Module Builder & Skill**  
> Ubah dokumen materi, SOP, silabus, dan slide statis menjadi aplikasi web e-learning interaktif mandiri (*single-file HTML*) berstandar industri dengan 18 tipe slide, kuis anti-spam, timer gating, dan sinkronisasi Google Sheets.

[![Live Demo](https://img.shields.io/badge/Live_Demo-WI_Pelatihan_Rev--2-success?style=for-the-badge&logo=github)](https://notsyam.github.io/wi-pelatihan-rev2/)
[![HTML5](https://img.shields.io/badge/HTML5-Single--File-E34F26?style=for-the-badge&logo=html5&logoColor=white)](#)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v3.x-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](#)
[![Web Audio API](https://img.shields.io/badge/Web_Audio-Synthesized_FX-005571?style=for-the-badge)](#)
[![Google Sheets Sync](https://img.shields.io/badge/Google_Sheets-Webhook_Sync-34A853?style=for-the-badge&logo=google-sheets&logoColor=white)](#)

---

## 🌐 Contoh Modul yang Sudah Jadi (Live Demo)

Lihat contoh modul e-learning interaktif nyata yang diproduksi menggunakan engine dan skill ini:

👉 **[Work Instruction Pelatihan (PP/SOP/E3-029 REV-2) - PT PP (Persero) Tbk](https://notsyam.github.io/wi-pelatihan-rev2/)**

> **Fitur yang dapat dicoba pada Live Demo di atas:**
> - ⏳ **Slide Gating Timer 10 Detik**: Tombol *Lanjut* terkunci dengan hitung mundur di setiap slide baru.
> - 🌲 **Interactive Flowchart Canvas**: Diagram pohon alur kerja dengan pan/zoom, filter peran (*Role Filter*), dan hotspot interaktif.
> - 📝 **Native In-App Quiz**: Uji pemahaman dengan kartu identitas peserta, acak opsi, dan batas maksimal 5 kali percobaan.
> - 🎓 **Official Printable Certificate**: Membuka gembok sertifikat resmi berformat cetak A4 landscape ke PDF jika lulus kuis ($\ge 80$).
> - 📊 **Real-time Webhook Sync**: Pengiriman skor otomatis ke Google Sheets dengan pencegahan data spam dan upsert nilai tertinggi.

---

## 📖 Ringkasan (Overview)

**Doc-to-Interactive** adalah skill AI agent dan builder engine yang mengonversi dokumen kurikulum, modul training, SOP kerja, serta slide statis menjadi modul e-learning interaktif yang modern, responsif, dan siap produksi.

Hasil akhir berupa **satu file `.html` mandiri (standalone)** yang dapat langsung dibuka di browser tanpa server lokal (`file://`), di-host di static web hosting (GitHub Pages, Vercel, Netlify), maupun disematkan ke dalam LMS (Moodle, Canvas, Blackboard) via iframe atau SCORM package.

---

## 🚀 Cara Menggunakan (Usage Guide)

Ada 2 cara praktis untuk menggunakan builder ini:
1. **Bersama AI Agent (Rekomendasi)**: Menggunakan Claude Code, Gemini CLI, atau Google Antigravity Agent.
2. **Secara Manual via CLI Python**: Menggunakan skrip `build_module.py` dan format `content.json`.

---

### Alur 1: Menggunakan AI Agent (Prompting)

1. Pasang skill ini di direktori konfigurasi AI Agent Anda (misal `~/.gemini/config/skills/doc-to-interactive/` atau `~/.claude/skills/doc-to-interactive/`).
2. Lampirkan dokumen materi Anda (PDF, Word, Markdown, atau teks mentah).
3. Berikan prompt instruksi:
   ```text
   /doc-to-interactive
   "Tolong konversi dokumen SOP terlampir menjadi modul e-learning interaktif 12 slide. 
   Gunakan brand corporate, tambahkan kuis 5 soal dengan passing grade 80, 
   dan terapkan slide gating timer 10 detik per slide."
   ```
4. AI Agent akan menganalisis dokumen dan menyusun **Slide Breakdown Terstruktur** untuk Anda review sebelum file HTML final dikompilasi.

---

### Alur 2: Format Teks Input Breakdown Materi

Jika Anda ingin menentukan sendiri urutan dan jenis interaksi pada tiap slide secara presisi, gunakan format **Structured Bullets** berikut:

#### 📋 Template Standar Per Slide:
```markdown
## Slide <Nomor>: <Judul Slide>
type: <tipe_slide>              # Pilih dari 18 tipe slide yang tersedia
category: <Kategori Badge>      # Ditampilkan di stage bar atas (misal: Pendahuluan, Prosedur, Evaluasi)
duration: <MM:SS>               # Estimasi durasi membaca (misal: 01:30)
icon: <nama_material_icon>      # Ikon Google Material Symbol untuk sidebar menu
narration: <Naskah Suara>       # Teks narasi untuk Closed Caption (CC) dan tab Catatan

<Field khusus sesuai tipe slide, format YAML/indented bullets>
```

---

#### 💡 Contoh Nyata Input Teks Breakdown Materi:

```markdown
# Breakdown Modul: Prosedur Pengajuan Cuti Karyawan (SOP-HC-004)

## Slide 1: Tata Cara Pengajuan Cuti
type: cover
category: Pendahuluan
duration: 00:30
icon: verified_user
narration: Selamat datang pada modul interaktif pengajuan cuti tahunan dan khusus karyawan.
heroTitle: Prosedur Pengajuan Cuti Karyawan
heroLead: Panduan standar operasional pengajuan, verifikasi, dan persetujuan cuti.
heroMeta: SOP-HC-004 · Revisi 2 · Berlaku 2026
ctaLabel: Mulai Belajar
reasons:
  - icon: schedule
    title: Tepat Waktu
    desc: Pengajuan minimal H-3 sebelum tanggal pelaksanaan cuti.
  - icon: approval
    title: Alur Berjenjang
    desc: Persetujuan Atasan Langsung hingga Manager HRD.

## Slide 2: Jenis Hak Cuti Karyawan
type: cardList
category: Materi Pokok
duration: 01:30
icon: category
narration: Kenali tiga kategori hak cuti yang berlaku di perusahaan.
title: 3 Kategori Hak Cuti
lead: Pelajari ketentuan dan kuota masing-masing cuti berikut
columns: 3
cards:
  - icon: event_available
    title: Cuti Tahunan
    desc: Hak 12 hari kerja per tahun setelah masa kerja minimal 12 bulan berturut-turut.
  - icon: medical_services
    title: Cuti Sakit
    desc: Wajib melampirkan surat keterangan dokter resmi jika melebihi 1 hari kerja.
  - icon: celebration
    title: Cuti Khusus / Ibadah
    desc: Termasuk cuti menikah (3 hari), melahirkan (3 bulan), dan ibadah haji.

## Slide 3: Alur Verifikasi & Persetujuan
type: stepByStep
category: Prosedur
duration: 02:00
icon: linear_scale
narration: Ikuti 4 tahapan berurutan pengajuan cuti melalui portal HC.
title: 4 Langkah Pengajuan di Portal HRIS
steps:
  - step: 1
    title: Input Pengajuan di HRIS
    desc: Karyawan login ke portal dan mengisi tanggal serta alasan cuti.
  - step: 2
    title: Review Atasan Langsung
    desc: Atasan memeriksa sisa kuota dan jadwal operasional tim kerja.
  - step: 3
    title: Persetujuan HRD
    desc: Tim HR memvalidasi eligibilitas dan menerbitkan notifikasi persetujuan.
  - step: 4
    title: Notifikasi Otomatis
    desc: Surat izin cuti elektronik dikirimkan ke email karyawan dan atasan.

## Slide 4: Simulasi Pengambilan Keputusan
type: scenarioPicker
category: Studi Kasus
duration: 02:00
icon: psych
narration: Uji pemahaman Anda terhadap kasus darurat di lapangan.
title: Dilema Cuti Mendadak
scenario: Karyawan A mengalami musibah darurat keluarga pada hari H kerja dan belum sempat mengajukan di portal. Apa langkah yang tepat?
options:
  - label: A. Menunggu masuk kerja baru mengurus izin cuti seminggu kemudian.
    isCorrect: false
    feedback: Kurang tepat. Karyawan wajib segera memberi kabar kepada atasan langsung di hari yang sama.
  - label: B. Memberitahu atasan via telepon/pesan hari itu juga, lalu input form HRIS maksimal H+1 masuk kerja.
    isCorrect: true
    feedback: Benar! Prosedur darurat memperbolehkan pelaporan verbal terlebih dahulu diikuti input administratif resmi.

## Slide 5: Uji Pemahaman (Quiz)
type: quiz
category: Evaluasi
duration: 03:00
icon: quiz
narration: Jawab 2 pertanyaan berikut untuk menguji pemahaman Anda. Syarat kelulusan minimal 80.
title: Evaluasi Pemahaman Kuis
passingScore: 80
questions:
  - id: 1
    type: mcq
    question: Berapa hari batas minimal pengajuan cuti tahunan normal sebelum tanggal pelaksanaan?
    options:
      - H-1 hari kerja
      - H-3 hari kerja
      - H-7 hari kerja
      - Hari H keberangkatan
    correctIndex: 1
    explanation: Sesuai SOP, pengajuan normal wajib dilakukan minimal H-3 agar atasan dapat mengatur jadwal tugas tim.
  - id: 2
    type: trueFalse
    question: Cuti sakit selama lebih dari 1 hari wajib disertai surat keterangan dokter resmi.
    correctBool: true
    explanation: Surat dokter resmi diperlukan untuk validasi absensi medis berbayar.

## Slide 6: Rangkuman & Sertifikat
type: summaryCertificate
category: Penutup
duration: 00:30
icon: workspace_premium
narration: Selamat! Anda telah menyelesaikan seluruh rangkaian materi dan lulus evaluasi.
title: Sertifikat Kompetensi
certificate:
  courseTitle: "Pelatihan Prosedur Pengajuan Cuti (SOP-HC-004)"
  signatoryTitle: "Head of Human Capital"
  signatoryName: "Direktur HC & Legal"
takeaways:
  - "Pengajuan cuti tahunan dilakukan minimal H-3 via portal HRIS."
  - "Kondisi darurat wajib dilaporkan di hari yang sama kepada atasan langsung."
  - "Sertifikat resmi diterbitkan otomatis setelah lulus kuis dengan skor >= 80."
```

---

### Alur 3: Kompilasi Manual Menggunakan CLI Python

Jika Anda memiliki data dalam format JSON (`kursus.json`):

1. **Validasi Skema**:
   ```bash
   python scripts/validate_content.py kursus.json
   ```
2. **Kompilasi ke HTML Mandiri**:
   ```bash
   python scripts/build_module.py \
     --content kursus.json \
     --output dist/kursus_interaktif.html \
     --validate
   ```
3. Buka file `dist/kursus_interaktif.html` di browser Anda!

---

## ✨ Fitur Teknis & Arsitektur Keamanan

### 1. ⏱️ 10-Second Slide Gating Timer
- Mencegah peserta melakukan *skipping* materi tanpa membaca.
- Tombol **Lanjut (Next)** otomatis terkunci (`disabled`) selama 10 detik saat slide baru dibuka, lengkap dengan hitung mundur dinamis (`Tunggu (10s)` $\rightarrow$ `Tunggu (1s)`).
- Menampilkan countdown badge di bar durasi atas (`⏳ Selesaikan materi dalam Xs...`).
- Notifikasi peringatan jika user mencoba melompat lewat daftar isi/sidebar sebelum timer selesai.
- Dilengkapi efek *unlock chime* (Web Audio) dan animasi pulse glow saat waktu tuntas.
- Slide yang sudah tuntas dipelajari tidak dikunci ulang saat dibuka kembali.

### 2. 📝 Native In-App Quiz & Anti-Spam (Maksimal 5 Attempt)
- Formulir identitas peserta langsung di aplikasi: Nama Lengkap, NIP/NRP, Jabatan, dan Divisi/Departemen.
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
- Panduan setup lengkap: [`references/gas_webhook_setup.md`](references/gas_webhook_setup.md).

### 4. 🧩 18 Tipe Slide Interaktif
1. `cover`: Hero title, badge versi, deskripsi, dan CTA mulai.
2. `cardList`: Kartu interaktif grid dengan icon, detail modal, dan status.
3. `treeCanvas`: Alur proses flowchart interaktif dengan zoom/pan, filter peran (*Role Filter*), dan modal hotspot.
4. `scenarioPicker`: Simulasi pengambilan keputusan / dilema etika dengan umpan balik instan.
5. `tabbedAccordion`: Navigasi tab konten berbasis pilar/tahapan.
6. `verificationMatrix`: Matriks verifikasi dokumen dengan status lulus/tinjau.
7. `twoCardAccordion`: Komparasi 2 kartu interaktif (*sebelum vs sesudah, do vs don't*).
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
├── LICENSE                           # Lisensi open-source MIT
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
