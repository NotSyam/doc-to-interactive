#!/usr/bin/env python3
"""
build_module.py — E-Learning Module Builder

Reads a content.json (matching assets/content.schema.json) + a brand profile
(from assets/brand.profiles.json), injects them into assets/shell.template.html,
replaces all __*__ placeholders, and writes a self-contained final HTML module.

USAGE
  python3 build_module.py --content <content.json> --output <out.html> [options]

OPTIONS
  --content PATH          Path to content.json (required)
  --output PATH           Path to write final HTML (required)
  --brand-preset NAME     Override brand.preset in content.json
                          (one of: ptpp, corporate, education, tech-startup, custom)
  --skill-root PATH       Path to skill root (default: this script's parent dir)
  --validate              Run validate_content.py before building
  --no-validate           Skip validation (default)

EXAMPLE
  python3 build_module.py \\
    --content samples/ptpp-sop.content.json \\
    --output /home/z/my-project/download/my-module.html \\
    --validate
"""
import argparse
import json
import re
import sys
from pathlib import Path

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)


def resolve_brand(content: dict, profiles: dict, preset_override: str = None) -> dict:
    """Merge: profile preset → inline content.brand overrides → CLI override.
    Returns a flat brand dict with all keys."""
    brand_block = dict(content.get("brand") or {})
    preset_name = preset_override or brand_block.get("preset", "ptpp")

    if preset_name == "custom":
        # Use inline fields verbatim
        return brand_block
    if preset_name not in profiles:
        print(f"ERROR: Unknown brand preset '{preset_name}'. Available: {', '.join(profiles.keys())}", file=sys.stderr)
        sys.exit(1)

    merged = dict(profiles[preset_name])
    # Overlay inline fields
    for k, v in brand_block.items():
        if k == "preset":
            continue
        merged[k] = v
    merged["preset"] = preset_name
    return merged


def inject_course_data(template: str, course_obj: dict) -> str:
    """Replace `let COURSE = null; // __COURSE_DATA_INJECTION_POINT__` with
    `let COURSE = <JSON>;` AND strip any remaining mention of the marker in
    comment text."""
    marker = "let COURSE = null; // __COURSE_DATA_INJECTION_POINT__"
    injection = "let COURSE = " + json.dumps(course_obj, ensure_ascii=False, indent=2) + ";"
    if marker in template:
        template = template.replace(marker, injection)
    else:
        # Fall back: any line that contains the marker
        m = re.search(r"let\s+COURSE\s*=\s*null;.*__COURSE_DATA_INJECTION_POINT__", template)
        if not m:
            print("ERROR: Could not find COURSE_DATA injection point in template.", file=sys.stderr)
            sys.exit(1)
        template = template[:m.start()] + injection + ";" + template[m.end():]
    # Strip any remaining mentions in comment text
    template = template.replace("__COURSE_DATA_INJECTION_POINT__", "COURSE data")
    return template


def apply_color_tokens(template: str, brand: dict) -> str:
    """Replace the Tailwind config brand.* colors with the brand profile's hex
    values. The original template uses PT PP's palette as defaults; we override
    every occurrence of the hex codes in the Tailwind config + the CSS rules."""
    color_map = {
        "#2B73BD":   "#" + brand.get("primary", "2B73BD"),         # primary
        "#205c99":   "#" + brand.get("primaryHover", "205c99"),    # primaryHover
        "#5A89B8":   "#" + brand.get("secondary", "5A89B8"),       # secondary
        "#7eabd9":   "#" + brand.get("secondaryLight", "7eabd9"),  # secondaryLight
        "#38BDF8":   "#" + brand.get("accent", "38BDF8"),          # lightBlue / accent
        "#F0F4F7":   "#" + brand.get("iceBg", "F0F4F7"),           # iceBg
        "#09111E":   "#" + brand.get("darkBg", "09111E"),          # darkBg
        "#111C2E":   "#" + brand.get("darkSurface", "111C2E"),    # darkSurface
        "#1F2F4A":   "#" + brand.get("darkBorder", "1F2F4A"),      # darkBorder
        "#16233B":   "#" + brand.get("darkSubtle", "16233B"),      # darkSubtle
    }
    for old, new in color_map.items():
        template = template.replace(old, new)
    return template


