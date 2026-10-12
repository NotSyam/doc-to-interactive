#!/usr/bin/env python3
"""
generate_audio.py — Edge-TTS Audio Narration Generator for Doc-to-Interactive

Reads narration scripts from a content.json (under the 'narration' key) or a
standalone narration JSON file, and generates studio-quality neural MP3 audio
files for each unit using Microsoft Edge-TTS.

USAGE:
  python scripts/generate_audio.py --content <path-to-content.json> [options]

OPTIONS:
  --content PATH        Path to content.json containing 'narration' block (or standalone narration JSON)
  --output-dir PATH     Output folder for MP3 files (default: './audio')
  --voice NAME          Voice preset: gadis, ardi, jenny, guy, or full Edge-TTS voice name
                        (default: 'gadis' / id-ID-GadisNeural)
  --rate RATE           Speech rate adjustment, e.g. '+0%', '+10%', '-5%' (default: '+0%')
  --unit INDEX          Generate only a specific unit index (e.g. '--unit 0')

EXAMPLES:
  # Generate audio for all units using default Indonesian female voice
  python scripts/generate_audio.py --content assets/sample.content.json

  # Generate using authoritative male Indonesian voice to custom folder
  python scripts/generate_audio.py --content assets/sample.content.json --voice ardi --output-dir ./dist/audio
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


# Voice Presets
VOICE_CHOICES = {
    "gadis": "id-ID-GadisNeural",      # Female, Warm & Expressive (Indonesian)
    "ardi": "id-ID-ArdiNeural",        # Male, Authoritative & Formal (Indonesian)
    "jenny": "en-US-JennyNeural",      # Female, Natural & Engaging (English)
    "guy": "en-US-GuyNeural",          # Male, Professional (English)
}


async def generate_unit_audio(unit_id: str, text: str, output_path: Path, voice: str, rate: str = "+0%"):
    import edge_tts
    print(f"[*] Generating unit_{unit_id}.mp3 ({len(text)} chars) with voice='{voice}' (rate={rate})...")
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(str(output_path))
    size_kb = output_path.stat().st_size / 1024
    print(f"    ✓ Saved: {output_path} ({size_kb:.1f} KB)")


async def run_generation(args):
    try:
        import edge_tts
    except ImportError:
        print("\n[!] Error: 'edge-tts' package is not installed.", file=sys.stderr)
        print("    Install it via pip:   pip install edge-tts", file=sys.stderr)
        print("    Or via uv:            uv pip install edge-tts\n", file=sys.stderr)
        sys.exit(1)

    content_path = Path(args.content).resolve()
    if not content_path.exists():
        print(f"[!] Error: File not found: {content_path}", file=sys.stderr)
        sys.exit(1)

    try:
        raw_data = json.loads(content_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[!] Error parsing JSON {content_path}: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract narrations: either from content.narration or top-level dict
    if isinstance(raw_data, dict) and "narration" in raw_data and isinstance(raw_data["narration"], dict):
        narrations = raw_data["narration"]
    elif isinstance(raw_data, dict) and all(isinstance(v, str) for v in raw_data.values()):
        narrations = raw_data
    else:
        print(f"[!] Error: No valid 'narration' dictionary found in {content_path}", file=sys.stderr)
        print("    Expected schema: {\"narration\": {\"0\": \"text...\", \"1\": \"text...\"}}", file=sys.stderr)
        sys.exit(1)

    if not narrations:
        print(f"[!] Warning: 'narration' block is empty in {content_path}. Nothing to generate.", file=sys.stderr)
        return

    # Determine voice
    voice_key = args.voice.lower()
    voice = VOICE_CHOICES.get(voice_key, args.voice)

    # Output directory
    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Filter targets if single unit specified
    if args.unit is not None:
        unit_key = str(args.unit)
        if unit_key not in narrations:
            print(f"[!] Error: Unit index '{unit_key}' not found in narration keys: {list(narrations.keys())}", file=sys.stderr)
            sys.exit(1)
        targets = [(unit_key, narrations[unit_key])]
    else:
        targets = list(narrations.items())

    print(f"\n🎙️ Doc-to-Interactive Audio Narration Builder")
    print(f"=============================================")
    print(f"Source JSON : {content_path.name}")
    print(f"Output Dir  : {out_dir}")
    print(f"Voice       : {voice}")
    print(f"Speed Rate  : {args.rate}")
    print(f"Total Units : {len(targets)}\n")

    success_count = 0
    for unit_id, text in targets:
        clean_text = text.strip()
        if not clean_text:
            print(f"[!] Skipping unit_{unit_id}: empty narration text.")
            continue
        out_file = out_dir / f"unit_{unit_id}.mp3"
        try:
            await generate_unit_audio(unit_id, clean_text, out_file, voice, args.rate)
            success_count += 1
        except Exception as e:
            print(f"[!] Failed to generate unit_{unit_id}.mp3: {e}", file=sys.stderr)

    print(f"\n✓ Completed: {success_count}/{len(targets)} audio files generated in {out_dir}")


def main():
    parser = argparse.ArgumentParser(description="Doc-to-Interactive Edge-TTS Narration Generator")
    parser.add_argument("--content", required=True, help="Path to content.json or narrations JSON file")
    parser.add_argument("--output-dir", default="./audio", help="Directory where MP3 files will be saved (default: ./audio)")
    parser.add_argument("--voice", default="gadis", help="Voice choice: gadis, ardi, jenny, guy, or custom voice string")
    parser.add_argument("--rate", default="+0%", help="Speed rate modifier, e.g. +0%%, +10%%, -5%%")
    parser.add_argument("--unit", default=None, help="Generate only a specific unit index (e.g. 0)")
    args = parser.parse_args()

    asyncio.run(run_generation(args))


if __name__ == "__main__":
    main()
