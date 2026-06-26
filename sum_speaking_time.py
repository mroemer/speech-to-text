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
        parts.append(f"{hours:>2}h")
    if minutes or hours:
        parts.append(f"{minutes:>2}m")

    if remaining or not parts:
        if remaining == int(remaining):
            parts.append(f"{int(remaining):>2}s")
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
    
    # merge rows by speaker
    merged_rows = {}
    for row in rows:
        speaker = row["speaker"]
        if speaker not in merged_rows:
            merged_rows[speaker] = row
            merged_rows[speaker]["sessions"] = 1
        else:
            merged_rows[speaker]["seconds"] += row["seconds"]
            merged_rows[speaker]["word_count"] += row["word_count"]
            merged_rows[speaker]["sessions"] += 1
    rows = list(merged_rows.values())

    if args.sort == "time":
        rows.sort(key=lambda row: row["seconds"], reverse=True)
    elif args.sort == "speaker":
        rows.sort(key=lambda row: row["speaker"].casefold())
    elif args.sort == "file":
        rows.sort(key=lambda row: row["file"].casefold())


    print(f"{'Speaker':<16} {'Time':>11} {'Seconds':>9} {'Words':>7} {'Share':>7} {'Sessions':>8}")
    print("-" * 63)

    for row in rows:
        if speaker_name_file.exists():
            with speaker_name_file.open("r", encoding="utf-8") as fh:
                speaker_name = yaml.safe_load(fh) or {}
        speaker = speaker_name.get(row["speaker"], row["speaker"])

        share = row["seconds"] / grand_total * 100 if grand_total else 0.0
        print(
            f"{speaker:<16} "
            f"{human_duration(row['seconds']):>11} "
            f"{int(row['seconds']):>9} "
            f"{row['word_count']:>7} "
            f"{share:>6.1f}% "
            f"{row['sessions']:>8}"
        )

    print("-" * 63)
    print(
        f"{'TOTAL':<16} "
        f"{human_duration(grand_total):>11} "
        f"{int(grand_total):>9} "
        f"{sum(row['word_count'] for row in rows):>7} "
        f"{100.0:>6.1f}% "
        f"{max(row['sessions'] for row in rows):>8}"
    )


if __name__ == "__main__":
    main()