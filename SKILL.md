---
name: doc-to-interactive
description: Transform raw training documents, SOPs, syllabi, or slide breakdowns into production-ready, self-contained interactive e-learning modules (single HTML file) with 18 slide types, slide gate timers, anti-spam quiz evaluations, Google Sheets sync, and certificate printing. Use when user asks to build interactive modules or types /elearning, /modul, /doc-to-interactive.
---

# Doc to Interactive E-Learning Module Builder Skill (/doc-to-interactive, /elearning, /modul)

Build production-ready, self-contained interactive e-learning modules (single HTML file) from a slide-by-slide content breakdown + optional reference documents.

## What this skill produces

A **single `.html` file** that runs in any modern browser (open via `file://`, no server needed). Each module includes:

- Top player bar (logo, course code, theme toggle, fullscreen, modals)
- Collapsible sidebar (Menu / Notes / Resources tabs)
- Central 16:9 slide viewport with category badge + duration label
- Bottom playbar (play/pause, seekbar, speed, prev/next, slide counter)
- Per-slide audio narration (mp3 file or 45-second fallback simulator)
- Closed-caption (CC) dock + sidebar Notes tab (both driven from same transcript)
- 18 slide types: `cover`, `cardList`, `treeCanvas`, `scenarioPicker`, `tabbedAccordion`, `verificationMatrix`, `twoCardAccordion`, `docTabs`, `kpiDashboard`, `riskCards`, `quiz`, `summaryCertificate`, `imageGallery`, `videoEmbed`, `calloutBox`, `stepByStep`, `comparisonTable`, `faqAccordion`
- Dark/light theme toggle (default dark)
- 4 brand presets (`ptpp`, `corporate`, `education`, `tech-startup`) + custom inline
- Quiz formats: MCQ + True/False + Fill-in-the-blank (shuffled options, 1-question-per-screen, post-submit review)
- Certificate generator (A4 landscape print, auto reg-number + date)
- Pan/zoom canvas for tree diagrams with role filter + phase jumps + hotspot modal
- Tenggat cheat-sheet modal, Terminologi (glossary) modal, Petunjuk (help) modal
- Tactile Web Audio tones (click / success / error / fanfare)
- WCAG 2.2 AA keyboard nav + ARIA roles
- Canvas confetti for celebrations

## Skill architecture

```
skills/elearning-module-builder/
├── SKILL.md                         (this file)
├── assets/
│   ├── shell.template.html          (the reusable shell — 2900+ lines, do NOT hand-edit)
│   ├── content.schema.json          (JSON Schema for content.json validation)
│   ├── brand.profiles.json          (4 brand presets)
│   └── sample.content.json          (working example — 6-slide module demonstrating all key types)
├── scripts/
│   ├── build_module.py              (inject content.json + brand → final HTML)
│   ├── validate_content.py          (validate content.json against schema)
│   └── build_shell_template.py      (regenerate shell.template.html from upstream original — used by skill maintainer, not by AI in normal workflow)
└── references/
    ├── slide_types.md               (per-type field reference for all 18 slide types — READ when picking slide types for the user's content)
    ├── input_format.md              (how the user should structure the slide breakdown input)
    └── brand_profiles.md            (how brand presets work + how to add custom)
```

## Workflow (always follow these steps)

### Step 1 — Read the user's slide breakdown + reference docs

The user will provide a slide-by-slide breakdown in **structured bullets** format (see `references/input_format.md` for the canonical spec). They may also attach reference docs (PDF, DOCX, MD, TXT) — read them to enrich the content.

If the user provides prose instead of structured bullets, gently extract the structure:
- Slide N → slideDef.type → fields per the schema
- If unclear which slide type fits, consult `references/slide_types.md` for the full taxonomy + decision tree

### Step 2 — Pick the brand profile

Default to `corporate`. Override only if the user's context suggests otherwise:
- Indonesian state-owned enterprise / infrastructure → `ptpp`
- Generic corporate training → `corporate` (default)
- School / academic / continuing education → `education`
- Tech startup / engineering playbook → `tech-startup`
- User wants full control over colors → `custom` (inline fields required)

