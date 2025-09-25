import json
import whisper
import torch
from pathlib import Path
from prefect import task

@task
def transcribe_with_timestamps(wav_folder: str, speaker_label: str, language: str, whisper_model: str, cache_dir: str) -> list:
    segment_dir = Path(cache_dir) / (Path(wav_folder).stem)
    all_segments_file = Path(str(segment_dir) + ".json")
    if all_segments_file.exists():
        return json.loads(all_segments_file.read_text())

    wav_files = Path(wav_folder).glob('*.wav')

    model = whisper.load_model(whisper_model)
    segment_dir.mkdir(exist_ok=True, parents=True)
    all_segments = []
    for wav_file in sorted(wav_files, key=lambda f: int(f.stem)):
        offset = int(Path(wav_file).stem) / 16000
        segment_file = Path(segment_dir) / (Path(wav_file).stem + ".json")
        if segment_file.exists():
            segments = json.loads(segment_file.read_text())
            for seg in segments:
                seg["start"] = seg["start"] + offset
                seg["end"] = seg["end"] + offset
            all_segments.extend(segments)
            continue

        # disable fp16 if running on CPU
        use_fp16 = torch.cuda.is_available()
        
        result = model.transcribe(
            str(wav_file),
            language=language,
            verbose=False,
            fp16=use_fp16
        )
        segments = result["segments"]
        for seg in segments:
            seg["speaker"] = speaker_label
            seg["start"] = seg["start"] + offset
            seg["end"] = seg["end"] + offset
        segment_file.write_text(json.dumps(segments, indent=2))
        all_segments.extend(segments)
    
    all_segments_file.write_text(json.dumps(all_segments, indent=2))
    return all_segments
