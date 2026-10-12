#!/usr/bin/env python3
"""
validate_content.py — Schema Validator for E-Learning Module content.json

USAGE
  python3 validate_content.py <content.json> [schema.json]

Default schema path: ../assets/content.schema.json (relative to this script).

Exit codes:
  0 = valid
  1 = invalid (errors printed to stderr)
  2 = missing dependencies (jsonschema not installed)
"""
import json
import sys
from pathlib import Path

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema package not installed. Run: pip install jsonschema", file=sys.stderr)
    sys.exit(2)


def main():
    if len(sys.argv) < 2:
        print("USAGE: validate_content.py <content.json> [schema.json]", file=sys.stderr)
        sys.exit(1)
    content_path = Path(sys.argv[1])
    if not content_path.exists():
        print(f"ERROR: content.json not found: {content_path}", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) >= 3:
        schema_path = Path(sys.argv[2])
    else:
        schema_path = Path(__file__).parent.parent / "assets" / "content.schema.json"

    if not schema_path.exists():
        print(f"ERROR: schema not found: {schema_path}", file=sys.stderr)
        sys.exit(1)

    try:
        content = json.loads(content_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"✗ Invalid schema JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate
    validator = jsonschema.Draft7Validator(schema)
    errors = list(validator.iter_errors(content))

    if not errors:
        # Cross-field consistency check: units.length == slides.length
        units = content.get("units", [])
        slides = content.get("slides", [])
        if len(units) != len(slides):
            print(f"✗ Cross-field error: units.length ({len(units)}) != slides.length ({len(slides)})", file=sys.stderr)
            sys.exit(1)
        # Course totalUnits should match
        total_units = content.get("course", {}).get("totalUnits")
        if total_units is not None and total_units != len(units):
            print(f"✗ course.totalUnits ({total_units}) != units.length ({len(units)})", file=sys.stderr)
            sys.exit(1)

        print(f"✓ Valid! {len(units)} units, {len(slides)} slides.")
        # Quick stats
        type_counts = {}
        for s in slides:
            t = s.get("type", "?")
            type_counts[t] = type_counts.get(t, 0) + 1
        for t, n in sorted(type_counts.items()):
            print(f"  {t}: {n}")
        sys.exit(0)
    else:
        print(f"✗ {len(errors)} validation error(s):", file=sys.stderr)
        for i, err in enumerate(errors[:20], 1):
            # Build a path string
            path = "/".join(str(p) for p in err.absolute_path) or "<root>"
            print(f"  [{i}] {path}: {err.message}", file=sys.stderr)
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
