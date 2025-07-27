from prefect import flow
from tasks.unzip_utils import unzip_aac_files
from tasks.audio_conversion import convert_aac_to_wav
from tasks.whisper_segments import transcribe_with_timestamps
from tasks.transcript_merger import merge_segments
from pathlib import Path

@flow
def full_stt_pipeline(zip_file: str,
                      language: str = "de",
                      extract_dir: str = "inputs/unzipped",
                      output_path: str = "outputs/final_transcript.txt",
                      whisper_model: str = "medium"):
    aac_files = unzip_aac_files(zip_file, extract_dir)
    all_segments = []

    for aac_file in aac_files:
        speaker = Path(aac_file).stem.split("-")[1].replace("_", "").replace(".", "")
        wav_file = aac_file.replace(".aac", ".wav")
        wav_path = convert_aac_to_wav(aac_file, wav_file)
        segments = transcribe_with_timestamps(wav_path, speaker, language, whisper_model)
        all_segments.append(segments)

    merge_segments(all_segments, output_path)
    print(f"Transcript saved to {output_path}")

if __name__ == "__main__":
    full_stt_pipeline("inputs/aac_files.zip")
