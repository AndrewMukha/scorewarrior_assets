import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional


class AbstractVcs(ABC):
    @abstractmethod
    def get_changed_files(self, revision: str) -> Optional[List[str]]:
        pass

    @abstractmethod
    def write_changes(self, file_path: Path) -> None:
        pass


class Git(AbstractVcs):
    def write_changes(self, file_path: Path) -> None:
        with open(file_path, "w") as file:
            subprocess.run(["git", "show"], stdout=file, stderr=subprocess.PIPE)

    def get_changed_files(self, revision: str) -> Optional[List[str]]:
        try:
            result = subprocess.run(
                [
                    "git",
                    "diff-tree",
                    "--no-commit-id",
                    "--name-only",
                    "-r",
                    revision,
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            files = result.stdout.strip().split("\n")
            return [file for file in files if file]
        except subprocess.CalledProcessError as e:
            print(f"Error getting changed files: {e}")
            return None
