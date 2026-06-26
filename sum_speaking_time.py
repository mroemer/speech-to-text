#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path

import yaml

speaker_name_file = Path("conf/speaker_names.yml")

def human_duration(seconds: float) -> str:
    seconds = round(seconds, 3)

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remaining = int(seconds % 60)

    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")

    if remaining or not parts:
        if remaining == int(remaining):
            parts.append(f"{int(remaining)}s")
        else:
            parts.append(f"{remaining:.3f}s")

    return " ".join(parts)


def speaker_from_filename(path: Path) -> str:
    """
    Extracts speaker from filenames like:
      1-_jannybunny.json -> jannybunny
      2-fox.json         -> fox
    """
    stem = path.stem
    match = re.match(r"^\d+-(.+)$", stem)
    speaker = match.group(1) if match else stem
    return speaker.lstrip("_")


def total_seconds_and_words_for_file(path: Path) -> tuple[float, int]:
    with path.open("r", encoding="utf-8") as handle:
        segments = json.load(handle)

    total = 0.0
    word_count = 0

    for index, segment in enumerate(segments):
        try:
            start = float(segment["start"])
            end = float(segment["end"])
        except KeyError as exc:
            raise ValueError(f"{path}: segment {index} missing {exc}") from exc

        duration = end - start
        if duration < 0:
            raise ValueError(
                f"{path}: segment {index} has negative duration: "
                f"start={start}, end={end}"
            )
        
        if str(segment.get("text", "")).strip() == "Vielen Dank.":
            continue

        total += duration
        word_count += len(segment.get("text", "").split())

    return total, word_count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sum speaking time per speaker from Whisper-style JSON files."
    )
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="JSON files, one per speaker, named like 1-_jannybunny.json",
    )
    parser.add_argument(
        "--sort",
        choices=["time", "speaker", "file"],
        default="time",
        help="Sort output by total time, speaker, or filename. Default: time.",
    )

    args = parser.parse_args()

    rows = []
    grand_total = 0.0

    for path in args.files:
        seconds, word_count = total_seconds_and_words_for_file(path)
        grand_total += seconds

        rows.append(
            {
                "file": path.name,
                "speaker": speaker_from_filename(path),
                "seconds": seconds,
                "word_count": word_count,
            }
        )

    if args.sort == "time":
        rows.sort(key=lambda row: row["seconds"], reverse=True)
    elif args.sort == "speaker":
        rows.sort(key=lambda row: row["speaker"].casefold())
    elif args.sort == "file":
        rows.sort(key=lambda row: row["file"].casefold())


    print(f"{'Speaker':<24} {'Time':>14} {'Seconds':>9} {'Words':>8} {'Share':>8}")
    print("-" * 67)

    for row in rows:
        if speaker_name_file.exists():
            with speaker_name_file.open("r", encoding="utf-8") as fh:
                speaker_name = yaml.safe_load(fh) or {}
        speaker = speaker_name.get(row["speaker"], row["speaker"])

        share = row["seconds"] / grand_total * 100 if grand_total else 0.0
        print(
            f"{speaker:<24} "
            f"{human_duration(row['seconds']):>14} "
            f"{int(row['seconds']):>9} "
            f"{row['word_count']:>8} "
            f"{share:>7.2f}%"
        )

    print("-" * 67)
    print(
        f"{'TOTAL':<24} "
        f"{human_duration(grand_total):>14} "
        f"{int(grand_total):>9} "
        f"{sum(row['word_count'] for row in rows):>8} "
        f"{100.00:>7.2f}%"
    )


if __name__ == "__main__":
    main()