import json
from pathlib import Path
from typing import List

import numpy as np
import soundfile as sf
import torch
from prefect import task
from scipy.signal import resample_poly


def read_audio_16k_mono(audio_path: str, sampling_rate: int = 16000) -> torch.Tensor:
    audio, source_rate = sf.read(audio_path, dtype="float32", always_2d=False)

    if audio.ndim == 2:
        audio = audio.mean(axis=1)

    if source_rate != sampling_rate:
        gcd = np.gcd(source_rate, sampling_rate)
        up = sampling_rate // gcd
        down = source_rate // gcd
        audio = resample_poly(audio, up, down).astype(np.float32)

    return torch.from_numpy(audio)


@task
def detect_voice_activity(audio_path: str, cache_dir: str) -> List[dict]:
    cache_path = Path(cache_dir) / "vad" / (Path(audio_path).stem + ".json")

    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))

    # Silero VAD is CPU-oriented and optimized for one CPU thread.
    torch.set_num_threads(1)

    vad_model, utils = torch.hub.load(
        repo_or_dir="snakers4/silero-vad",
        model="silero_vad",
        trust_repo=True,
    )

    get_speech_timestamps = utils[0]

    wav = read_audio_16k_mono(audio_path, sampling_rate=16000)

    speech_timestamps = get_speech_timestamps(
        wav,
        vad_model,
        sampling_rate=16000,
    )

    cache_path.parent.mkdir(exist_ok=True, parents=True)
    cache_path.write_text(
        json.dumps(speech_timestamps, indent=2),
        encoding="utf-8",
    )

    return speech_timestamps