If unsure, ask the user. Otherwise use `corporate` and tell them they can change it post-build by editing `brand.preset` in content.json and re-running `build_module.py`.

### Step 3 — Build `content.json`

Construct the JSON following `assets/content.schema.json`. Key rules:

1. **units[] and slides[] MUST have the same length** — `units[N]` is the sidebar entry for `slides[N]`.
2. **Each slide.type** must be one of the 18 supported types. Per-type required fields are in `references/slide_types.md`.
3. **narration** is optional but recommended — drives both the CC dock and the sidebar Notes tab. Key is the slide index as a STRING (e.g., `"0"`, `"1"`).
4. **glossary**, **tenggatCheatSheet**, **hintTips**, **resources** are all optional — omit if the module doesn't need them.
5. **brand** block: either `{"preset": "name"}` (resolves from `brand.profiles.json`) OR `{"preset": "custom", ...inline fields}`.

### Step 4 — Save content.json

Save to `/home/z/my-project/scripts/<module-name>.content.json` (NOT in the skill directory — keep the skill clean).

### Step 5 — Validate

```bash
python3 <skill-root>/scripts/validate_content.py <content.json>
```

Must exit with code 0 and print `✓ Valid!`. Fix any errors before proceeding.

### Step 6 — Build

```bash
python3 <skill-root>/scripts/build_module.py \
  --content <content.json> \
  --output /home/z/my-project/download/<module-name>.html \
  --validate
```

The build script:
1. Injects `content.json` as the `COURSE` object literal into the template.
2. Resolves the brand preset and applies the brand's hex colors to the Tailwind config + CSS rules (every brand color token gets overridden).
3. Replaces all `__COURSE_*__` and `__CERT_*__` placeholders with concrete values.
4. Writes the final HTML to the user-facing `download/` directory.

### Step 7 — Smoke test (optional but recommended)

```bash
python3 /home/z/my-project/scripts/smoke_test_module.py /home/z/my-project/download/<module-name>.html
```

The smoke test loads the module in headless Chromium and verifies:
- All key DOM elements exist (`#topHeader`, `#courseSidebar`, `#slideBody`, `#bottomPlaybar`, `#seekBar`, etc.)
- `COURSE` object is loaded with the correct `units.length` / `slides.length`
- Navigation via `goToSlide()` works (slide counter updates)
- Quiz slide renders `#quizContainer` properly
- Tree-canvas slide renders `.flow-card-node` elements
- Tenggat modal opens successfully
- No runtime errors / unhandled exceptions

Expected non-fatal warnings:
- `cdn.tailwindcss.com should not be used in production` — cosmetic, expected for single-file distribution.
- `AudioContext was not allowed to start` — browser autoplay policy; resumes on first user interaction.
- `Failed to load resource: ERR_FILE_NOT_FOUND` — for missing `assets/logo.png` or `audio/unit_N.mp3` if not provided by the user.

### Step 8 — Report to user

Tell the user:
- The final HTML file path (in `/home/z/my-project/download/`)
- Brand preset used
- Number of slides + a quick type breakdown
- Any non-fatal warnings to ignore
- Suggest next steps: attach real logo + audio mp3 files, iterate content by editing content.json + re-running `build_module.py`

## Critical rules (the "why" matters)

1. **Always validate before building.** A malformed `content.json` will produce a module that loads with a red error message instead of content. The validator catches schema violations + cross-field consistency (units.length == slides.length).

2. **Never hand-edit `shell.template.html` for content changes.** All content lives in `content.json`. If the shell itself needs a fix (a renderer bug, a missing feature), regenerate it via `scripts/build_shell_template.py` from the upstream original at `/home/z/my-project/upload/index_tree_canvas.html`. Editing the shell by hand makes future regenerations lose your changes.

3. **The `slides[]` array IS the slide order.** Sidebar outline entries (`units[]`) follow the same order. Don't try to "skip" slides by leaving gaps — the engine doesn't support conditional slides. If you need fewer slides, just shorten both arrays.

