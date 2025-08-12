from pathlib import Path
from prefect import task
import torch
import torchaudio

@task
def extract_audio_segments(wav_path: str, segments_to_keep: list) -> torch.Tensor:
    raw_wav, sr = torchaudio.load(wav_path)
    wav = raw_wav.squeeze(0)

    if wav.ndim != 1:
        raise ValueError("Only mono (1D) waveforms are supported.")

    segment_wav_folder = Path(Path(wav_path).parent.parent) / Path("segments") / Path(wav_path).stem
    segment_wav_folder.mkdir(exist_ok=True, parents=True)

    for seg in sorted(segments_to_keep, key=lambda s: s["start"]):
        start = int(seg["start"])
        end = int(seg["end"])

        segment_wav_path = Path(segment_wav_folder) / Path(str(start) + ".wav")
        if segment_wav_path.exists():
            continue

        # Ensure start and end are within bounds
        if start < 0 or end > len(wav) or start >= end:
            continue  # Skip invalid segments

        segment_wav = wav[start:end]
        torchaudio.save(str(segment_wav_path), segment_wav.unsqueeze(0), sr)

    return str(segment_wav_folder)
