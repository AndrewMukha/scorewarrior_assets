from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Optional

from PIL import Image


class RotateDirection(Enum):
    NONE = "none"
    LEFT = "left"
    RIGHT = "right"


ROTATION_ANGLES = {
    RotateDirection.LEFT: 90,
    RotateDirection.RIGHT: -90,
    RotateDirection.NONE: 0,
}


class AbstractImageProcessor(ABC):
    @abstractmethod
    def rotate_image(
        self, image_path: Path, direction: RotateDirection
    ) -> Optional[Image.Image]:
        pass


class PillowImageProcessor(AbstractImageProcessor):
    def rotate_image(
        self, image_path: Path, direction: RotateDirection
    ) -> Optional[Image.Image]:
        try:
            image = Image.open(image_path)
            angle = ROTATION_ANGLES.get(direction, 0)
            if angle:
                image = image.rotate(angle, expand=True)
            return image.convert("RGBA")
        except Exception as e:
            print(f"Error rotating image {image_path}: {e}")
            return None
