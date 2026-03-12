import os
import shutil
from pathlib import Path

def save_upload_file(upload_file, destination: Path):
    with destination.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return destination
