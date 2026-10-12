#!/usr/bin/env python3
"""
build_shell_template.py

Transforms the original index_tree_canvas.html (the SOP-specific PT PP module)
into a generic, reusable shell template at:
  /home/z/my-project/skills/elearning-module-builder/assets/shell.template.html

Operations performed:
  1. Replace SOP-specific static strings (title, header badge, course title text,
     effective date, logo path) with build-time placeholders.
  2. Strip the SOP constants block (COURSE_CONFIG, DEFINISI_POIN_4, COURSE_UNITS,
     SWIMLANE_FLOWCHART, QUIZ_QUESTIONS, HP5_*, VERIF_*, LAMPIRAN_LIST, RECORD_LIST,
     RISK_LIST, FLOW_CARD, NARRATION_TRANSCRIPTS) and replace with a single
     `let COURSE = null; // __COURSE_DATA_INJECTION_POINT__` injection marker.
  3. Replace the hard-coded renderCurrentSlide() switch-case body with a generic
     type-dispatcher + 18 per-type renderer functions.
  4. Replace the old quiz engine with an extended one that handles mcq + trueFalse
     + fillIn types.
  5. Replace the bespoke testCompliance/testBranchPfc functions with a generic
     scenario picker dispatcher.
  6. Update openSwimlaneHotspot + updateTranscriptAndCC to read from COURSE.*
  7. Replace renderAuthenticSOPTree with a generic renderTreeCanvas(slideDef).
  8. Replace Tenggat modal static grid + Hint modal static tips with empty
     containers populated at init from COURSE.tenggatCheatSheet / COURSE.hintTips.
  9. Replace certificate static strings with placeholders.

Re-run any time the original file is updated, or the template logic needs revision.
"""
import re
import sys
from pathlib import Path

SRC = Path("/home/z/my-project/upload/index_tree_canvas.html")
DST = Path("/home/z/my-project/skills/elearning-module-builder/assets/shell.template.html")

# ────────────────────────────────────────────────────────────────────────────
# Read source
# ────────────────────────────────────────────────────────────────────────────
src_lines = SRC.read_text(encoding="utf-8").splitlines(keepends=True)
n = len(src_lines)
print(f"Source: {SRC} ({n} lines)")

# We'll splice the source into segments identified by 1-indexed line numbers
# (matching the output of grep -n above). Convert to 0-indexed Python slices.
def L(start_1, end_1_inclusive):
    """Return lines[start-1:end] as a single string (1-indexed inclusive)."""
    return "".join(src_lines[start_1 - 1:end_1_inclusive])

# ────────────────────────────────────────────────────────────────────────────
# 1. HEAD + BODY SKELETON (lines 1-786) — keep verbatim, but apply string
#    replacements for SOP-specific text.
# ────────────────────────────────────────────────────────────────────────────
head_and_skeleton = L(1, 786)

# Title tag
head_and_skeleton = head_and_skeleton.replace(
    "<title>SOP Masa Pemeliharaan & Penutupan Proyek Konstruksi & EPC (PP/SOP/C1-050 REV-3)</title>",
    "<title>__COURSE_TITLE__</title>"
)

# Header logo + course code badge + course title text
head_and_skeleton = head_and_skeleton.replace(
    'src="assets/logo_pp.png"',
    'src="__COURSE_LOGO__"'
)
head_and_skeleton = head_and_skeleton.replace(
    'alt="PT PP"',
    'alt="__COURSE_LOGO_ALT__"'
)
head_and_skeleton = head_and_skeleton.replace(
    "PP/SOP/C1-050 REV-3",
    "__COURSE_CODE__"
)
head_and_skeleton = head_and_skeleton.replace(
    "Berlaku: 31 Des 2024",
    "__COURSE_EFFECTIVE_DATE__"
)
# Course title text node — handle both & and &amp; forms
head_and_skeleton = head_and_skeleton.replace(
    "Masa Pemeliharaan &amp; Penutupan Proyek Konstruksi &amp; EPC",
    "__COURSE_TITLE_TEXT__"
)
head_and_skeleton = head_and_skeleton.replace(
    "Masa Pemeliharaan & Penutupan Proyek Konstruksi & EPC",
    "__COURSE_TITLE_TEXT__"
)
head_and_skeleton = head_and_skeleton.replace(
    "Masa Pemeliharaan & Penutupan Proyek Konstruksi dan EPC",
    "__COURSE_TITLE_TEXT__"
)
# Resources tab content (gets overwritten by initResources at runtime, but
# replace static SOP-specific text for cleanliness)
head_and_skeleton = head_and_skeleton.replace(
    "PP/SOP/E6-032",
    "__COURSE_CODE2__"
)
head_and_skeleton = head_and_skeleton.replace(
    "Form Pembebanan, Rencana, Tutup Buku I & II, Lesson Learned",
    "__COURSE_RESOURCES_DESC__"
)
# Terminologi search placeholder — make generic
head_and_skeleton = head_and_skeleton.replace(
    'placeholder="Cari istilah (contoh: PFC, Tutup Buku, Contingency, Hold Point V)..."',
    'placeholder="__GLOSSARY_SEARCH_PLACEHOLDER__"'
)
# Hotspot modal default text — gets overwritten by openSwimlaneHotspot at runtime
head_and_skeleton = head_and_skeleton.replace(
    '>Tahap 5.1</span>',
    '>Tahap</span>'
)
head_and_skeleton = head_and_skeleton.replace(
    '>Penyelesaian Proyek</h3>',
    '>Detail Proses</h3>'
)
# Certificate static strings in HTML body
head_and_skeleton = head_and_skeleton.replace(
    "PT PP (Persero) Tbk",
    "__CERT_BRAND_NAME__"
)
head_and_skeleton = head_and_skeleton.replace(
    "Human Capital Management & Quality Assurance",
    "__CERT_DIVISION__"
)
head_and_skeleton = head_and_skeleton.replace(
    "SVP - Operation Control & SCC",
    "__CERT_SIGNATORY__"
)
head_and_skeleton = head_and_skeleton.replace(
    "Standard Operating Procedure",
    "__CERT_TITLE__"
)
head_and_skeleton = head_and_skeleton.replace(
    "No. Reg: PP/HCM-QA/CERT/2026/0982",
    "No. Reg: __CERT_REG_PREFIX__/2026/0000"
)

# Tenggat modal: replace the static cheat-sheet grid with an empty container
# populated at init from COURSE.tenggatCheatSheet.
TENGAT_OPEN = '<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">'
tenggat_grid_start = head_and_skeleton.find(TENGAT_OPEN)
if tenggat_grid_start != -1:
    # Find the matching closing </div> at the same depth
    depth = 1
    pos = tenggat_grid_start + len(TENGAT_OPEN)
    while depth > 0 and pos < len(head_and_skeleton):
        next_open = head_and_skeleton.find('<div', pos)
        next_close = head_and_skeleton.find('</div>', pos)
        if next_close == -1:
            break
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open + 4
        else:
            depth -= 1
            pos = next_close + 6
    if depth == 0:
        head_and_skeleton = (head_and_skeleton[:tenggat_grid_start]
                             + '<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs" id="tenggatGrid">\n        <!-- Populated by initCheatSheet() from COURSE.tenggatCheatSheet -->\n      '
                             + head_and_skeleton[pos - 1:])
        print("  Replaced Tenggat cheat-sheet grid with empty container.")
    else:
        print("  WARN: Could not find Tenggat grid closing tag.", file=sys.stderr)
else:
    print("  WARN: Could not find Tenggat grid opening tag.", file=sys.stderr)

# Hint modal: replace the static 4-tip block with an empty container
HINT_OPEN = '<div class="space-y-3 text-xs text-slate-600 dark:text-slate-300">'
hint_modal_start = head_and_skeleton.find('id="modalHint"')
if hint_modal_start != -1:
    hint_grid_start = head_and_skeleton.find(HINT_OPEN, hint_modal_start)
    if hint_grid_start != -1:
        depth = 1
        pos = hint_grid_start + len(HINT_OPEN)
        while depth > 0 and pos < len(head_and_skeleton):
            next_open = head_and_skeleton.find('<div', pos)
            next_close = head_and_skeleton.find('</div>', pos)
            if next_close == -1:
                break
            if next_open != -1 and next_open < next_close:
                depth += 1
                pos = next_open + 4
            else:
                depth -= 1
                pos = next_close + 6
        if depth == 0:
            head_and_skeleton = (head_and_skeleton[:hint_grid_start]
                                 + '<div class="space-y-3 text-xs text-slate-600 dark:text-slate-300" id="hintGrid">\n      <!-- Populated by initHintTips() from COURSE.hintTips -->\n    '
                                 + head_and_skeleton[pos - 1:])
            print("  Replaced Hint tips block with empty container.")
        else:
            print("  WARN: Could not find Hint block closing tag.", file=sys.stderr)
    else:
        print("  WARN: Could not find Hint block opening tag.", file=sys.stderr)
else:
    print("  WARN: Could not find Hint modal.", file=sys.stderr)

# Certificate static strings
head_and_skeleton = head_and_skeleton.replace("PT PP (PERSERO) TBK", "__CERT_BRAND_NAME__")
head_and_skeleton = head_and_skeleton.replace("Human Capital Management & Quality Assurance", "__CERT_DIVISION__")
head_and_skeleton = head_and_skeleton.replace("SVP - Operation Control & SCC", "__CERT_SIGNATORY__")
head_and_skeleton = head_and_skeleton.replace("Standard Operating Procedure", "__CERT_TITLE__")

# ────────────────────────────────────────────────────────────────────────────
# 2. CONSTANTS BLOCKS — TWO STRIPS, keep engine code between them.
#    Strip A: lines 787-1306 (COURSE_CONFIG, DEFINISI_POIN_4, COURSE_UNITS,
#             SWIMLANE_FLOWCHART, QUIZ_QUESTIONS — pure data).
#    Keep:    lines 1308-1642 (state + audio engine + navigation engine + UI
#             helpers — engine code that just references the constants).
#    Strip B: lines 1647-1744 (HP5_AGENDA, HP5_OUTPUT, VERIF_*, LAMPIRAN_LIST,
#             RECORD_LIST, RISK_LIST, FLOW_CARD — pure data).
# ────────────────────────────────────────────────────────────────────────────
COURSE_PLACEHOLDER = """
    // ========================================================================
    // COURSE DATA — INJECTED AT BUILD TIME BY build_module.py
    //
    // The `COURSE` object shape is defined by:
    //   assets/content.schema.json
    //
    // It contains:
    //   course  — code, title, logo, effectiveDate, totalUnits, passingScore,
    //             totalQuestions, devMode, defaultDark, enableGatingTimer
    //   brand   — resolved brand profile (preset + inline overrides) applied
    //             via build-time string placeholders in this very template.
    //   units   — sidebar outline entries (title/subtitle/icon/duration/category)
    //   slides  — array of slideDef objects, each with `type` discriminator +
    //             type-specific fields (see references/slide_types.md).
    //   glossary     — optional terminology entries for the Terminologi modal.
    //   narration    — {slideIndex: transcriptString} for CC dock + Notes tab.
    //   tenggatCheatSheet — optional quick-reference cards for Tenggat modal.
    //   hintTips     — optional navigation tips for Petunjuk modal.
    //   resources    — optional cards for sidebar Resources tab.
    //
    // build_module.py replaces the __COURSE_DATA_INJECTION_POINT__ marker below
    // with `let COURSE = { ...content.json... };` — a single literal assignment.
    // ========================================================================
    let COURSE = null; // __COURSE_DATA_INJECTION_POINT__

"""

