import json
import torch
from pathlib import Path
from prefect import task

@task
def detect_voice_activity(audio_path: str) -> list:
    cache_path = Path("outputs") / Path("vad") / (Path(audio_path).stem + ".json")
    if cache_path.exists():
        return json.loads(cache_path.read_text())

    # Silero VAD (voice activation detection)
    vad_model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', trust_repo=True)
    (get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

    # filter segments based on (voice activation detection)
    wav = read_audio(audio_path, sampling_rate=16000)
    speech_timestamps = get_speech_timestamps(wav, vad_model, sampling_rate=16000, return_seconds=True)
    cache_path.parent.mkdir(exist_ok=True)
    cache_path.write_text(json.dumps(speech_timestamps, indent=2))

    return speech_timestamps
