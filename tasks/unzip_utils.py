from zipfile import ZipFile
from pathlib import Path
from prefect import task

@task
def unzip_aac_files(zip_path: str, extract_to: str) -> list:
    Path(extract_to).mkdir(parents=True, exist_ok=True)
    with ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    return sorted([str(f) for f in Path(extract_to).glob("*.aac")])
