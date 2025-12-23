from prefect import task
from pathlib import Path
import yaml

speaker_name_file = Path("conf/speaker_names.yml")

@task
def merge_segments(all_segments: list, output_path: str):
    flat = [s for sublist in all_segments for s in sublist]
    flat.sort(key=lambda x: x["start"])

    with open(output_path, "w", encoding="utf-8") as f:
        for s in flat:
            # skip common artifacts
            if s['text'] == ' Vielen Dank.':
                continue

            # use speaker names instead of Discord ID
            speaker_name = {}
            if speaker_name_file.exists():
                with speaker_name_file.open("r", encoding="utf-8") as fh:
                    speaker_name = yaml.safe_load(fh) or {}
            speaker = speaker_name.get(s["speaker"], s["speaker"])

            ts = f"{s['start']:.2f}-{s['end']:.2f}"
            f.write(f"[{ts}] {speaker}:{s['text']}\n")
