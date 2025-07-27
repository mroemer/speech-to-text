import ffmpeg
from pathlib import Path
from prefect import task

@task
def convert_aac_to_wav(aac_path: str, wav_path: str) -> str:
    ffmpeg.input(aac_path).output(
        wav_path,
        format='wav',
        acodec='pcm_s16le',
        ac=1,
        ar='16000'
    ).overwrite_output().run()
    return wav_path