4. **Each slide.type has a fixed set of expected fields.** Mismatched fields are silently ignored (renderer just doesn't use them), but missing REQUIRED fields will render empty/blank sections. Always consult `references/slide_types.md` when unsure.

5. **Quiz questions can be mixed.** A single quiz slide can contain MCQ, True/False, and Fill-in questions in any order. Each question's `type` discriminator (`mcq` / `trueFalse` / `fillIn`) determines which fields are required.

6. **Brand color tokens are hex without `#`.** When defining a custom brand inline, write `"primary": "2B73BD"` (NOT `"#2B73BD"`). The build script adds the `#` prefix.

7. **Audio files follow the convention `./audio/unit_<slideIndex>.mp3`.** If absent, the 45-second simulator drives the seekbar and triggers `completeCurrentSlideTask()` at the end. Users can drop real mp3 files into the module's directory at any time without rebuilding.

8. **Certificate is triggered only on quiz pass.** The summary certificate slide conditionally renders the name/NIP inputs + "Cetak Sertifikat" button only if `state.quizCompleted && state.quizScore >= COURSE.course.passingScore`. Set `passingScore` in `course` block (default 80).

## Output format

Final deliverable: a single `.html` file at `/home/z/my-project/download/<module-name>.html` (~150-200 KB, fully self-contained). The user can:
- Open it directly in a browser via `file://` (no server)
- Host it on any static web server
- Embed it in an LMS via `<iframe>`
- Print certificates to PDF (A4 landscape)

## Examples

### Example 1: Minimal 3-slide module

User: "Bikin modul simpel 3 slide: cover judul 'Welcome', 1 slide card list 3 kartu, 1 slide quiz MCQ 2 soal. Brand corporate."

Slide breakdown → content.json structure:
```json
{
  "course": { "code": "WELCOME-001", "title": "Welcome Module", "totalUnits": 3, "passingScore": 70, "totalQuestions": 2 },
  "brand": { "preset": "corporate" },
  "units": [
    { "title": "0. Welcome",  "icon": "info", "duration": "00:20", "category": "Intro" },
    { "title": "1. Concepts", "icon": "school", "duration": "01:00", "category": "Content" },
    { "title": "2. Quiz",     "icon": "quiz", "duration": "01:00", "category": "Quiz" }
  ],
  "slides": [
    { "type": "cover", "heroTitle": "Welcome", "heroLead": "...", "ctaLabel": "Start" },
    { "type": "cardList", "title": "3 Concepts", "cards": [ ...3 cards... ] },
    { "type": "quiz", "questions": [ ...2 MCQs... ] }
  ]
}
```

### Example 2: Convert user's prose breakdown to structured

User: "Slide 1 cover judul X. Slide 2 4 alasan perubahan. Slide 3 tree diagram alur. Slide 4 quiz 5 soal. Slide 5 sertifikat."

You convert each prose line into the matching slideDef type:
- "cover judul X" → `{"type": "cover", "heroTitle": "X", ...}`
- "4 alasan perubahan" → `{"type": "cover"... }` OR `{"type": "cardList", "cards": [...4 cards...]}` (cardList is more reusable)
- "tree diagram alur" → `{"type": "treeCanvas", "swimlaneData": [...], "flowCard": {...}}`
- "quiz 5 soal" → `{"type": "quiz", "questions": [...5 questions...]}`
- "sertifikat" → `{"type": "summaryCertificate", "takeaways": [...], "certificate": {...}}`

### Example 3: Mixed quiz types

```json
{
  "type": "quiz",
  "questions": [
    { "id": 1, "type": "mcq", "question": "...", "options": ["A","B","C","D"], "correctIndex": 0, "explanation": "..." },
    { "id": 2, "type": "trueFalse", "question": "...", "correctBool": true, "explanation": "..." },
    { "id": 3, "type": "fillIn", "question": "...", "acceptedAnswers": ["PFC","pfc"], "placeholder": "3 huruf...", "explanation": "..." }
  ]
}
```

## Frequently asked questions

**Q: Can the user add a new slide type not in the 18?**
A: Not via content.json alone — they'd need to add a renderer function to `shell.template.html` and register it in the `SLIDE_RENDERERS` map. This requires editing the shell template directly. Refer them to the skill maintainer (you, the AI agent reading this) — adding a new type means extending `build_shell_template.py`'s `NEW_RENDER_DISPATCHER` block + extending `content.schema.json` + updating `references/slide_types.md`.

**Q: Can the module use real audio narration?**
A: Yes. Drop mp3 files at `./audio/unit_0.mp3`, `./audio/unit_1.mp3`, ... next to the built HTML. The audio engine auto-detects and uses them. If absent, the 45-second fallback simulator drives the seekbar identically.

**Q: How does certificate printing work?**
A: User clicks "Cetak Sertifikat" on the summary slide. The build script populates `#certificatePrintArea` with brand org name, signatory, reg number (random), today's date, recipient name + NIP, then calls `window.print()`. Browser print dialog with A4 landscape + `@media print` rules produces a clean certificate PDF.

**Q: Can the module be embedded in an LMS?**
A: Yes — single self-contained HTML file with no external dependencies (except CDN-loaded Tailwind, fonts, confetti, icons). Embed via `<iframe src="module.html">`. Progress is NOT persisted across refreshes (state is in-memory only).

**Q: How to update content after the first build?**
A: Edit `content.json`, re-run `build_module.py`. The shell template never changes between content updates — only the injected `COURSE` literal + the placeholder substitutions.

## Failure modes to watch for

- **`Unknown slide type: <X>`** — the user's content.json used a `type` value not in the 18 supported. Check `references/slide_types.md` for the canonical list.
- **`#slideBody` shows red error** — a slide renderer threw an exception. Check the browser console. Most common cause: a required field is missing for the slide type (e.g., `cover` without `heroTitle`).
- **`goToSlide is not defined`** at runtime — the script tag failed to parse. Run `node --check` on the extracted JS to find the syntax error.
- **Certificate not rendering on slide 11** — user hasn't passed the quiz yet. Verify `state.quizCompleted` is true + `state.quizScore >= COURSE.course.passingScore`.
- **Colors look wrong (still PT PP blue)** — brand preset not resolved. Verify `brand.preset` in content.json matches a key in `brand.profiles.json` (case-sensitive).
- **Tailwind classes not applying** — Tailwind CDN loaded but failed. Check network connectivity. The CDN is `https://cdn.tailwindcss.com`.

## What NOT to do

- Don't write slide content directly into `shell.template.html`. All content lives in `content.json`.
- Don't use a multi-file structure (separate JS, CSS). The shell is intentionally single-file for portability.
- Don't add `localStorage` / `sessionStorage` persistence — the engine is in-memory only by design.
- Don't try to render slides server-side — everything runs client-side in the browser.
- Don't skip the validation step. A malformed content.json produces a broken module.
- Don't hand-edit `shell.template.html` for content changes. Edit `content.json` and re-run `build_module.py`.

## Reference paths (relative to skill root)

- `assets/shell.template.html` — the reusable HTML shell (do NOT hand-edit for content)
- `assets/content.schema.json` — JSON Schema for content.json
- `assets/brand.profiles.json` — 4 brand presets (ptpp / corporate / education / tech-startup)
- `assets/sample.content.json` — working 6-slide example
- `scripts/build_module.py` — content.json → final HTML
- `scripts/validate_content.py` — content.json schema validator
- `scripts/build_shell_template.py` — regenerates shell from upstream (skill maintainer use only)
- `references/slide_types.md` — per-type field reference for all 18 slide types
- `references/input_format.md` — how the user should structure the slide breakdown input
- `references/brand_profiles.md` — brand preset details + how to add custom


## Fitur Ekstensi: Native In-App Quiz & Google Sheets Webhook Sync

Ketika modul membutuhkan evaluasi pemahaman (Level 2) yang terintegrasi langsung tanpa ketergantungan iframe Google Form, gunakan arsitektur **Native In-App Quiz dengan Dual-Sync**:

### 1. Spesifikasi Fitur
- **Kartu Identitas Peserta**: Input Nama Lengkap, NIP/NRP, Jabatan, dan Divisi/Unit Kerja langsung di halaman kuis.
- **Kalkulasi Skor Otomatis**: Menghitung skor real-time (0 - 100) berbasis bobot jawaban benar.
- **Passing Grade Gating**:
  - Skor $\ge$ ambang batas (default 80): Membuka gembok halaman Sertifikat Resmi, memicu selebrasi (Canvas Confetti & Fanfare Web Audio), dan melakukan pengiriman data otomatis.
  - Skor < ambang batas: Menampilkan kartu evaluasi remedial, mengunci halaman sertifikat, dan menyediakan tombol *Ulangi Kuis (Retake)*.
- **Google Sheets Serverless Webhook Sync**:
  - Mengirim payload JSON via etch(WEBHOOK_URL, {method: 'POST', body: JSON.stringify({...})}) ke Google Apps Script.
  - Aman dan tahan beban antrean serentak 50+ peserta menggunakan LockService.getScriptLock() pada Google Cloud engine.


### 2. Standar Google Apps Script Webhook Receiver (Anti-Spam & Upsert Nilai Tertinggi)
```javascript
function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.tryLock(10000); // Mencegah race condition (aman untuk 50+ peserta serentak)
  
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var data = JSON.parse(e.postData.contents);
    
    var newNip = String(data.nip || "").trim();
    var newScore = Number(data.skor) || 0;
    
    if (!newNip) {
      return ContentService.createTextOutput(JSON.stringify({result: "error", message: "NIP wajib ada"}))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    var lastRow = sheet.getLastRow();
    var foundRowIndex = -1;
    var existingScore = -1;
    
    // Header diasumsikan ada di baris 1:
    // Col 1: Timestamp | Col 2: Nama | Col 3: NIP | Col 4: Jabatan | Col 5: Divisi | Col 6: Skor | Col 7: Status | Col 8: Attempt
    if (lastRow > 1) {
      var nipRange = sheet.getRange(2, 3, lastRow - 1, 1).getValues(); // Ambil seluruh kolom NIP (Kolom C)
      var scoreRange = sheet.getRange(2, 6, lastRow - 1, 1).getValues(); // Kolom Skor (Kolom F)
      
      for (var i = 0; i < nipRange.length; i++) {
        if (String(nipRange[i][0]).trim() === newNip) {
          foundRowIndex = i + 2;
          existingScore = Number(scoreRange[i][0]) || 0;
          break;
        }
      }
    }
    
    if (foundRowIndex > -1) {
      // Jika NIP sudah ada, HANYA TIMPA jika nilai baru LEBIH TINGGI
      if (newScore > existingScore) {
        sheet.getRange(foundRowIndex, 1).setValue(new Date());
        sheet.getRange(foundRowIndex, 2).setValue(data.nama);
        sheet.getRange(foundRowIndex, 4).setValue(data.jabatan);
        sheet.getRange(foundRowIndex, 5).setValue(data.divisi);
        sheet.getRange(foundRowIndex, 6).setValue(newScore);
        sheet.getRange(foundRowIndex, 7).setValue(data.status);
        if (data.attempt) sheet.getRange(foundRowIndex, 8).setValue(data.attempt);
        
        return ContentService.createTextOutput(JSON.stringify({result: "updated", message: "Data lama ditimpa dengan nilai lebih tinggi"}))
          .setMimeType(ContentService.MimeType.JSON);
      } else {
        return ContentService.createTextOutput(JSON.stringify({result: "skipped", message: "Nilai lama lebih tinggi atau sama, tidak ditimpa"}))
          .setMimeType(ContentService.MimeType.JSON);
      }
    } else {
      // Jika NIP belum ada sama sekali, tambahkan baris baru
      sheet.appendRow([
        new Date(),
        data.nama,
        data.nip,
        data.jabatan,
        data.divisi,
        newScore,
        data.status,
        data.attempt || 1
      ]);
      return ContentService.createTextOutput(JSON.stringify({result: "created", message: "Baris baru berhasil ditambahkan"}))
        .setMimeType(ContentService.MimeType.JSON);
    }
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({result: "error", error: err.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}
```

### 3. Gating System: 10-Second Gate Timer per Slide
Untuk memastikan peserta benar-benar membaca dan mempelajari materi sebelum melompat ke slide berikutnya, gunakan sistem pembatasan waktu (Slide Gate Timer):
- **Waktu Minimal Membaca**: Nilai default adalah `10` detik per slide (didefinisikan di `COURSE_CONFIG.gatingSeconds: 10`).
- **State & Navigasi**:
  - `state.slideGateSecondsLeft`: menyimpan sisa detik hitung mundur untuk slide yang sedang aktif.
  - `state.isGateTimerActive`: boolean penanda apakah timer sedang berjalan.
  - `state.completedSlides`: `Set` yang menyimpan indeks slide yang telah tuntas dipelajari minimal selama durasi gate.
- **Interaksi Tombol "Lanjut" (Next)**:
  - Saat slide baru dibuka, tombol `#btnNextSlide` otomatis berstatus `disabled` dengan visual redup (`opacity-40 cursor-not-allowed`).
  - Label tombol menampilkan countdown dinamis: `Tunggu (10s)`, `Tunggu (9s)`, dst.
  - Indikator badge waktu di stage bar menampilkan pesan peringatan hitung mundur: `⏳ Selesaikan materi dalam Xs...`.
  - Jika peserta mencoba mengklik slide berikutnya via daftar isi/outline sebelum 10 detik habis, sistem menampilkan modal/alert edukatif: `Mohon pelajari materi ini terlebih dahulu. Anda dapat lanjut dalam X detik.`
- **Penyelesaian Gate**:
  - Saat timer mencapai 0, Web Audio API memutar nada halus (unlock chime), tombol `#btnNextSlide` aktif kembali dengan efek pulse visual (`btn-next-ready`), dan slide dimasukkan ke dalam `state.completedSlides`.
- **Pengecualian Gating**:
  - **Slide yang Pernah Selesai**: Peserta yang kembali ke slide sebelumnya tidak akan dikunci ulang (`state.completedSlides.has(slideIndex)`).
  - **Slide Quiz & Sertifikat**: Otomatis melewati (bypass) timer reguler 10 detik karena memiliki gate evaluasi sendiri (menjawab seluruh soal kuis & ambang kelulusan $\ge 80$).

---

### 4. Anti-Spam & Limit Percobaan Kuis (Maksimal 5 Attempts)
Untuk mencegah eksploitasi brute-force jawaban atau spam data ke Google Sheets:
- **Batas Percobaan**: Maksimal 5 kali percobaan kuis (`COURSE_CONFIG.maxQuizAttempts: 5`).
- **Penyimpanan Attempt**:
  - Disimpan dalam `state.quizAttempts` dan disinkronkan ke `localStorage` (jika mode persistence aktif) atau memori sesi.
  - Setiap kali tombol submit diklik, counter attempt bertambah 1 (`attempt = state.quizAttempts`).
- **Gating Skor & Penguncian**:
  - **Lulus ($\ge 80$)**: Mengirimkan data ke Google Sheets, membuka sertifikat, dan menghentikan pengulangan.
  - **Gagal (< 80) & Attempt < 5**: Menyediakan tombol *Ulangi Kuis (Sisa X Percobaan)*.
  - **Gagal (< 80) & Attempt $\ge$ 5**: Kuis terkunci permanen. Tombol ulangi kuis dinonaktifkan (`disabled`) dan digantikan oleh instruksi: `Kesempatan kuis Anda telah habis (5/5). Silakan hubungi Tim HC / PIC Pelatihan untuk evaluasi lebih lanjut.` Data kuis tetap tidak dikirimkan ke sheet kelulusan untuk mencegah polusi data.

---

### 5. Gated Mode vs Dev Mode Governance
- **Production / Deployment Mode (`devMode: false`)**:
  - Semua gate aktif (10 detik timer, kuis terkunci hingga slide materi selesai, sertifikat terkunci hingga lulus kuis).
  - Badge review/dev tool disembunyikan.
  - Cocok untuk rilis produksi di LMS atau GitHub Pages.
- **Development / Review Mode (`devMode: true`)**:
  - Tombol cheat / dev menu diaktifkan (misal: tombol instan loncat ke kuis, isi otomatis kuis dengan skor 100, atau bypass gate timer untuk keperluan review dan QA).