def apply_placeholders(template: str, content: dict, brand: dict) -> str:
    """Replace all __*__ placeholder strings in template with concrete values
    from content + brand."""
    course = content.get("course", {})

    placeholders = {
        "__COURSE_TITLE__":         course.get("title", "Untitled Module"),
        "__COURSE_CODE__":           course.get("code", ""),
        "__COURSE_EFFECTIVE_DATE__": course.get("effectiveDate", ""),
        "__COURSE_LOGO__":           course.get("logo", ""),
        "__COURSE_LOGO_ALT__":      course.get("logoAlt", course.get("title", "")),
        "__COURSE_TITLE_TEXT__":     course.get("title", ""),
        "__COURSE_CODE2__":          course.get("code", ""),
        "__COURSE_RESOURCES_DESC__": "",
        "__GLOSSARY_SEARCH_PLACEHOLDER__": "Cari istilah...",
        "__CERT_BRAND_NAME__":      brand.get("orgName", ""),
        "__CERT_DIVISION__":        brand.get("orgDivision", ""),
        "__CERT_SIGNATORY__":       brand.get("signatory", ""),
        "__CERT_TITLE__":           brand.get("certTitle", "Standard Operating Procedure"),
        "__CERT_REG_PREFIX__":      brand.get("certRegPrefix", "REG"),
    }
    for k, v in placeholders.items():
        template = template.replace(k, v)
    return template


def main():
    ap = argparse.ArgumentParser(description="E-Learning Module Builder")
    ap.add_argument("--content", required=True, help="Path to content.json")
    ap.add_argument("--output", required=True, help="Path to write final HTML")
    ap.add_argument("--brand-preset", default=None, help="Override brand.preset (ptpp|corporate|education|tech-startup|custom)")
    ap.add_argument("--skill-root", default=None, help="Path to skill root (default: this script's parent)")
    ap.add_argument("--validate", action="store_true", default=False, help="Run validate_content.py before building")
    ap.add_argument("--no-validate", dest="validate", action="store_false")
    args = ap.parse_args()

    # Resolve skill root
    script_dir = Path(__file__).parent.resolve()
    skill_root = Path(args.skill_root) if args.skill_root else script_dir.parent
    template_path = skill_root / "assets" / "shell.template.html"
    schema_path = skill_root / "assets" / "content.schema.json"
    profiles_path = skill_root / "assets" / "brand.profiles.json"
    validator_path = skill_root / "scripts" / "validate_content.py"

    # Load inputs
    content_path = Path(args.content).resolve()
    if not content_path.exists():
        print(f"ERROR: content.json not found at {content_path}", file=sys.stderr)
        sys.exit(1)

    content = load_json(content_path)

    # Optional validation
    if args.validate and validator_path.exists():
        import subprocess
        print(f"Validating {content_path} against schema...")
        result = subprocess.run([sys.executable, str(validator_path), str(content_path), str(schema_path)],
                                capture_output=True, text=True, encoding="utf-8", errors="replace")
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr, file=sys.stderr)
            print("Validation failed. Aborting.", file=sys.stderr)
            sys.exit(1)

    # Ensure brand block exists
    if "brand" not in content:
        content["brand"] = {"preset": "ptpp"}

    # Load brand profiles
    profiles = load_json(profiles_path)
    # Remove _comment key
    profiles = {k: v for k, v in profiles.items() if not k.startswith("_")}

    # Resolve final brand
    brand = resolve_brand(content, profiles, args.brand_preset)

    # Load template
    if not template_path.exists():
        print(f"ERROR: shell.template.html not found at {template_path}", file=sys.stderr)
        sys.exit(1)
    template = template_path.read_text(encoding="utf-8")

    # Step 1: Inject COURSE object literal
    print("Step 1: Injecting COURSE data...")
    template = inject_course_data(template, content)

    # Step 2: Apply brand color tokens
    print(f"Step 2: Applying brand color tokens (preset: {brand.get('preset', 'custom')})...")
    template = apply_color_tokens(template, brand)

    # Step 3: Apply all __*__ placeholders
    print("Step 3: Replacing placeholders...")
    template = apply_placeholders(template, content, brand)

    # Verify no placeholders left
    leftover = re.findall(r"__[A-Z_]+__", template)
    if leftover:
        print(f"WARN: Unfilled placeholders remain: {set(leftover)}", file=sys.stderr)

    # Write output
    out_path = Path(args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(template, encoding="utf-8")
    print(f"\n✓ Built module: {out_path}")
    print(f"  Size: {len(template):,} chars, {template.count(chr(10)) + 1:,} lines")
    print(f"  Brand: {brand.get('preset', 'custom')} ({brand.get('orgName', '—')})")
    print(f"  Slides: {len(content.get('slides', []))}")
    print(f"  Units:  {len(content.get('units', []))}")


if __name__ == "__main__":
    main()