# Engine block: lines 1308-1642 — state, audio, navigation, UI helpers
# Apply COURSE_CONFIG → COURSE.course + COURSE_UNITS → COURSE.units patches.
engine_state_audio_nav = L(1308, 1642)
engine_state_audio_nav = engine_state_audio_nav.replace(
    "COURSE_CONFIG.totalUnits", "COURSE.units.length"
)
engine_state_audio_nav = engine_state_audio_nav.replace(
    "COURSE_CONFIG.devMode", "COURSE.course.devMode"
)
engine_state_audio_nav = engine_state_audio_nav.replace(
    "COURSE_CONFIG.passingScore", "COURSE.course.passingScore"
)
engine_state_audio_nav = engine_state_audio_nav.replace(
    "COURSE_CONFIG.totalQuestions", "COURSE.course.totalQuestions"
)
engine_state_audio_nav = engine_state_audio_nav.replace(
    "COURSE_CONFIG", "COURSE.course"
)
engine_state_audio_nav = engine_state_audio_nav.replace(
    "COURSE_UNITS", "COURSE.units"
)

# ────────────────────────────────────────────────────────────────────────────
# 3. CORE ENGINE PIECES (lines 1745-1789) — renderFlowNode() and the comment
#    header for renderCurrentSlide. Keep verbatim; we'll override renderFlowNode's
#    FLOW_CARD reference inside its body via string replace below.
# ────────────────────────────────────────────────────────────────────────────
render_flow_node_block = L(1745, 1789)
# Update renderFlowNode to read FLOW_CARD from the current slide's data
# (currentSlide is a treeCanvas slide).
render_flow_node_block = render_flow_node_block.replace(
    "const c = FLOW_CARD[item.id] || { t: item.title };",
    "const fc = (COURSE.slides[state.currentSlide].flowCard) || {};\n      const c = fc[item.id] || { t: item.title };"
)

