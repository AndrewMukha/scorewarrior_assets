import shutil
import subprocess
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List


class AbstractZipService(ABC):
    @abstractmethod
    def create_zip(self, zip_path: Path, files: List[Path]) -> None:
        pass

class ZipService(AbstractZipService):
    def create_zip(self, zip_path: Path, files: list[Path]) -> None:
        with zipfile.ZipFile(zip_path, "w") as zip_file:
            for file in files:
                zip_file.write(file, file.name)


class SevenZipService(AbstractZipService):
    def __init__(self) -> None:
        if shutil.which("7z") is None:
            raise RuntimeError("7zip is not installed or not in PATH.")

    def create_zip(self, zip_path: Path, files: List[Path]) -> None:
        try:
            file_list = " ".join(str(file) for file in files)
            command = f"7z a -tzip -slp -mx1 -bd -bt {str(zip_path)} {file_list}".split()
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error creating 7z archive: {e}")
