"""Smoke test the built e-learning module with Playwright.

Opens the HTML file via file://, captures console errors + warnings,
verifies key DOM elements exist + key functions are callable.

USAGE
  python3 /home/z/my-project/scripts/smoke_test_module.py <html_path>
"""
import sys
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    if len(sys.argv) < 2:
        print("USAGE: smoke_test_module.py <html_path>", file=sys.stderr)
        sys.exit(2)
    html_path = Path(sys.argv[1]).resolve()
    if not html_path.exists():
        print(f"ERROR: {html_path} not found", file=sys.stderr)
        sys.exit(2)

    url = f"file://{html_path}"
    print(f"Loading: {url}")

    errors = []
    warnings = []
    logs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()

        page.on("console", lambda msg: (
            errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error"
            else warnings.append(f"[{msg.type}] {msg.text}") if msg.type == "warning"
            else logs.append(f"[{msg.type}] {msg.text}")
        ))
        page.on("pageerror", lambda err: errors.append(f"[PAGEERROR] {err}"))

        page.goto(url, wait_until="networkidle", timeout=30000)
        # Wait a bit for any async stuff
        page.wait_for_timeout(1500)

        # Check key DOM elements exist
        checks = [
            ("#topHeader",              "Top header"),
            ("#courseSidebar",          "Sidebar"),
            ("#slideBody",              "Slide body"),
            ("#bottomPlaybar",          "Bottom playbar"),
            ("#seekBar",                "Seekbar"),
            ("#btnNextSlide",           "Next button"),
            ("#btnPrevSlide",           "Prev button"),
            ("#slideCounterText",       "Slide counter"),
            ("#overallPercentage",      "Progress %"),
            ("#outlineNavList",         "Outline list"),
            ("#notesTextContainer",    "Notes container"),
            ("#captionText",            "Caption text"),
        ]
        print("\n=== DOM element checks ===")
        missing = []
        for sel, name in checks:
            count = page.locator(sel).count()
            status = "✓" if count > 0 else "✗ MISSING"
            print(f"  {status} {sel} ({name})")
            if count == 0:
                missing.append(sel)

        # Check COURSE object loaded
        print("\n=== COURSE object check ===")
        course_loaded = page.evaluate("typeof COURSE !== 'undefined' && COURSE !== null")
        print(f"  {'✓' if course_loaded else '✗'} COURSE loaded: {course_loaded}")
        if course_loaded:
            n_units = page.evaluate("COURSE.units.length")
            n_slides = page.evaluate("COURSE.slides.length")
            print(f"  ✓ units.length = {n_units}, slides.length = {n_slides}")
            # Check first slide rendered
            body_html = page.locator("#slideBody").inner_html()
            print(f"  ✓ #slideBody innerHTML length: {len(body_html)}")
            # Check counter text reflects slide 1 of N
            counter = page.locator("#slideCounterText").inner_text()
            print(f"  ✓ #slideCounterText = '{counter}'")

        # Try navigating to slide 1 (index 1) via global function goToSlide
        print("\n=== Navigation test ===")
        try:
            page.evaluate("goToSlide(1)")
            page.wait_for_timeout(500)
            counter = page.locator("#slideCounterText").inner_text()
            print(f"  ✓ goToSlide(1) → #slideCounterText = '{counter}'")
        except Exception as e:
            errors.append(f"goToSlide(1) failed: {e}")
            print(f"  ✗ goToSlide(1) failed: {e}")

        # Try navigating to quiz slide (index 4 in sample)
        print("\n=== Quiz slide test ===")
        try:
            page.evaluate("goToSlide(4)")
            page.wait_for_timeout(500)
            counter = page.locator("#slideCounterText").inner_text()
            print(f"  ✓ goToSlide(4) → #slideCounterText = '{counter}'")
            quiz_visible = page.locator("#quizContainer").count() > 0
            print(f"  ✓ quiz container visible: {quiz_visible}")
        except Exception as e:
            errors.append(f"goToSlide(4) (quiz) failed: {e}")
            print(f"  ✗ quiz slide test failed: {e}")

        # Try navigating to treeCanvas (slide 2)
        print("\n=== Tree canvas test ===")
        try:
            page.evaluate("goToSlide(2)")
            page.wait_for_timeout(800)
            counter = page.locator("#slideCounterText").inner_text()
            tree_present = page.locator("#treeCanvasViewport").count() > 0
            flow_nodes = page.locator(".flow-card-node").count()
            # Authentic 3-column layout: col-span-3 (input/output) + col-span-6 (center)
            col3_count = page.locator("#treeCanvasInner .col-span-3").count()
            col6_count = page.locator("#treeCanvasInner .col-span-6").count()
            fase_containers = page.locator("#treeCanvasInner [id^='fase-']").count()
            print(f"  ✓ goToSlide(2) → #slideCounterText = '{counter}'")
            print(f"  ✓ treeCanvas={tree_present}, flow-card-nodes={flow_nodes}")
            print(f"  ✓ 3-column layout: col-span-3={col3_count}, col-span-6={col6_count}, fase containers={fase_containers}")
            if col3_count == 0 or col6_count == 0:
                errors.append("treeCanvas: 3-column layout not rendered (col-span-3/col-span-6 missing)")
            if fase_containers == 0:
                errors.append("treeCanvas: phase containers (#fase-N) not rendered")
        except Exception as e:
            errors.append(f"goToSlide(2) (treeCanvas) failed: {e}")
            print(f"  ✗ treeCanvas slide test failed: {e}")

        # Try opening Tenggat modal
        print("\n=== Modal test (Tenggat) ===")
        try:
            page.evaluate("openTenggatModal()")
            page.wait_for_timeout(300)
            open_state = page.evaluate("document.getElementById('modalTenggat').open")
            print(f"  ✓ openTenggatModal() → open = {open_state}")
            page.evaluate("closeTenggatModal()")
        except Exception as e:
            errors.append(f"Tenggat modal failed: {e}")
            print(f"  ✗ Tenggat modal test failed: {e}")

        browser.close()

    print("\n=== Summary ===")
    print(f"Errors:   {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    if errors:
        print("\n--- ERRORS ---")
        for e in errors[:10]:
            print(f"  {e}")
    if warnings:
        print("\n--- WARNINGS ---")
        for w in warnings[:10]:
            print(f"  {w}")
    sys.exit(0 if not errors else 1)

if __name__ == "__main__":
    main()
