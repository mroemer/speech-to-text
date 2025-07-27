import json
import torch
import numpy as np
from pathlib import Path
from prefect import task

# Silero VAD (voice activation detection)
vad_model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', trust_repo=True)
(get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

@task
def filter_with_vad(audio_path: str, segments: list) -> list:
    cache_path = Path("outputs") / Path("vad_filtered") / (Path(audio_path).stem + ".json")
    if cache_path.exists():
        return json.loads(cache_path.read_text())

    # filter segments based on (voice activation detection)
    wav = read_audio(audio_path, sampling_rate=16000)
    speech_timestamps = get_speech_timestamps(wav, vad_model, sampling_rate=16000)
    speech_ts_set = set()
    for ts in speech_timestamps:
        start = round(ts['start'] / 16000, 1)
        end = round(ts['end'] / 16000, 1)
        for i in np.arange(start, end, 0.1):
            speech_ts_set.add(i)
    cleaned_segments = []
    for seg in segments:
        seg_midpoint = round((seg["start"] + seg["end"]) / 2, 1)
        seg["midpoint"] = seg_midpoint
        if seg_midpoint in speech_ts_set:
            cleaned_segments.append(seg)
    cache_path.parent.mkdir(exist_ok=True)
    cache_path.write_text(json.dumps(cleaned_segments, indent=2))

    return cleaned_segments
