import whisper
from prefect import task

model = whisper.load_model("base")

@task
def transcribe_with_timestamps(audio_path: str, speaker_label: str) -> list:
    result = model.transcribe(audio_path, verbose=False)
    segments = result["segments"]
    for seg in segments:
        seg["speaker"] = speaker_label
    return segments
