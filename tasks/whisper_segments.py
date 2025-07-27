import json
import whisper
from pathlib import Path
from prefect import task

model = whisper.load_model("base")

@task
def transcribe_with_timestamps(audio_path: str, speaker_label: str) -> list:
    cache_path = Path("outputs") / (Path(audio_path).stem + ".json")
    if cache_path.exists():
        return json.loads(cache_path.read_text())

    result = model.transcribe(audio_path, verbose=False)
    segments = result["segments"]
    for seg in segments:
        seg["speaker"] = speaker_label
    cache_path.write_text(json.dumps(segments, indent=2))
    return segments
