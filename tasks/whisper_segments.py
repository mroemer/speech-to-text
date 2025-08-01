import json
import whisper
from pathlib import Path
from prefect import task


@task
def transcribe_with_timestamps(audio_path: str, speaker_label: str, language: str, whisper_model: str, cache_dir: str) -> list:
    cache_path = Path(cache_dir) / (Path(audio_path).stem + ".json")
    if cache_path.exists():
        return json.loads(cache_path.read_text())

    model = whisper.load_model(whisper_model)
    result = model.transcribe(audio_path, language=language, verbose=False)
    segments = result["segments"]
    for seg in segments:
        seg["speaker"] = speaker_label
    cache_path.write_text(json.dumps(segments, indent=2))
    return segments
