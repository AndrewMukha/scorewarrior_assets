import hashlib
import json
import shutil
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from toolbox.image_processor import AbstractImageProcessor, RotateDirection
from toolbox.zip_service import AbstractZipService


class AbstractAsset(ABC):
    def __init__(self, image_path: Path) -> None:
        self.image_path = image_path

    @abstractmethod
    def build(self, output_dir: Path, zip_service: AbstractZipService) -> None:
        pass

    @abstractmethod
    def get_hash(self) -> str:
        pass

    @abstractmethod
    def get_files(self) -> List[Path]:
        pass

    def get_zip_path(self, output_dir: Path) -> Path:
        return output_dir / f"{self.get_hash()}.zip"


class SoloImage(AbstractAsset):
    def build(self, output_dir: Path, zip_service: AbstractZipService) -> None:
        zip_service.create_zip(self.get_zip_path(output_dir), [self.image_path])

    def get_files(self) -> List[Path]:
        return [self.image_path]

    def get_hash(self) -> str:
        with open(self.image_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()


class Bundle(AbstractAsset):
    def __init__(
        self,
        image_path: Path,
        json_path: Path,
        image_processor: AbstractImageProcessor,
    ) -> None:
        super().__init__(image_path)
        self.json_path = json_path
        self.image_processor = image_processor

    def build(self, output_dir: Path, zip_service: AbstractZipService) -> None:
        rotated_image_path = self._process_image()
        if rotated_image_path:
            zip_service.create_zip(
                self.get_zip_path(output_dir),
                [rotated_image_path, self.json_path],
            )

    def get_files(self) -> List[Path]:
        return [self.image_path, self.json_path]

    def _process_image(self) -> Optional[Path]:
        with open(self.json_path, "r") as f:
            config = json.load(f)

        rotate_value = config.get("rotate", "none").lower()
        direction = next(
            (d for d in RotateDirection if d.value == rotate_value),
            RotateDirection.NONE,
        )

        temp_dir = tempfile.gettempdir()
        copied_image_path = Path(temp_dir) / self.image_path.name
        shutil.copy(self.image_path, copied_image_path)

        rotated_image = self.image_processor.rotate_image(
            copied_image_path, direction
        )
        if not rotated_image:
            return None

        if copied_image_path.suffix.lower() == ".jpg":
            rotated_image_path = copied_image_path.with_suffix(".png")
        else:
            rotated_image_path = copied_image_path

        rotated_image.save(rotated_image_path)

        return rotated_image_path

    def get_hash(self) -> str:
        with open(self.image_path, "rb") as img_file, open(
            self.json_path, "rb"
        ) as json_file:
            hasher = hashlib.md5()
            hasher.update(img_file.read())
            hasher.update(json_file.read())
            return hasher.hexdigest()
