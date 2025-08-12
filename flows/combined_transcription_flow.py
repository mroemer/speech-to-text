from pathlib import Path
from prefect import flow
import argparse
import os

from tasks.unzip_utils import unzip_aac_files
from tasks.audio_conversion import convert_aac_to_wav
from tasks.whisper_segments import transcribe_with_timestamps
from tasks.detect_voice_activity import detect_voice_activity
from tasks.extract_audio_segments import extract_audio_segments
from tasks.filter_overlapping_segments import filter_overlapping_segments
from tasks.transcript_merger import merge_segments

@flow
def full_stt_pipeline(zip_file: str,
                      language: str = "de",
                      output_dir: str = "outputs",
                      whisper_model: str = "medium"):
    extract_dir = os.path.join(output_dir, "unzipped")
    aac_files = unzip_aac_files(zip_file, extract_dir)
    all_segments = []

    for aac_file in aac_files:
        speaker = Path(aac_file).stem.split("-")[1].replace("_", "").replace(".", "")
        wav_file = aac_file.replace(".aac", ".wav")
        wav_path = convert_aac_to_wav(aac_file, wav_file)
        speech_timestamps = detect_voice_activity(wav_path, cache_dir=output_dir)
        
        # remove non-speaking parts from audio file to remove transcription noise
        cleaned_wav_path = extract_audio_segments(wav_path, speech_timestamps)
        segments = transcribe_with_timestamps(cleaned_wav_path, speaker, language, whisper_model, cache_dir=output_dir)
        
        all_segments.append(segments)

    output_path = os.path.join(output_dir, "final_transcript.txt")
    merge_segments(all_segments, output_path)
    print(f"Transcript saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run speech-to-text transcription pipeline with Whisper and Silero VAD.")

    parser.add_argument("zip_file", type=str, help="Path to the input zip file containing AAC files")
    parser.add_argument("--language", type=str, default="de", help="Language to use for transcription (default: de)")
    parser.add_argument("--output_dir", type=str, default="outputs", help="Directory to save output files")
    parser.add_argument("--whisper_model", type=str, default="medium", choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper model to use (default: medium)")

    args = parser.parse_args()

    full_stt_pipeline(
        zip_file=args.zip_file,
        language=args.language,
        output_dir=args.output_dir,
        whisper_model=args.whisper_model
    )
