# Speech-to-Text Pipeline

A Prefect-based pipeline to extract and merge transcripts from zipped AAC files.

Transcripts are created using [Whisper by OpenAI](https://openai.com/index/whisper/) after extracting speech segments with Voice Activation Detection using [Silero VAD](https://github.com/snakers4/silero-vad).

## Usage

1. Install `ffmpeg`

   ```sh
   sudo apt update
   sudo apt install ffmpeg
   ```

1. Activate the `venv`

   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```

1. Install Python dependencies

   ```sh
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

1. Run the pipeline

   ```sh
   PYTHONPATH=. python flows/combined_transcription_flow.py inputs/aac_files.zip --whisper_model medium
   ```

## Optional configuration: speaker names

By default, transcript lines are labeled with the speaker identifier produced by the pipeline (for example a Discord user ID).

You can optionally replace these identifiers with human-readable speaker names by providing a YAML configuration file at:

```
conf/speaker_names.yml
```

### Format

The file must contain a simple key-value mapping from speaker ID to display name:

```yaml
"123456789012345678": Alice
"987654321098765432": Bob
```

* Keys must match the exact speaker identifiers found in the transcript data
* Values are written verbatim into the merged transcript output

### Behavior

* If `conf/speaker_names.yml` does not exist, the pipeline falls back to using the original speaker IDs
* If a speaker ID is not present in the file, that specific entry also falls back to the original ID