# ────────────────────────────────────────────────────────────────────────────
# 4. NEW renderCurrentSlide() DISPATCHER + 18 TYPE RENDERERS
#    (replaces lines 1790-2481 — the entire old switch-case body)
# ────────────────────────────────────────────────────────────────────────────
NEW_RENDER_DISPATCHER = r'''
    // ========================================================================
    // SLIDE CONTENT RENDERER (DATA-DRIVEN)
    //
    // `renderCurrentSlide()` looks up the slideDef for the current slide index
    // in `COURSE.slides` and dispatches to a per-type renderer registered in
    // the SLIDE_RENDERERS map. Each renderer is a pure function that takes a
    // slideDef and returns an HTML string.
    //
    // To add a new slide type: write `renderYourType(slideDef)` and register
    // it in the SLIDE_RENDERERS map at the bottom of this section.
    // ========================================================================
    function renderCurrentSlide() {
      const body = document.getElementById("slideBody");
      const catBadge = document.getElementById("slideCategoryBadge");
      const durLabel = document.getElementById("lblSlideDuration");
      body.className = "p-4 sm:p-6 md:p-8 flex-1 overflow-y-auto slide-enter";

      const unit = COURSE.units[state.currentSlide];
      const slideDef = COURSE.slides[state.currentSlide];

      catBadge.innerText = slideDef.category || unit.category || "";
      durLabel.innerText = unit.duration || "00:00";

      const renderer = SLIDE_RENDERERS[slideDef.type];
      if (!renderer) {
        body.innerHTML = `<div class="p-8 text-center text-red-500">Unknown slide type: ${slideDef.type}. Available: ${Object.keys(SLIDE_RENDERERS).join(', ')}</div>`;
        return;
      }
      body.innerHTML = renderer(slideDef);

      // Post-render hooks per type
      if (slideDef.type === 'treeCanvas') {
        setTimeout(() => { initTreeCanvasPanZoom(); initScrollbarThumbDrag(); }, 50);
      } else if (slideDef.type === 'quiz') {
        // Reset quiz state when (re)entering quiz slide
        state.quizSlideIndex = state.currentSlide;
        ensureQuizOrder();
        // Render quiz content INTO #quizContainer (which renderQuiz() created)
        // — not into body, otherwise we destroy the #quizContainer wrapper.
        const quizC = body.querySelector('#quizContainer') || body;
        renderQuizSlide(quizC);
      } else if (slideDef.type === 'scenarioPicker') {
        // No-op: scenario picker verdicts are wired via inline onclick="runScenario('scnId','optId')"
      } else if (slideDef.type === 'kpiDashboard') {
        // No-op: calcAuditScore() wires itself via onchange="calcAuditScore()"
      }
    }

    // ────────────────────────────────────────────────────────────────────────
    // SHARED UI HELPERS — UI const + uiTitle + uiTabs + switchTabGroup are
    // defined in the original engine block above (lines 1601-1642 of source).
    // We do NOT redefine them here to avoid duplicate-declaration errors.
    // ────────────────────────────────────────────────────────────────────────
    function esc(s) {
      if (s == null) return "";
      return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    }

    // ────────────────────────────────────────────────────────────────────────
    // TYPE 1: cover
    // ────────────────────────────────────────────────────────────────────────
    function renderCover(s) {
      const reasons = (s.reasons || []).map(r => `
        <div class="${UI.card} p-4 flex items-start gap-3">
          <span class="material-symbols-outlined text-brand-primary dark:text-brand-lightBlue text-xl mt-0.5 shrink-0">${r.icon || "info"}</span>
          <div>
            <p class="text-sm font-bold text-slate-900 dark:text-white">${esc(r.title)}</p>
            <p class="mt-1 ${UI.text}">${esc(r.desc)}</p>
          </div>
        </div>`).join("");
      const skipTo = (typeof s.skipTo === "number") ? s.skipTo : 1;
      return `
        <div class="max-w-3xl mx-auto space-y-6">
          <div class="p-6 sm:p-8 rounded-2xl bg-gradient-to-br from-brand-primary to-[#1F548E] text-white shadow-lg">
            ${s.heroMeta ? `<div class="mb-2"><p class="text-xs font-semibold text-sky-200 tracking-wide font-mono">${esc(s.heroMeta)}</p></div>` : ""}
            <h2 class="mt-1 text-2xl sm:text-3xl font-extrabold leading-tight">${esc(s.heroTitle)}</h2>
            ${s.heroLead ? `<p class="mt-3 text-sm text-blue-100 leading-relaxed">${esc(s.heroLead)}</p>` : ""}
          </div>
          ${reasons ? `
            <div>
              <p class="${UI.label} mb-3">${esc(s.title || "Alasan Perubahan")}</p>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">${reasons}</div>
            </div>` : ""}
          <div class="text-center pt-2">
            <button onclick="goToSlide(${skipTo})" class="btn-next-ready inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-brand-primary text-white font-bold shadow-lg btn-tactile hover:bg-brand-primaryHover">
              <span class="material-symbols-outlined">${s.ctaIcon || "play_arrow"}</span>
              <span>${esc(s.ctaLabel || "Mulai Pembelajaran")}</span>
            </button>
          </div>
        </div>`;
    }

    // ────────────────────────────────────────────────────────────────────────
    // TYPE 2: cardList
    // ────────────────────────────────────────────────────────────────────────
    function renderCardList(s) {
      const cols = s.columns || 1;
      const gridCls = cols === 1 ? "grid grid-cols-1 gap-3" :
                      cols === 2 ? "grid grid-cols-1 sm:grid-cols-2 gap-3" :
                      "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3";
      const cards = (s.cards || []).map(c => `
        <div class="${UI.card} p-4 ${cols === 1 ? 'flex items-start gap-3' : ''}">
          ${c.icon ? `<span class="material-symbols-outlined text-brand-primary dark:text-brand-lightBlue text-xl ${cols===1?'mt-0.5 shrink-0':''}">${c.icon}</span>` : ""}
          <div class="${cols===1?'flex-1':''}">
            <p class="text-sm font-bold text-slate-900 dark:text-white">${esc(c.title)}</p>
            ${c.desc ? `<p class="mt-1 ${UI.text}">${esc(c.desc)}</p>` : ""}
            ${c.body ? `<div class="mt-2 ${UI.text}">${c.body}</div>` : ""}
            ${c.tags && c.tags.length ? `<div class="mt-2 flex flex-wrap gap-1">${c.tags.map(t => `<span class="text-[10px] px-2 py-0.5 rounded-full bg-brand-primary/10 text-brand-primary dark:text-brand-lightBlue font-mono">${esc(t)}</span>`).join("")}</div>` : ""}
          </div>
        </div>`).join("");
      return `
        <div class="max-w-4xl mx-auto space-y-4">
          ${(s.title || s.lead) ? uiTitle(s.title, s.lead) : ""}
          <div class="${gridCls}">${cards}</div>
        </div>`;
    }

    // ────────────────────────────────────────────────────────────────────────
    // TYPE 3: treeCanvas — AUTHENTIC 3-column layout (Input | Aktivitas | Output)
    // Each swimlaneData entry is a "phase container" (#fase-N). Each item
    // inside becomes a row: left input box → center node button → right output
    // box, with down-arrow connectors between rows. Decision items render
    // their branches inline inside the center column.
    // Hotspot modal + role filter + pan/zoom handled by existing engine.
    // ────────────────────────────────────────────────────────────────────────
    function renderTreeCanvas(s) {
      const roleOptions = s.roleFilterOptions || ["Semua"];
      const phases = s.swimlaneData || [];
      const fc = s.flowCard || {};

      // Column header
      const colHeader = `
        <div class="grid grid-cols-12 gap-4 pb-2 border-b-2 border-brand-primary/40 text-xs font-black uppercase tracking-wider text-slate-800 dark:text-slate-200">
          <div class="col-span-3 flex items-center gap-2">
            <span class="w-6 h-6 rounded-lg bg-sky-100 text-sky-800 flex items-center justify-center font-mono">1</span>
            <span>Dokumen Input</span>
          </div>
          <div class="col-span-6 text-center flex items-center justify-center gap-2">
            <span class="w-6 h-6 rounded-lg bg-brand-primary text-white flex items-center justify-center font-mono">2</span>
            <span>Aktivitas & Bagan Alir Keputusan</span>
          </div>
          <div class="col-span-3 text-right flex items-center justify-end gap-2">
            <span>Dokumen Output</span>
            <span class="w-6 h-6 rounded-lg bg-blue-100 text-blue-800 flex items-center justify-center font-mono">3</span>
          </div>
        </div>`;

      // Phase containers
      const phaseContainers = phases.map((phase, phaseIdx) => {
        const items = phase.items || [];
        const phaseId = s.phaseJumps && s.phaseJumps[phaseIdx] 
          ? s.phaseJumps[phaseIdx].id 
          : `fase-${phaseIdx + 1}`;

        const rows = items.map((item, itemIdx) => {
          const isLast = itemIdx === items.length - 1;
          const cardData = fc[item.id] || { t: item.title };
          const isDecision = !!item.isDecision || !!(cardData.branches);
          const actorColor = item.actorColor || 'bg-brand-primary text-white';

          // Input box
          const inputBox = `
            <div class="col-span-3">
              <div class="p-3 rounded-xl bg-slate-50 dark:bg-brand-darkSubtle border border-slate-200 dark:border-brand-darkBorder text-xs text-slate-700 dark:text-slate-300">
                <span class="text-[10px] font-bold uppercase text-slate-400 block mb-0.5">Input:</span>
                <p class="font-semibold text-slate-800 dark:text-slate-200">${esc((item.inputs || []).join(' • ') || '—')}</p>
              </div>
            </div>`;

          // Center node
          const branches = cardData.branches ? `
            <div class="mt-2 space-y-1.5 pt-2 border-t border-sky-200 dark:border-sky-900/60">
              ${cardData.branches.map(b => `
                <div class="flex items-start gap-1.5 text-[11px] leading-snug p-1.5 rounded-lg bg-white/80 dark:bg-brand-darkSurface/80 border border-sky-200/60 dark:border-sky-900/40">
                  <span class="inline-block px-1.5 py-0.5 rounded font-mono font-bold text-[10px] ${(b[0].match(/[T<>]/) || b[0].toLowerCase().includes('tidak')) ? 'bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300' : 'bg-blue-100 dark:bg-blue-950/60 text-blue-800 dark:text-blue-300'} shrink-0">${esc(b[0])}</span>
                  <span class="text-slate-700 dark:text-slate-300 font-medium">${esc(b[1])}</span>
                </div>`).join("")}
            </div>` : '';

          const centerNode = `
            <div class="col-span-6 flex flex-col items-center">
              <button onclick="openSwimlaneHotspot('${esc(item.id)}')"
                data-actor="${esc(item.actor || '')}"
                data-actor-role="${esc(item.actorRole || '')}"
                class="flow-card-node group w-80 text-center p-3 rounded-2xl border-2 ${isDecision ? 'border-sky-400 bg-sky-50/80 dark:bg-sky-950/40' : 'border-brand-primary bg-blue-50/80 dark:bg-brand-primary/15'} hover:shadow-lg transition-all btn-tactile cursor-pointer">
                <div class="flex items-center justify-between gap-1 mb-1">
                  <span class="px-2 py-0.5 rounded ${actorColor} font-mono font-bold text-[10px]">${esc(item.actor || '—')}</span>
                  <span class="text-[10px] font-mono text-slate-500">${esc(item.step)}</span>
                </div>
                <h4 class="text-xs sm:text-sm font-black text-slate-900 dark:text-white leading-tight">${esc(cardData.t || item.title)}</h4>
                ${item.actorRole ? `<p class="text-[11px] text-slate-600 dark:text-slate-300 mt-0.5">${esc(item.actorRole)}</p>` : ''}
                ${branches}
              </button>
            </div>`;

          // Output box
          const outputBox = cardData.branches ? `
            <div class="col-span-3">
              <div class="p-3 rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 text-xs text-slate-700 dark:text-slate-300">
                <span class="text-[10px] font-bold uppercase text-amber-600 block mb-0.5">Cabang Keputusan:</span>
                <p class="font-semibold text-amber-800 dark:text-amber-300">${esc(cardData.branches.length)} cabang</p>
                <p class="text-[10px] text-amber-600 dark:text-amber-400 mt-1">Lihat detail di kartu proses</p>
              </div>
            </div>` : `
            <div class="col-span-3">
              <div class="p-3 rounded-xl bg-blue-50 dark:bg-brand-primary/10 border border-blue-200 dark:border-brand-primary/30 text-xs text-slate-700 dark:text-slate-300">
                <span class="text-[10px] font-bold uppercase text-brand-primary block mb-0.5">Output Wajib:</span>
                <p class="font-bold text-brand-primary dark:text-brand-lightBlue">${esc(cardData.out || (item.outputs || []).join(' • ') || '—')}</p>
              </div>
            </div>`;

          const row = `
            <div class="grid grid-cols-12 gap-4 items-center">
              ${inputBox}
              ${centerNode}
              ${outputBox}
            </div>`;

          // Down-arrow connector between rows
          const connector = isLast ? '' : `
            <div class="flex justify-center -my-2 text-brand-primary">
              <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="12" y1="2" x2="12" y2="22"></line>
                <polyline points="18 16 12 22 6 16"></polyline>
              </svg>
            </div>`;

          return row + connector;
        }).join('');

        // Phase klausul range
        const firstStep = (items[0] && items[0].step) || '';
        const lastStep = (items[items.length-1] && items[items.length-1].step) || '';
        const klausul = (firstStep && lastStep && firstStep !== lastStep)
          ? `Klausul ${firstStep} – ${lastStep}`
          : (firstStep ? `Klausul ${firstStep}` : '');

        return `
          <div id="${phaseId}" class="rounded-3xl p-6 bg-white/70 dark:bg-brand-darkSurface/70 border border-slate-200 dark:border-brand-darkBorder shadow-sm space-y-6">
            <div class="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-brand-darkBorder">
              <span class="px-3 py-1 rounded-xl bg-brand-primary text-white text-xs font-bold font-mono tracking-wider">${esc(phase.section || 'FASE ' + (phaseIdx+1))}</span>
              ${klausul ? `<span class="text-xs text-slate-500 font-semibold font-mono">${klausul}</span>` : ''}
            </div>
            ${rows}
          </div>`;
      }).join('');

      // Phase jump buttons
      const jumps = s.phaseJumps || phases.map((p, i) => ({ id: `fase-${i+1}`, label: p.section || `Fase ${i+1}` }));

      return `
        <div class="max-w-6xl mx-auto space-y-3">
          <div class="flex items-center justify-between gap-2 flex-wrap">
            <div>
              <p class="${UI.label}">Alur Proses</p>
              <p class="text-sm font-bold text-slate-900 dark:text-white">${esc(s.title || "Tree Diagram")}</p>
            </div>
            <div class="flex items-center gap-2">
              <select id="swimlaneRoleFilter" onchange="filterSwimlaneRole(this.value)" class="text-xs rounded-lg border border-slate-300 dark:border-brand-darkBorder bg-white dark:bg-brand-darkSurface px-2 py-1">
                ${roleOptions.map(r => `<option value="${esc(r)}">${esc(r)}</option>`).join("")}
              </select>
            </div>
          </div>
          <div class="relative w-full h-[640px] sm:h-[700px] rounded-2xl border-2 border-slate-200 dark:border-brand-darkBorder bg-[#F8FAFC] dark:bg-[#070D18] overflow-hidden shadow-inner select-none cursor-grab active:cursor-grabbing" id="treeCanvasViewport">
            <div class="absolute top-2 left-2 right-2 flex items-center justify-between gap-2 z-10 pointer-events-none">
              <div class="flex gap-1 pointer-events-auto flex-wrap">
                ${jumps.map((p, i) => `<button id="btnJumpFase${i+1}" onclick="jumpToPhase('${esc(p.id)}')" class="text-[10px] font-bold px-2 py-1 rounded-md bg-white/90 dark:bg-brand-darkSurface/90 border border-slate-200 dark:border-brand-darkBorder text-slate-600 dark:text-slate-300 hover:bg-brand-primary hover:text-white">${esc(p.label)}</button>`).join("")}
              </div>
              <span id="treeCurrentPhaseText" class="text-[10px] font-mono text-slate-500 dark:text-slate-400 bg-white/80 dark:bg-brand-darkSurface/80 px-2 py-1 rounded">—</span>
            </div>
            <div class="absolute bottom-2 right-2 flex flex-col gap-1 z-10">
              <button onclick="zoomInCanvas()" class="w-8 h-8 rounded-lg bg-white dark:bg-brand-darkSurface border border-slate-200 dark:border-brand-darkBorder flex items-center justify-center text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-brand-darkSubtle" title="Zoom In"><span class="material-symbols-outlined text-base">add</span></button>
              <button onclick="zoomOutCanvas()" class="w-8 h-8 rounded-lg bg-white dark:bg-brand-darkSurface border border-slate-200 dark:border-brand-darkBorder flex items-center justify-center text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-brand-darkSubtle" title="Zoom Out"><span class="material-symbols-outlined text-base">remove</span></button>
              <button onclick="resetCanvasZoom()" class="w-8 h-8 rounded-lg bg-white dark:bg-brand-darkSurface border border-slate-200 dark:border-brand-darkBorder flex items-center justify-center text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-brand-darkSubtle" title="Reset"><span class="material-symbols-outlined text-base">center_focus_strong</span></button>
            </div>
            <div id="treeCanvasInner" class="absolute origin-top-left p-8 transition-transform duration-75" style="transform: translate(0px, 0px) scale(1);">
              <div class="w-[1100px] space-y-10">
                ${colHeader}
                ${phaseContainers}
              </div>
            </div>
            <div id="treeScrollTrack" class="absolute right-1 top-12 bottom-12 w-1 bg-slate-200/50 dark:bg-brand-darkBorder/50 rounded-full hidden md:block">
              <div id="treeScrollThumb" class="absolute left-0 right-0 top-0 h-12 bg-brand-primary/60 dark:bg-brand-lightBlue/60 rounded-full cursor-pointer"></div>
            </div>
          </div>
          <div class="flex items-center justify-between gap-2 text-[10px] text-slate-500 dark:text-slate-400">
            <button onclick="scrollTreeStep('up')" class="px-2 py-1 rounded hover:bg-slate-100 dark:hover:bg-brand-darkSubtle"><span class="material-symbols-outlined text-sm">arrow_upward</span></button>
            <span id="treeZoomLabel">100%</span>
            <button onclick="scrollTreeStep('down')" class="px-2 py-1 rounded hover:bg-slate-100 dark:hover:bg-brand-darkSubtle"><span class="material-symbols-outlined text-sm">arrow_downward</span></button>
          </div>
        </div>`;
    }

    // ────────────────────────────────────────────────────────────────────────
    // TYPE 4: scenarioPicker — generic dispatcher
    // ────────────────────────────────────────────────────────────────────────
    function renderScenarioPicker(s) {
      const cards = (s.cards || []).map(c => `
        <div class="${UI.card} p-4 flex items-start gap-3">
          ${c.icon ? `<span class="material-symbols-outlined text-brand-primary dark:text-brand-lightBlue text-xl mt-0.5 shrink-0">${c.icon}</span>` : ""}
          <div>
            <p class="text-sm font-bold text-slate-900 dark:text-white">${esc(c.title)}</p>
            ${c.desc ? `<p class="mt-1 ${UI.text}">${esc(c.desc)}</p>` : ""}
          </div>
        </div>`).join("");
      const scenarios = (s.scenarios || []).map(sc => `
        <div class="${UI.card} p-4 space-y-3">
          <div>
            <p class="${UI.label}">${esc(sc.label || sc.id)}</p>
            ${sc.title ? `<p class="mt-1 text-sm font-bold text-slate-900 dark:text-white">${esc(sc.title)}</p>` : ""}
          </div>
          <div class="flex flex-wrap gap-2">
            ${sc.options.map(o => `<button onclick="runScenario('${esc(sc.id)}','${esc(o.id)}')" class="px-3 py-1.5 rounded-lg text-xs font-semibold border border-slate-200 dark:border-brand-darkBorder bg-white dark:bg-brand-darkSurface text-slate-700 dark:text-slate-300 hover:border-brand-primary dark:hover:border-brand-lightBlue btn-tactile">${esc(o.label)}</button>`).join("")}
          </div>
          <div id="scenarioResult_${esc(sc.id)}" class="hidden mt-2 p-3 rounded-lg border text-xs leading-relaxed"></div>
        </div>`).join("");
      return `
        <div class="max-w-4xl mx-auto space-y-4">
          ${(s.title || s.lead) ? uiTitle(s.title, s.lead) : ""}
          ${s.infoBanner ? `<div class="p-3 rounded-xl bg-blue-50 dark:bg-brand-primary/10 border border-brand-primary/30 text-xs sm:text-sm text-brand-primary dark:text-brand-lightBlue">${s.infoBanner}</div>` : ""}
          ${cards ? `<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">${cards}</div>` : ""}
          ${scenarios}
        </div>`;
    }

    function runScenario(scenarioId, optionId) {
      playTone('click');
      const slideDef = COURSE.slides[state.currentSlide];
      const sc = (slideDef.scenarios || []).find(x => x.id === scenarioId);
      if (!sc) return;
      const opt = (sc.options || []).find(x => x.id === optionId);
      if (!opt) return;
      const panel = document.getElementById(`scenarioResult_${scenarioId}`);
      if (!panel) return;
      panel.classList.remove('hidden');
      const toneCls = {
        positive: 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-900 text-emerald-800 dark:text-emerald-300',
        negative: 'bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-900 text-rose-800 dark:text-rose-300',
        neutral: 'bg-slate-50 dark:bg-brand-darkSubtle border-slate-200 dark:border-brand-darkBorder text-slate-700 dark:text-slate-300'
      }[opt.tone || 'neutral'];
      panel.className = `mt-2 p-3 rounded-lg border text-xs leading-relaxed ${toneCls}`;
      panel.innerHTML = opt.verdict;
    }

    // ────────────────────────────────────────────────────────────────────────
    // TYPE 5: tabbedAccordion
    // ────────────────────────────────────────────────────────────────────────
    function renderTabbedAccordion(s) {
      const tabs = s.tabs || [];
      if (!tabs.length) return `<div class="p-8 text-center text-slate-500">No tabs defined.</div>`;
      const tabHeaders = uiTabs(s.tabs[0].key + '_group', tabs); // group id derived from first tab key
      // Actually use a stable group id
      const groupId = 'tba_' + state.currentSlide;
      const tabHeadersHtml = `
        <div class="inline-flex flex-wrap gap-1 p-1 rounded-xl bg-slate-100 dark:bg-brand-darkBg mb-4" role="tablist">
          ${tabs.map((it, i) => `<button role="tab" id="tab-${groupId}-${it.key}" aria-controls="panel-${groupId}-${it.key}" aria-selected="${i === 0 ? 'true' : 'false'}" tabindex="${i === 0 ? '0' : '-1'}" data-tab-group="${groupId}" data-tab="${it.key}" onclick="switchTabGroup('${groupId}','${it.key}')" class="${i === 0 ? UI.tabOn : UI.tabOff}">${esc(it.label)}</button>`).join("")}
        </div>`;
      const panels = tabs.map((tb, i) => {
        const items = (tb.items || []).map(it => {
          if (typeof it === 'string') {
            return `<li class="flex items-start gap-2 ${UI.text}"><span class="text-brand-primary dark:text-brand-lightBlue mt-0.5">•</span><span>${esc(it)}</span></li>`;
          }
          return `<li class="p-3 rounded-lg border border-slate-100 dark:border-brand-darkBorder/60"><p class="text-sm font-bold text-slate-900 dark:text-white">${esc(it.t)}</p>${it.d ? `<p class="mt-1 ${UI.text}">${esc(it.d)}</p>` : ""}</li>`;
        }).join("");
        return `<ol data-panel-group="${groupId}" data-panel="${tb.key}" class="${i === 0 ? '' : 'hidden'} space-y-2 list-none" role="tabpanel">${items}</ol>`;
      }).join("");
      const check = (s.checklist && s.checklist.length) ? `
        ${s.checklist.map(ch => `<details class="mt-4"><summary class="cursor-pointer text-xs font-bold text-brand-primary dark:text-brand-lightBlue">${esc(ch.label)}</summary><ul class="mt-2 space-y-1 list-disc list-inside ${UI.text}">${(ch.items || []).map(it => `<li>${esc(it)}</li>`).join("")}</ul></details>`).join("")}
      ` : "";
      return `
        <div class="max-w-4xl mx-auto space-y-4">
          ${(s.title || s.lead) ? uiTitle(s.title, s.lead) : ""}
          ${tabHeadersHtml}
          ${panels}
          ${check}
        </div>`;
    }

    // ────────────────────────────────────────────────────────────────────────
    // TYPE 6: verificationMatrix
    // ────────────────────────────────────────────────────────────────────────
    function renderVerificationMatrix(s) {
      const tabs = s.tabs || [];
      if (!tabs.length) return `<div class="p-8 text-center text-slate-500">No verification tabs defined.</div>`;
      const groupId = 'verif_' + state.currentSlide;
      const tabHeadersHtml = `
        <div class="inline-flex flex-wrap gap-1 p-1 rounded-xl bg-slate-100 dark:bg-brand-darkBg mb-4" role="tablist">
          ${tabs.map((it, i) => `<button role="tab" data-tab-group="${groupId}" data-tab="${it.key}" onclick="switchTabGroup('${groupId}','${it.key}')" class="${i === 0 ? UI.tabOn : UI.tabOff}">${esc(it.label)}</button>`).join("")}
        </div>`;
      const panels = tabs.map((tb, i) => {
        const defaultPic = tb.defaultPic || "—";
        const rows = (tb.items || []).map(r => {
          const pic = r.pic || defaultPic;
          if (r.noInfo) {
            return `<li class="flex items-center justify-between gap-3 py-2 border-b border-slate-100 dark:border-brand-darkBorder/60 last:border-0">
              <span class="text-sm text-slate-700 dark:text-slate-200">${esc(r.doc)}</span>
              <span class="text-[10px] font-mono px-2 py-1 rounded bg-slate-100 dark:bg-brand-darkSubtle text-slate-500 dark:text-slate-400">${esc(pic)}</span>
            </li>`;
          }
          return `<li class="py-2 border-b border-slate-100 dark:border-brand-darkBorder/60 last:border-0">
            <div class="flex items-center justify-between gap-3">
              <span class="text-sm font-semibold text-slate-900 dark:text-white">${esc(r.doc)}</span>
              <span class="text-[10px] font-mono px-2 py-1 rounded bg-brand-primary/10 text-brand-primary dark:text-brand-lightBlue">${esc(pic)}</span>
            </div>
            ${r.note ? `<p class="mt-1 text-xs text-slate-500 dark:text-slate-400">${esc(r.note)}</p>` : ""}
          </li>`;
        }).join("");
        return `<ul data-panel-group="${groupId}" data-panel="${tb.key}" class="${i === 0 ? '' : 'hidden'} divide-y divide-slate-100 dark:divide-brand-darkBorder" role="tabpanel">${rows}</ul>`;
      }).join("");
      return `
        <div class="max-w-4xl mx-auto space-y-4">
          ${(s.title || s.lead) ? uiTitle(s.title, s.lead) : ""}
          ${tabHeadersHtml}
          ${panels}
        </div>`;
    }

    // ────────────────────────────────────────────────────────────────────────
    // TYPE 7: twoCardAccordion
    // ────────────────────────────────────────────────────────────────────────
    function renderTwoCardAccordion(s) {
      const cards = (s.cards || []).slice(0, 2).map(c => {
        const items = (c.items || []).map(it => `<li class="flex items-start justify-between gap-3 py-1.5 border-b border-slate-100 dark:border-brand-darkBorder/60 last:border-0"><span class="text-xs text-slate-600 dark:text-slate-300">${esc(it.label)}</span><span class="text-xs font-bold text-brand-primary dark:text-brand-lightBlue text-right">${esc(it.value || "")}</span></li>`).join("");
        return `<div class="${UI.card} p-5 flex-1">
          ${c.icon ? `<span class="material-symbols-outlined text-brand-primary dark:text-brand-lightBlue text-xl mb-2">${c.icon}</span>` : ""}
          <p class="text-base font-bold text-slate-900 dark:text-white">${esc(c.title)}</p>
          ${c.desc ? `<p class="mt-1 text-xs text-slate-500 dark:text-slate-400">${esc(c.desc)}</p>` : ""}
          ${items ? `<ul class="mt-3">${items}</ul>` : ""}
        </div>`;
      }).join("");
      const check = (s.miniCheck && s.miniCheck.length) ? s.miniCheck.map(ch => `<details class="mt-4"><summary class="cursor-pointer text-xs font-bold text-brand-primary dark:text-brand-lightBlue">${esc(ch.label)}</summary><ul class="mt-2 space-y-1 list-disc list-inside ${UI.text}">${(ch.items || []).map(it => `<li>${esc(it)}</li>`).join("")}</ul></details>`).join("") : "";
      return `
        <div class="max-w-3xl mx-auto space-y-4">
          ${(s.title || s.lead) ? uiTitle(s.title, s.lead) : ""}
          ${s.infoBanner ? `<div class="p-3 rounded-xl bg-blue-50 dark:bg-brand-primary/10 border border-brand-primary/30 text-xs sm:text-sm text-brand-primary dark:text-brand-lightBlue flex items-start gap-2"><span class="material-symbols-outlined text-base shrink-0">${s.infoBannerIcon || "info"}</span><span>${s.infoBanner}</span></div>` : ""}
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">${cards}</div>
          ${check}
        </div>`;
    }

    // ────────────────────────────────────────────────────────────────────────
    // TYPE 8: docTabs
    // ────────────────────────────────────────────────────────────────────────
    function renderDocTabs(s) {
      const tabs = s.tabs || [];
      if (!tabs.length) return `<div class="p-8 text-center text-slate-500">No doc tabs defined.</div>`;
      const groupId = 'docs_' + state.currentSlide;
      const tabHeadersHtml = `
        <div class="inline-flex flex-wrap gap-1 p-1 rounded-xl bg-slate-100 dark:bg-brand-darkBg mb-4" role="tablist">
          ${tabs.map((it, i) => `<button role="tab" data-tab-group="${groupId}" data-tab="${it.key}" onclick="switchTabGroup('${groupId}','${it.key}')" class="${i === 0 ? UI.tabOn : UI.tabOff}">${esc(it.label)}</button>`).join("")}
        </div>`;
      const panels = tabs.map((tb, i) => {
        const itType = tb.itemType || 'list';
        const items = (tb.items || []).map((it, idx) => {
          if (typeof it === 'string') {
            if (itType === 'attachments') {
              return `<li class="${UI.card} p-3 flex items-center gap-3"><span class="w-16 shrink-0 text-xs font-mono font-bold text-brand-primary dark:text-brand-lightBlue">Lamp. ${idx+1}</span><span class="text-xs sm:text-sm text-slate-700 dark:text-slate-200 leading-snug">${esc(it)}</span></li>`;
            }
            if (itType === 'records') {
              return `<li class="${UI.card} p-3 flex items-center gap-3"><span class="w-8 shrink-0 text-xs font-mono font-bold text-brand-primary dark:text-brand-lightBlue">${(idx+1).toString().padStart(2,'0')}</span><span class="text-xs sm:text-sm text-slate-700 dark:text-slate-200 leading-snug">${esc(it)}</span></li>`;
            }
            return `<li class="${UI.card} p-3 flex items-center gap-3"><span class="material-symbols-outlined text-brand-primary dark:text-brand-lightBlue text-sm">description</span><span class="text-xs sm:text-sm text-slate-700 dark:text-slate-200 leading-snug">${esc(it)}</span></li>`;
          }
          return `<li class="${UI.card} p-3"><div class="flex items-center gap-3"><span class="material-symbols-outlined text-brand-primary dark:text-brand-lightBlue text-sm">description</span><span class="text-xs sm:text-sm text-slate-700 dark:text-slate-200 leading-snug">${esc(it.doc)}</span></div>${it.note ? `<p class="mt-1 ml-8 text-[10px] text-slate-500 dark:text-slate-400">${esc(it.note)}</p>` : ""}</li>`;
        }).join("");
        return `<ol data-panel-group="${groupId}" data-panel="${tb.key}" class="${i === 0 ? '' : 'hidden'} grid grid-cols-1 sm:grid-cols-2 gap-2.5" role="tabpanel">${items}</ol>`;
      }).join("");
      return `
        <div class="max-w-4xl mx-auto space-y-4">
          ${(s.title || s.lead) ? uiTitle(s.title, s.lead) : ""}
          ${tabHeadersHtml}
          ${panels}
        </div>`;
    }

    // ────────────────────────────────────────────────────────────────────────
    // TYPE 9: kpiDashboard
    // ────────────────────────────────────────────────────────────────────────
    function renderKpiDashboard(s) {
      const kpis = (s.kpis || []).map(k => `
        <div class="${UI.card} p-5">
          <div class="flex items-start justify-between gap-2">
            <p class="${UI.label}">${esc(k.label)}</p>
            ${k.icon ? `<span class="material-symbols-outlined text-brand-primary dark:text-brand-lightBlue">${k.icon}</span>` : ""}
          </div>
          <p class="mt-3 text-2xl font-extrabold text-slate-900 dark:text-white">${esc(k.value)}</p>
          ${k.target ? `<p class="mt-1 text-xs text-slate-500 dark:text-slate-400">Target: ${esc(k.target)}</p>` : ""}
          ${k.desc ? `<p class="mt-2 ${UI.text}">${esc(k.desc)}</p>` : ""}
        </div>`).join("");
      const checklist = (s.auditChecklist && s.auditChecklist.length) ? `
        <div class="${UI.card} p-5">
          <div class="flex items-center justify-between gap-2 mb-3">
            <p class="${UI.label}">Audit Checklist</p>
            <div class="text-right">
              <span id="auditGaugeScore" class="text-2xl font-extrabold text-brand-primary dark:text-brand-lightBlue">0</span>
              <span class="text-xs text-slate-500 dark:text-slate-400"> / ${s.auditChecklist.length}</span>
            </div>
          </div>
          <div class="w-full h-2 rounded-full bg-slate-200 dark:bg-brand-darkBorder overflow-hidden mb-3">
            <div id="auditGaugeBar" class="h-full bg-brand-primary dark:bg-brand-lightBlue transition-all" style="width: 0%"></div>
          </div>
          <ul class="space-y-2">
            ${s.auditChecklist.map(it => `<li class="flex items-center gap-2"><input type="checkbox" id="audit_${esc(it.id)}" class="audit-item w-4 h-4 rounded border-slate-300 dark:border-brand-darkBorder text-brand-primary focus:ring-brand-primary" onchange="calcAuditScore()"><label for="audit_${esc(it.id)}" class="text-xs sm:text-sm text-slate-700 dark:text-slate-300 cursor-pointer">${esc(it.label)}</label></li>`).join("")}
          </ul>
        </div>` : "";
      return `
        <div class="max-w-4xl mx-auto space-y-4">
          ${(s.title || s.lead) ? uiTitle(s.title, s.lead) : ""}
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">${kpis}</div>
          ${checklist}
        </div>`;
    }

    // ────────────────────────────────────────────────────────────────────────
    // TYPE 10: riskCards
    // ────────────────────────────────────────────────────────────────────────
    function renderRiskCards(s) {
      const risks = (s.risks || []).map(r => `
        <div class="${UI.card} p-5">
          <div class="flex items-center gap-2 mb-2">
            <span class="text-[10px] font-mono font-bold px-2 py-1 rounded bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300">${esc(r.no)}</span>
            <p class="text-sm font-bold text-slate-900 dark:text-white">Proses</p>
          </div>
          <p class="text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed">${esc(r.proc)}</p>
          <div class="mt-3 pt-3 border-t border-slate-100 dark:border-brand-darkBorder/60 grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div><p class="${UI.label}">Risiko</p><p class="mt-1 text-xs text-rose-700 dark:text-rose-300 leading-relaxed">${esc(r.risk)}</p></div>
            <div><p class="${UI.label}">Mitigasi</p><p class="mt-1 text-xs text-emerald-700 dark:text-emerald-300 leading-relaxed">${esc(r.mit)}</p></div>
          </div>
        </div>`).join("");
      return `
        <div class="max-w-4xl mx-auto space-y-3">
          ${(s.title || s.lead) ? uiTitle(s.title, s.lead) : ""}
          ${risks}
        </div>`;
    }

    // ────────────────────────────────────────────────────────────────────────
    // TYPE 11: quiz — body shell rendered here. Question rendering delegated
    // to the extended quiz engine (renderQuizSlide below).
    // ────────────────────────────────────────────────────────────────────────
    function renderQuiz(s) {
      return `
        <div class="max-w-3xl mx-auto space-y-4" id="quizContainer">
          <header class="text-center">
            <p class="${UI.label}">${esc(s.category || "Uji Pemahaman")}</p>
            <h2 class="text-2xl font-extrabold text-slate-900 dark:text-white mt-1">${esc(s.title || "Uji Pemahaman")}</h2>
            ${s.lead ? `<p class="mt-2 text-xs sm:text-sm text-slate-600 dark:text-slate-400">${esc(s.lead)}</p>` : ""}
          </header>
          <!-- Quiz content rendered by renderQuizSlide(body) into #quizContainer -->
        </div>`;
    }

    // ────────────────────────────────────────────────────────────────────────
    // TYPE 12: summaryCertificate
    // ────────────────────────────────────────────────────────────────────────
    function renderSummaryCertificate(s) {
      const passed = state.quizCompleted && state.quizScore >= (COURSE.course.passingScore || 80);
      const takeaways = (s.takeaways || []).map(r => `
        <div class="${UI.card} p-4 flex items-start gap-3">
          <span class="material-symbols-outlined text-brand-primary dark:text-brand-lightBlue text-xl mt-0.5 shrink-0">${r.icon || "check_circle"}</span>
          <div>
            <p class="text-sm font-bold text-slate-900 dark:text-white">${esc(r.title)}</p>
            ${r.desc ? `<p class="mt-1 ${UI.text}">${esc(r.desc)}</p>` : ""}
          </div>
        </div>`).join("");
      return `
        <div class="max-w-3xl mx-auto space-y-6">
          <div class="p-6 sm:p-8 rounded-2xl bg-gradient-to-br from-brand-primary to-[#1F548E] text-white shadow-lg text-center">
            <p class="text-xs font-semibold text-sky-200 tracking-wide font-mono">${esc(s.heroTitle || "Penyelesaian Modul")}</p>
            <p class="mt-3 text-5xl font-extrabold">${state.quizScore}<span class="text-2xl">/100</span></p>
            <p class="mt-2 text-sm text-blue-100">${passed ? "Selamat! Anda lulus uji pemahaman." : (s.failMessage || "Anda belum lulus. Silakan ulangi kuis.")}</p>
          </div>
          ${takeaways ? `<div><p class="${UI.label} mb-3">Key Takeaways</p><div class="grid grid-cols-1 sm:grid-cols-2 gap-3">${takeaways}</div></div>` : ""}
          ${passed ? `
            <div class="${UI.card} p-5 space-y-4">
              <p class="${UI.label} text-center">Sertifikat Penyelesaian</p>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <label class="text-xs text-slate-600 dark:text-slate-400">Nama Lengkap
                  <input id="certInputName" type="text" value="${esc(state.participantName)}" oninput="state.participantName=this.value" class="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-brand-darkBorder bg-white dark:bg-brand-darkSurface text-slate-900 dark:text-white text-sm">
                </label>
                <label class="text-xs text-slate-600 dark:text-slate-400">NIP / ID
                  <input id="certInputNip" type="text" value="${esc(state.participantNIP)}" oninput="state.participantNIP=this.value" class="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-brand-darkBorder bg-white dark:bg-brand-darkSurface text-slate-900 dark:text-white text-sm">
                </label>
              </div>
              <button onclick="printCertificate()" class="w-full px-4 py-3 rounded-xl bg-brand-primary text-white font-bold shadow-lg btn-tactile hover:bg-brand-primaryHover flex items-center justify-center gap-2">
                <span class="material-symbols-outlined">verified</span>
                <span>Cetak Sertifikat</span>
              </button>
            </div>` : ""}
        </div>`;
    }

    // ────────────────────────────────────────────────────────────────────────
    // TYPE 13: imageGallery (NEW)
    // ────────────────────────────────────────────────────────────────────────
    function renderImageGallery(s) {
      const cols = s.columns || 3;
      const gridCls = cols === 2 ? "grid grid-cols-1 sm:grid-cols-2 gap-4" :
                      cols === 4 ? "grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4" :
                      "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4";
      if (s.layout === 'carousel') {
        return `
          <div class="max-w-4xl mx-auto space-y-4">
            ${(s.title || s.lead) ? uiTitle(s.title, s.lead) : ""}
            <div class="relative ${UI.card} overflow-hidden">
              <div id="galleryCarousel" class="flex overflow-x-auto snap-x snap-mandatory scroll-smooth">
                ${(s.images || []).map((img, i) => `
                  <figure class="snap-center shrink-0 w-full sm:w-3/4 p-3">
                    <img src="${esc(img.src)}" alt="${esc(img.alt)}" class="w-full h-auto rounded-xl" loading="lazy">
                    ${img.caption ? `<figcaption class="mt-2 text-xs text-center text-slate-500 dark:text-slate-400">${esc(img.caption)}</figcaption>` : ""}
                  </figure>`).join("")}
              </div>
              <div class="flex justify-center gap-2 mt-2">
                ${(s.images || []).map((_, i) => `<button onclick="document.querySelectorAll('#galleryCarousel figure')[${i}].scrollIntoView({behavior:'smooth',inline:'center',block:'nearest'})" class="w-2 h-2 rounded-full bg-slate-300 dark:bg-brand-darkBorder hover:bg-brand-primary"></button>`).join("")}
              </div>
            </div>
          </div>`;
      }
      return `
        <div class="max-w-4xl mx-auto space-y-4">
          ${(s.title || s.lead) ? uiTitle(s.title, s.lead) : ""}
          <div class="${gridCls}">
            ${(s.images || []).map(img => `
              <figure class="${UI.card} overflow-hidden">
                <img src="${esc(img.src)}" alt="${esc(img.alt)}" class="w-full h-auto" loading="lazy">
                ${img.caption ? `<figcaption class="p-3 text-xs text-slate-500 dark:text-slate-400">${esc(img.caption)}</figcaption>` : ""}
              </figure>`).join("")}
          </div>
        </div>`;
    }

    // ────────────────────────────────────────────────────────────────────────
    // TYPE 14: videoEmbed (NEW)
    // ────────────────────────────────────────────────────────────────────────
    function renderVideoEmbed(s) {
      const aspectMap = { "16:9": "aspect-video", "4:3": "aspect-[4/3]", "1:1": "aspect-square", "9:16": "aspect-[9/16]" };
      const aspectCls = aspectMap[s.aspectRatio || "16:9"] || "aspect-video";
      let embed = "";
      const src = s.src || "";
      if (s.provider === "youtube") {
        // Extract YouTube video id
        const m = src.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/|v\/))([\w-]{11})/);
        const ytId = m ? m[1] : "";
        embed = `<iframe src="https://www.youtube.com/embed/${ytId}" title="${esc(s.title)}" class="w-full h-full" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>`;
      } else if (s.provider === "vimeo") {
        const m = src.match(/vimeo\.com\/(\d+)/);
        const vimeoId = m ? m[1] : "";
        embed = `<iframe src="https://player.vimeo.com/video/${vimeoId}" title="${esc(s.title)}" class="w-full h-full" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>`;
      } else {
        // Direct file
        embed = `<video controls ${s.poster ? `poster="${esc(s.poster)}"` : ""} class="w-full h-full"><source src="${esc(src)}">Your browser does not support the video tag.</video>`;
      }
      return `
        <div class="max-w-4xl mx-auto space-y-4">
          ${(s.title || s.lead) ? uiTitle(s.title, s.lead) : ""}
          <div class="${UI.card} overflow-hidden">
            <div class="${aspectCls} bg-black">${embed}</div>
            ${s.durationLabel ? `<div class="p-3 text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2"><span class="material-symbols-outlined text-sm">schedule</span><span>${esc(s.durationLabel)}</span></div>` : ""}
          </div>
        </div>`;
    }

    // ────────────────────────────────────────────────────────────────────────
    // TYPE 15: calloutBox (NEW)
    // ────────────────────────────────────────────────────────────────────────
    function renderCalloutBox(s) {
      const variantCfg = {
        info:     { icon: "info",      cls: "bg-blue-50 dark:bg-brand-primary/10 border-brand-primary/30 text-brand-primary dark:text-brand-lightBlue" },
        warning:  { icon: "warning",   cls: "bg-amber-50 dark:bg-amber-950/40 border-amber-300 dark:border-amber-800 text-amber-800 dark:text-amber-300" },
        success:  { icon: "check_circle", cls: "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-300 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300" },
        danger:   { icon: "dangerous", cls: "bg-rose-50 dark:bg-rose-950/40 border-rose-300 dark:border-rose-800 text-rose-800 dark:text-rose-300" }
      };
      const cfg = variantCfg[s.variant || "info"] || variantCfg.info;
      const icon = s.icon || cfg.icon;
      return `
        <div class="max-w-3xl mx-auto space-y-4">
          ${(s.title && s.title !== cfg.icon) ? uiTitle(s.title, s.lead) : (s.lead ? `<p class="text-xs text-slate-500 dark:text-slate-400 mb-3">${esc(s.lead)}</p>` : "")}
          <div class="p-4 sm:p-5 rounded-xl border-2 ${cfg.cls} flex items-start gap-3">
            <span class="material-symbols-outlined text-2xl shrink-0">${icon}</span>
            <div class="flex-1">
              <p class="text-sm font-bold">${esc(s.title || "")}</p>
              <div class="mt-1 text-xs sm:text-sm leading-relaxed">${s.body || ""}</div>
            </div>
          </div>
        </div>`;
    }

    // ────────────────────────────────────────────────────────────────────────
    // TYPE 16: stepByStep (NEW)
    // ────────────────────────────────────────────────────────────────────────
    function renderStepByStep(s) {
      const steps = (s.steps || []).map((st, i) => {
        const num = st.number || (i + 1).toString();
        return `
          <li class="flex items-start gap-3">
            <div class="shrink-0 w-10 h-10 rounded-full bg-brand-primary text-white flex items-center justify-center font-bold text-sm">${esc(num)}</div>
            <div class="flex-1 pt-1">
              <p class="text-sm font-bold text-slate-900 dark:text-white">${esc(st.title)}</p>
              ${st.desc ? `<p class="mt-1 ${UI.text}">${esc(st.desc)}</p>` : ""}
            </div>
          </li>`;
      }).join("");
      const connector = s.connector || "line";
      const ulCls = connector === "none" ? "space-y-3" : "space-y-4 relative";
      const lineCls = connector === "line" ? `<div class="absolute left-5 top-10 bottom-10 w-px bg-slate-200 dark:bg-brand-darkBorder"></div>` :
                      connector === "arrow" ? `<div class="absolute left-5 top-10 bottom-10 w-px bg-gradient-to-b from-transparent via-brand-primary/30 to-transparent"></div>` : "";
      return `
        <div class="max-w-2xl mx-auto space-y-4">
          ${(s.title || s.lead) ? uiTitle(s.title, s.lead) : ""}
          <ul class="${ulCls}">${lineCls}${steps}</ul>
        </div>`;
    }

    // ────────────────────────────────────────────────────────────────────────
    // TYPE 17: comparisonTable (NEW)
    // ────────────────────────────────────────────────────────────────────────
    function renderComparisonTable(s) {
      const cols = s.columns || [];
      if (!cols.length) return `<div class="p-8 text-center text-slate-500">No columns defined.</div>`;
      const highlight = s.highlightColumn;
      return `
        <div class="max-w-4xl mx-auto space-y-4">
          ${(s.title || s.lead) ? uiTitle(s.title, s.lead) : ""}
          <div class="${UI.card} overflow-hidden">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-slate-200 dark:border-brand-darkBorder">
                  <th class="p-3 text-left text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400"></th>
                  ${cols.map(c => `<th class="p-3 text-left ${highlight === c.key ? 'bg-brand-primary/10 dark:bg-brand-lightBlue/10 text-brand-primary dark:text-brand-lightBlue' : 'text-slate-700 dark:text-slate-300'} text-xs font-bold">${c.icon ? `<span class="material-symbols-outlined text-base mr-1 align-middle">${c.icon}</span>` : ""}${esc(c.label)}</th>`).join("")}
                </tr>
              </thead>
              <tbody>
                ${(s.rows || []).map(r => `
                  <tr class="border-b border-slate-100 dark:border-brand-darkBorder/60 last:border-0">
                    <td class="p-3 text-xs font-bold text-slate-700 dark:text-slate-300">${esc(r.label || "")}</td>
                    ${cols.map(c => `<td class="p-3 text-xs sm:text-sm ${highlight === c.key ? 'bg-brand-primary/5 dark:bg-brand-lightBlue/5' : ''} text-slate-700 dark:text-slate-300">${(r.cells && r.cells[c.key]) || ""}</td>`).join("")}
                  </tr>`).join("")}
              </tbody>
            </table>
          </div>
        </div>`;
    }

    // ────────────────────────────────────────────────────────────────────────
    // TYPE 18: faqAccordion (NEW)
    // ────────────────────────────────────────────────────────────────────────
    function renderFaqAccordion(s) {
      const items = (s.items || []).map((it, i) => `
        <details class="${UI.card} group">
          <summary class="p-4 cursor-pointer flex items-center justify-between gap-3 list-none">
            <span class="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              ${it.icon ? `<span class="material-symbols-outlined text-brand-primary dark:text-brand-lightBlue text-base">${it.icon}</span>` : `<span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-brand-primary/10 text-brand-primary dark:text-brand-lightBlue">Q${i+1}</span>`}
              ${esc(it.q)}
            </span>
            <span class="material-symbols-outlined text-slate-400 group-open:rotate-180 transition-transform">expand_more</span>
          </summary>
          <div class="px-4 pb-4 text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed">${it.a || ""}</div>
        </details>`).join("");
      return `
        <div class="max-w-3xl mx-auto space-y-3">
          ${(s.title || s.lead) ? uiTitle(s.title, s.lead) : ""}
          ${items}
        </div>`;
    }

    // ────────────────────────────────────────────────────────────────────────
    // SLIDE RENDERER REGISTRY — single source of truth.
    // To add a new slide type: write `renderYourType(slideDef)` above and
    // add an entry below: `'yourType': renderYourType`.
    // ────────────────────────────────────────────────────────────────────────
    const SLIDE_RENDERERS = {
      'cover':              renderCover,
      'cardList':           renderCardList,
      'treeCanvas':         renderTreeCanvas,
      'scenarioPicker':    renderScenarioPicker,
      'tabbedAccordion':    renderTabbedAccordion,
      'verificationMatrix': renderVerificationMatrix,
      'twoCardAccordion':   renderTwoCardAccordion,
      'docTabs':            renderDocTabs,
      'kpiDashboard':      renderKpiDashboard,
      'riskCards':         renderRiskCards,
      'quiz':              renderQuiz,
      'summaryCertificate':renderSummaryCertificate,
      'imageGallery':      renderImageGallery,
      'videoEmbed':        renderVideoEmbed,
      'calloutBox':        renderCalloutBox,
      'stepByStep':        renderStepByStep,
      'comparisonTable':   renderComparisonTable,
      'faqAccordion':      renderFaqAccordion
    };

'''

