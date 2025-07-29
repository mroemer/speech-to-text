# Speech-to-Text Pipeline

A Prefect-based pipeline to extract and merge transcripts from zipped AAC files.

Transcripts are created using [Whisper by OpenAI](https://openai.com/index/whisper/) and filtered with Voice Activation Detection using [Silero VAD](https://github.com/snakers4/silero-vad).

## Usage

1. Activate the `venv`

   ```sh
   source .venv/bin/activate
   ```

2. Install Python dependencies

   ```sh
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Run the pipeline

   ```sh
   PYTHONPATH=. python flows/combined_transcription_flow.py inputs/aac_files.zip --whisper_model medium
   ```