# ────────────────────────────────────────────────────────────────────────────
# 5. SKIP LINES 2482-2502 entirely (old } closing renderCurrentSlide + old
#    QUIZ CONTROLLER comment header + old shuffleArray + old ensureQuizOrder
#    which references QUIZ_QUESTIONS). The NEW quiz engine below defines its
#    own versions.
# ────────────────────────────────────────────────────────────────────────────
quiz_pre_block = ""  # nothing — NEW_QUIZ_ENGINE has its own header

# ────────────────────────────────────────────────────────────────────────────
# 6. NEW EXTENDED QUIZ ENGINE (replaces lines 2503-2648)
# ────────────────────────────────────────────────────────────────────────────
NEW_QUIZ_ENGINE = r'''
    // ========================================================================
    // QUIZ ENGINE — supports MCQ + True/False + Fill-in-the-blank
    // ========================================================================
    function shuffleArray(arr) {
      const a = arr.slice();
      for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
      }
      return a;
    }

    function getCurrentQuizQuestions() {
      // Find the quiz slideDef — could be the current slide (most common) OR a slide referenced elsewhere
      const slide = COURSE.slides[state.currentSlide];
      if (slide && slide.type === 'quiz' && slide.questions) return slide.questions;
      // Fallback: scan for any quiz slide
      const quizSlide = COURSE.slides.find(s => s.type === 'quiz');
      return (quizSlide && quizSlide.questions) || [];
    }

    function ensureQuizOrder() {
      // For each MCQ question, build a shuffled option-order array.
      // TF and fillIn don't need shuffling.
      if (state.quizOrder) return;
      const qs = getCurrentQuizQuestions();
      state.quizOrder = qs.map(q => {
        if (q.type === 'mcq') {
          const idxs = q.options.map((_, i) => i);
          return shuffleArray(idxs);
        }
        return null; // no shuffling for TF/fillIn
      });
    }

    function renderQuizSlide(container) {
      const qs = getCurrentQuizQuestions();
      const total = qs.length;
      if (!total) {
        container.innerHTML = `<div class="p-8 text-center text-slate-500">No quiz questions defined.</div>`;
        return;
      }
      // Summary screen post-submit
      if (state.quizCompleted) {
        renderQuizSummary(container, qs);
        return;
      }
      const idx = state.quizIndex;
      const q = qs[idx];
      // Progress indicator
      const dots = qs.map((_, i) => {
        const answered = state.userAnswers[i] != null;
        const current = i === idx;
        return `<button onclick="quizJump(${i})" class="w-7 h-7 rounded-full text-[10px] font-bold flex items-center justify-center border-2 transition-all ${current ? 'border-brand-primary dark:border-brand-lightBlue bg-brand-primary text-white' : answered ? 'border-brand-primary/50 dark:border-brand-lightBlue/50 text-brand-primary dark:text-brand-lightBlue' : 'border-slate-300 dark:border-brand-darkBorder text-slate-400'}">${i+1}</button>`;
      }).join(" ");

      let questionHtml = "";
      if (q.type === 'mcq') {
        const order = state.quizOrder[idx] || q.options.map((_, i) => i);
        questionHtml = `<div class="space-y-2 mt-4" role="radiogroup">
          ${q.options.map((opt, i) => {
            const originalIdx = order[i];
            const isSelected = state.userAnswers[idx] === originalIdx;
            return `<button onclick="selectQuizAnswer(${idx}, ${originalIdx})" role="radio" aria-checked="${isSelected}" class="w-full text-left p-3 rounded-xl border-2 ${isSelected ? 'border-brand-primary dark:border-brand-lightBlue bg-brand-primary/5 dark:bg-brand-lightBlue/5' : 'border-slate-200 dark:border-brand-darkBorder hover:border-brand-primary/50'} btn-tactile flex items-start gap-2">
              <span class="w-5 h-5 rounded-full border-2 ${isSelected ? 'border-brand-primary dark:border-brand-lightBlue bg-brand-primary dark:bg-brand-lightBlue' : 'border-slate-300 dark:border-brand-darkBorder'} flex items-center justify-center shrink-0 mt-0.5">${isSelected ? '<span class="w-2 h-2 rounded-full bg-white"></span>' : ''}</span>
              <span class="text-xs sm:text-sm text-slate-700 dark:text-slate-200">${esc(opt)}</span>
            </button>`;
          }).join("")}
        </div>`;
      } else if (q.type === 'trueFalse') {
        const sel = state.userAnswers[idx];
        const opt = (val, label) => `<button onclick="selectQuizAnswer(${idx}, ${val})" role="radio" aria-checked="${sel === val}" class="flex-1 p-3 rounded-xl border-2 ${sel === val ? 'border-brand-primary dark:border-brand-lightBlue bg-brand-primary/5 dark:bg-brand-lightBlue/5' : 'border-slate-200 dark:border-brand-darkBorder hover:border-brand-primary/50'} btn-tactile text-sm font-bold text-slate-700 dark:text-slate-200">${label}</button>`;
        questionHtml = `<div class="flex gap-2 mt-4" role="radiogroup">${opt(true, "Benar")}${opt(false, "Salah")}</div>`;
      } else if (q.type === 'fillIn') {
        const cur = state.userAnswers[idx] != null ? state.userAnswers[idx] : "";
        questionHtml = `<div class="mt-4">
          <input type="text" value="${esc(cur)}" placeholder="${esc(q.placeholder || "Ketik jawaban Anda...")}" oninput="selectQuizAnswer(${idx}, this.value)" class="w-full px-4 py-3 rounded-xl border-2 border-slate-200 dark:border-brand-darkBorder bg-white dark:bg-brand-darkSurface text-slate-900 dark:text-white text-sm focus:border-brand-primary dark:focus:border-brand-lightBlue focus:outline-none">
          <p class="mt-2 text-[10px] text-slate-500 dark:text-slate-400">Jawaban diterima case-insensitive.</p>
        </div>`;
      } else {
        questionHtml = `<div class="p-4 text-center text-red-500">Unknown question type: ${q.type}</div>`;
      }

      container.innerHTML = `
        <div class="space-y-4">
          <div class="flex items-center justify-between gap-2">
            <div class="flex flex-wrap gap-1.5">${dots}</div>
            <span class="text-xs text-slate-500 dark:text-slate-400">${idx+1} / ${total}</span>
          </div>
          <div class="${UI.card} p-5 space-y-3">
            <p class="text-sm sm:text-base font-bold text-slate-900 dark:text-white leading-relaxed">${esc(q.question)}</p>
            ${questionHtml}
          </div>
          <div class="flex items-center justify-between gap-2">
            <button onclick="quizJump(${Math.max(0, idx-1)})" ${idx === 0 ? 'disabled' : ''} class="px-4 py-2 rounded-lg text-xs font-bold ${idx === 0 ? 'bg-slate-100 dark:bg-brand-darkSubtle text-slate-400 cursor-not-allowed' : 'bg-slate-100 dark:bg-brand-darkSubtle text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-brand-darkBorder'} btn-tactile flex items-center gap-1"><span class="material-symbols-outlined text-base">arrow_back</span>Prev</button>
            ${idx === total - 1
              ? `<button onclick="submitQuizEvaluation()" class="px-4 py-2 rounded-lg text-xs font-bold bg-emerald-500 text-white hover:bg-emerald-600 btn-tactile flex items-center gap-1"><span class="material-symbols-outlined text-base">check_circle</span>Submit</button>`
              : `<button onclick="quizJump(${idx+1})" class="px-4 py-2 rounded-lg text-xs font-bold bg-brand-primary text-white hover:bg-brand-primaryHover btn-tactile flex items-center gap-1">Next<span class="material-symbols-outlined text-base">arrow_forward</span></button>`}
          </div>
        </div>`;
    }

    function renderQuizSummary(container, qs) {
      const total = qs.length;
      const correct = qs.reduce((acc, q, i) => acc + (isAnswerCorrect(q, state.userAnswers[i]) ? 1 : 0), 0);
      const pct = Math.round((correct / total) * 100);
      const passed = pct >= (COURSE.course.passingScore || 80);
      const rows = qs.map((q, i) => {
        const userAns = state.userAnswers[i];
        const isCorrect = isAnswerCorrect(q, userAns);
        const userDisplay = displayAnswer(q, userAns);
        const correctDisplay = displayCorrectAnswer(q);
        return `<div class="${UI.card} p-4">
          <div class="flex items-start gap-2 mb-2">
            <span class="material-symbols-outlined ${isCorrect ? 'text-emerald-500' : 'text-rose-500'}">${isCorrect ? 'check_circle' : 'cancel'}</span>
            <p class="text-sm font-bold text-slate-900 dark:text-white flex-1">${esc(q.question)}</p>
          </div>
          <div class="ml-7 space-y-1 text-xs">
            <p class="text-slate-600 dark:text-slate-400">Your answer: <span class="${isCorrect ? 'text-emerald-700 dark:text-emerald-300' : 'text-rose-700 dark:text-rose-300'} font-semibold">${userDisplay || "—"}</span></p>
            ${!isCorrect ? `<p class="text-slate-600 dark:text-slate-400">Correct: <span class="text-emerald-700 dark:text-emerald-300 font-semibold">${correctDisplay}</span></p>` : ""}
            ${q.explanation ? `<p class="text-slate-500 dark:text-slate-400 mt-2 italic">${esc(q.explanation)}</p>` : ""}
          </div>
        </div>`;
      }).join("");
      container.innerHTML = `
        <div class="space-y-4">
          <div class="text-center ${UI.card} p-6">
            <p class="text-5xl font-extrabold ${passed ? 'text-emerald-500' : 'text-rose-500'}">${pct}<span class="text-2xl">/100</span></p>
            <p class="mt-2 text-sm ${passed ? 'text-emerald-700 dark:text-emerald-300' : 'text-rose-700 dark:text-rose-300'}">${passed ? 'Lulus!' : 'Belum lulus'}</p>
            <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">${correct} dari ${total} benar</p>
          </div>
          ${rows}
          <div class="flex justify-center gap-2">
            <button onclick="resetQuiz()" class="px-4 py-2 rounded-lg text-xs font-bold bg-slate-100 dark:bg-brand-darkSubtle text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-brand-darkBorder btn-tactile flex items-center gap-1"><span class="material-symbols-outlined text-base">refresh</span>Ulangi</button>
          </div>
        </div>`;
    }

    function displayAnswer(q, ans) {
      if (ans == null || ans === "") return "—";
      if (q.type === 'mcq') return q.options[ans] || "—";
      if (q.type === 'trueFalse') return ans === true ? "Benar" : "Salah";
      if (q.type === 'fillIn') return String(ans);
      return String(ans);
    }

    function displayCorrectAnswer(q) {
      if (q.type === 'mcq') return q.options[q.correctIndex] || "—";
      if (q.type === 'trueFalse') return q.correctBool ? "Benar" : "Salah";
      if (q.type === 'fillIn') return (q.acceptedAnswers || []).join(" / ");
      return "—";
    }

    function isAnswerCorrect(q, ans) {
      if (ans == null || ans === "") return false;
      if (q.type === 'mcq') return ans === q.correctIndex;
      if (q.type === 'trueFalse') return ans === q.correctBool;
      if (q.type === 'fillIn') {
        const norm = String(ans).trim().toLowerCase();
        return (q.acceptedAnswers || []).some(a => a.trim().toLowerCase() === norm);
      }
      return false;
    }

    function quizJump(i) {
      const qs = getCurrentQuizQuestions();
      if (i < 0 || i >= qs.length) return;
      playTone('click');
      state.quizIndex = i;
      const body = document.getElementById("slideBody");
      // Find quiz container
      const container = body.querySelector('#quizContainer') || body;
      renderQuizSlide(container);
    }

    function selectQuizAnswer(qIdx, ans) {
      state.userAnswers[qIdx] = ans;
      const body = document.getElementById("slideBody");
      const container = body.querySelector('#quizContainer') || body;
      renderQuizSlide(container);
    }

    function submitQuizEvaluation() {
      const qs = getCurrentQuizQuestions();
      const total = qs.length;
      const unanswered = qs.reduce((acc, _, i) => acc + (state.userAnswers[i] == null || state.userAnswers[i] === "" ? 1 : 0), 0);
      if (unanswered > 0) {
        playTone('error');
        if (!confirm(`Masih ada ${unanswered} soal belum dijawab. Submit anyway?`)) return;
      }
      const correct = qs.reduce((acc, q, i) => acc + (isAnswerCorrect(q, state.userAnswers[i]) ? 1 : 0), 0);
      state.quizScore = Math.round((correct / total) * 100);
      state.quizCompleted = true;
      if (state.quizScore >= (COURSE.course.passingScore || 80)) {
        playTone('fanfare');
        try { confetti({ particleCount: 80, spread: 70, origin: { y: 0.6 } }); } catch (e) {}
      } else {
        playTone('error');
      }
      const body = document.getElementById("slideBody");
      const container = body.querySelector('#quizContainer') || body;
      renderQuizSlide(container);
      updateNavigationControls();
    }

    function resetQuiz() {
      playTone('click');
      state.userAnswers = {};
      state.quizScore = 0;
      state.quizCompleted = false;
      state.quizIndex = 0;
      state.quizOrder = null;
      ensureQuizOrder();
      const body = document.getElementById("slideBody");
      const container = body.querySelector('#quizContainer') || body;
      renderQuizSlide(container);
      updateNavigationControls();
    }

'''

# ────────────────────────────────────────────────────────────────────────────
# 7. KEEP LINES 2649-2652 (between)
# ────────────────────────────────────────────────────────────────────────────
between_block = L(2649, 2652)

# ────────────────────────────────────────────────────────────────────────────
# 8. SKIP LINES 2653-2770 (old testCompliance + testBranchPfc)
#    — Already covered by the generic runScenario() in NEW_RENDER_DISPATCHER.
# ────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────
# 9. KEEP LINES 2771-2787 (calcAuditScore — already generic)
# ────────────────────────────────────────────────────────────────────────────
calc_audit_block = L(2771, 2787)

# ────────────────────────────────────────────────────────────────────────────
# 10. KEEP LINES 2788-2857 (openSwimlaneHotspot + closeHotspotModal + filterSwimlaneRole)
#     — Update openSwimlaneHotspot to read swimlane data from current slide.
# ────────────────────────────────────────────────────────────────────────────
hotspot_block = L(2788, 2857)
hotspot_block = hotspot_block.replace(
    "const all = SWIMLANE_FLOWCHART.flatMap(s => s.items || []);",
    "const slide = COURSE.slides[state.currentSlide];\n      const all = (slide.swimlaneData || []).flatMap(s => s.items || []);"
)
# Also handle the old fallback search if it referenced SWIMLANE_FLOWCHART.items
hotspot_block = hotspot_block.replace("SWIMLANE_FLOWCHART", "(slide.swimlaneData || [])")

# ────────────────────────────────────────────────────────────────────────────
# 11. KEEP LINES 2858-3109 (modal openers, sidebar controllers, updateOutlineUI)
#     — Apply COURSE_CONFIG→COURSE.course, COURSE_UNITS→COURSE.units, DEFINISI_POIN_4→COURSE.glossary replacements
# ────────────────────────────────────────────────────────────────────────────
engine_block = L(2858, 3109)
engine_block = engine_block.replace("COURSE_CONFIG.totalUnits", "COURSE.units.length")
engine_block = engine_block.replace("COURSE_CONFIG.devMode", "COURSE.course.devMode")
engine_block = engine_block.replace("COURSE_CONFIG.passingScore", "COURSE.course.passingScore")
engine_block = engine_block.replace("COURSE_CONFIG.totalQuestions", "COURSE.course.totalQuestions")
engine_block = engine_block.replace("COURSE_CONFIG", "COURSE.course")
engine_block = engine_block.replace("COURSE_UNITS", "COURSE.units")
engine_block = engine_block.replace("DEFINISI_POIN_4", "COURSE.glossary")

# ────────────────────────────────────────────────────────────────────────────
# 12. SKIP NARRATION_TRANSCRIPTS (lines 3110-3124) — replace with empty lookup
# ────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────
# 13. KEEP + MODIFY updateTranscriptAndCC (lines 3125-3147)
# ────────────────────────────────────────────────────────────────────────────
transcript_block = L(3125, 3147)
transcript_block = transcript_block.replace(
    "const text = NARRATION_TRANSCRIPTS[state.currentSlide] || \"Transkrip belum tersedia.\";",
    "const slideDef = COURSE.slides[state.currentSlide];\n      const narr = (slideDef && slideDef.narration) || (COURSE.narration && (COURSE.narration[String(state.currentSlide)] || COURSE.narration[state.currentSlide])) || \"Transkrip belum tersedia.\";"
)
transcript_block = transcript_block.replace("text", "narr", 1)  # rename first occurrence only

# Also need to handle the inner usages of `text` — let's be safer and just do a full
# targeted rewrite of updateTranscriptAndCC.

NEW_TRANSCRIPT_FN = '''
    function updateTranscriptAndCC() {
      const slideDef = COURSE.slides[state.currentSlide];
      const narr = (slideDef && slideDef.narration)
        || (COURSE.narration && (COURSE.narration[String(state.currentSlide)] || COURSE.narration[state.currentSlide]))
        || "Transkrip belum tersedia.";
      const notes = document.getElementById("notesTextContainer");
      const cap = document.getElementById("captionText");
      if (notes) notes.innerHTML = `<p class="text-xs leading-relaxed text-slate-600 dark:text-slate-400">${narr}</p>`;
      if (cap) cap.innerText = narr;
    }

'''

# ────────────────────────────────────────────────────────────────────────────
# 14. KEEP LINES 3148-3204 (theme, fullscreen, printCertificate)
#     — Modify printCertificate to use COURSE.brand.* and COURSE.course.* paths.
# ────────────────────────────────────────────────────────────────────────────
theme_print_block = L(3148, 3204)
# Patch printCertificate's hardcoded brand string to read from COURSE.brand at runtime
theme_print_block = theme_print_block.replace(
    '`NIP: ${state.participantNIP || "-"} • PT PP (Persero) Tbk`',
    '`NIP: ${state.participantNIP || "-"} • ${COURSE.brand.orgName || ""}`'
)
# Update cert reg prefix — old code hardcodes "PP/HCM-QA/C1-050" — replace with brand.certRegPrefix
theme_print_block = theme_print_block.replace(
    '`No. Reg: PP/HCM-QA/C1-050/${new Date().getFullYear()}/${randNum}`',
    '`No. Reg: ${(COURSE.brand.certRegPrefix || "REG")}/${new Date().getFullYear()}/${randNum}`'
)
# Apply COURSE_CONFIG → COURSE.course for any remaining refs
theme_print_block = theme_print_block.replace("COURSE_CONFIG", "COURSE.course")

# ────────────────────────────────────────────────────────────────────────────
# 15. SKIP renderAuthenticSOPTree (lines 3205-3703) — replaced by renderTreeCanvas
#     which is already in NEW_RENDER_DISPATCHER above.
# ────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────
# 16. KEEP LINES 3704-4153 (pan/zoom engine, keyboard nav, DOMContentLoaded init)
#     — Modify DOMContentLoaded to populate Tenggat + Hint + Resources from COURSE.
#     — Patch updatePhaseBadgeUI to look up phase labels from slideDef.phaseJumps.
# ────────────────────────────────────────────────────────────────────────────
tail_block = L(3704, n)
# Patch updatePhaseBadgeUI hardcoded phase text
tail_block = tail_block.replace(
    'txt.innerText = "Fase 3: Tahap 5.21 – 5.28 (BAST-2 & Selesai Paripurna)";',
    'txt.innerText = (COURSE.slides[state.currentSlide].phaseJumps || [])[2]?.label || "Fase 3";'
)
tail_block = tail_block.replace(
    'txt.innerText = "Fase 2: Tahap 5.15 – 5.20 (Tutup Buku I & SAP)";',
    'txt.innerText = (COURSE.slides[state.currentSlide].phaseJumps || [])[1]?.label || "Fase 2";'
)
tail_block = tail_block.replace(
    'txt.innerText = "Fase 1: Tahap 5.1 – 5.14 (Fisik 100% & HP V)";',
    'txt.innerText = (COURSE.slides[state.currentSlide].phaseJumps || [])[0]?.label || "Fase 1";'
)
# Patch the `audioPath = ./audio/unit_N.mp3` to use slideDef.narration path? 
# Actually keep as-is — the audioPath uses state.currentSlide which is fine.

# Update DOMContentLoaded to populate empty modal containers
old_dcl = '''window.addEventListener("DOMContentLoaded", () => {
      applyTheme();
      goToSlide(0);
      updateOutlineUI();
      document.querySelectorAll("dialog").forEach(d => {
        d.addEventListener("click", (e) => { if (e.target === d) d.close(); });
        d.addEventListener("close", () => {
          if (state.lastFocusedElement) { try { state.lastFocusedElement.focus(); } catch (err) {} state.lastFocusedElement = null; }
        });
      });
    });'''

new_dcl = '''window.addEventListener("DOMContentLoaded", () => {
      applyTheme();
      initCheatSheet();
      initHintTips();
      initResources();
      goToSlide(0);
      updateOutlineUI();
      document.querySelectorAll("dialog").forEach(d => {
        d.addEventListener("click", (e) => { if (e.target === d) d.close(); });
        d.addEventListener("close", () => {
          if (state.lastFocusedElement) { try { state.lastFocusedElement.focus(); } catch (err) {} state.lastFocusedElement = null; }
        });
      });
    });

    function initCheatSheet() {
      const grid = document.getElementById("tenggatGrid");
      if (!grid) return;
      const items = COURSE.tenggatCheatSheet || [];
      if (!items.length) { grid.innerHTML = "<p class=\\"text-xs text-slate-500 dark:text-slate-400 col-span-full text-center py-4\\">No quick-reference cards defined.</p>"; return; }
      grid.innerHTML = items.map(c => `
        <div class="${UI.card} p-4 flex flex-col items-center text-center gap-1">
          ${c.icon ? `<span class="material-symbols-outlined text-brand-primary dark:text-brand-lightBlue text-xl">${c.icon}</span>` : ""}
          <p class="text-2xl font-extrabold text-slate-900 dark:text-white">${esc(c.value)}</p>
          <p class="${UI.label}">${esc(c.label)}</p>
          ${c.title ? `<p class="text-xs font-bold text-slate-700 dark:text-slate-200">${esc(c.title)}</p>` : ""}
          ${c.desc ? `<p class="text-[10px] text-slate-500 dark:text-slate-400">${esc(c.desc)}</p>` : ""}
        </div>`).join("");
    }

    function initHintTips() {
      const grid = document.getElementById("hintGrid");
      if (!grid) return;
      const items = COURSE.hintTips || [];
      if (!items.length) { grid.innerHTML = "<p class=\\"text-xs text-slate-500 dark:text-slate-400 col-span-full text-center py-4\\">No navigation tips defined.</p>"; return; }
      grid.innerHTML = items.map(c => `
        <div class="${UI.card} p-4 flex items-start gap-3">
          ${c.icon ? `<span class="material-symbols-outlined text-brand-primary dark:text-brand-lightBlue text-xl shrink-0">${c.icon}</span>` : ""}
          <div>
            <p class="text-sm font-bold text-slate-900 dark:text-white">${esc(c.title)}</p>
            ${c.desc ? `<p class="mt-1 ${UI.text}">${esc(c.desc)}</p>` : ""}
          </div>
        </div>`).join("");
    }

    function initResources() {
      const panel = document.getElementById("tabContentResources");
      if (!panel) return;
      const items = COURSE.resources || [];
      if (!items.length) return; // keep default empty
      panel.innerHTML = `<div class="p-3 space-y-2">${items.map(r => `
        <div class="${UI.card} p-3">
          <div class="flex items-center gap-2">
            ${r.icon ? `<span class="material-symbols-outlined text-brand-primary dark:text-brand-lightBlue text-base">${r.icon}</span>` : ""}
            <p class="text-xs font-bold text-slate-900 dark:text-white">${esc(r.title)}</p>
          </div>
          ${r.desc ? `<p class="mt-1 ${UI.text}">${esc(r.desc)}</p>` : ""}
          ${r.items && r.items.length ? `<ul class="mt-2 space-y-1 list-disc list-inside ${UI.text}">${r.items.map(it => `<li>${esc(it)}</li>`).join("")}</ul>` : ""}
        </div>`).join("")}</div>`;
    }'''

# Update DOMContentLoaded to populate empty modal containers
# Simplification: the DOMContentLoaded listener is the LAST block in the file
# (right before </script>). Truncate tail_block at the listener's start, then
# append new_dcl + the file's closing tags.
anchor = 'window.addEventListener("DOMContentLoaded",'
dcl_start = tail_block.find(anchor)
if dcl_start != -1:
    # Find the indentation prefix (likely 4 spaces)
    line_start = dcl_start
    while line_start > 0 and tail_block[line_start - 1] in ' \t':
        line_start -= 1
    # Find the </script> tag after the listener
    script_close = tail_block.find('</script>', dcl_start)
    if script_close == -1:
        script_close = len(tail_block)
    # Truncate from the listener start, append new_dcl + closing tags
    tail_block = (tail_block[:line_start]
                  + new_dcl
                  + "\n  </script>\n</body>\n</html>\n")
    print("  Updated DOMContentLoaded (truncate approach) to populate Tenggat + Hint + Resources.")
else:
    print("  WARN: Could not find DOMContentLoaded block to update.", file=sys.stderr)

# Apply state mutation patch — old code mutated COURSE_UNITS[idx].completed
tail_block = tail_block.replace("COURSE_UNITS[state.currentSlide].completed", "COURSE.units[state.currentSlide].completed = true")
tail_block = tail_block.replace("COURSE_CONFIG", "COURSE.course")
tail_block = tail_block.replace("COURSE_UNITS", "COURSE.units")
# Clean up stale comments
tail_block = tail_block.replace(
    "renderTreeCanvas (replaces renderAuthenticSOPTree) — defined above inside NEW_RENDER_DISPATCHER block.",
    "renderTreeCanvas is defined inside the NEW_RENDER_DISPATCHER block above."
)
# Also clean up in head_and_skeleton (which has the DEFINISI_POIN_4 comment)
head_and_skeleton = head_and_skeleton.replace(
    "<!-- Injected via JavaScript from DEFINISI_POIN_4 array -->",
    "<!-- Injected by renderTerminologiList() from COURSE.glossary -->"
)
# And clean up NEW_RENDER_DISPATCHER's own comment (it's a literal Python string, so we patch it via Python replace)
NEW_RENDER_DISPATCHER = NEW_RENDER_DISPATCHER.replace(
    "renderTreeCanvas (replaces renderAuthenticSOPTree) — defined above inside NEW_RENDER_DISPATCHER block.",
    "renderTreeCanvas is defined inside this same block above."
)

# ────────────────────────────────────────────────────────────────────────────
# 17. ASSEMBLE FINAL TEMPLATE
# ────────────────────────────────────────────────────────────────────────────
final = (
    head_and_skeleton
    + COURSE_PLACEHOLDER
    + engine_state_audio_nav
    + "\n"
    + render_flow_node_block
    + NEW_RENDER_DISPATCHER
    + quiz_pre_block
    + NEW_QUIZ_ENGINE
    + between_block
    + calc_audit_block
    + hotspot_block
    + engine_block
    + NEW_TRANSCRIPT_FN
    + theme_print_block
    + "\n    // ========================================================================\n"
    + "    // renderTreeCanvas is defined inside the NEW_RENDER_DISPATCHER block above.\n"
    + "    // ========================================================================\n\n"
    + tail_block
)

DST.parent.mkdir(parents=True, exist_ok=True)
DST.write_text(final, encoding="utf-8")
print(f"Output: {DST} ({len(final.splitlines())} lines, {len(final)} chars)")
