from pathlib import Path
import folder_paths


class PathManager:
    def __init__(self):
        # Base Paths
        self.ext_path = Path(__file__).resolve().parent.parent.parent.parent
        self.user_path = Path(folder_paths.get_user_directory())

        # Special Paths
        self.user_path = self.user_path / "default" / "BooruPrompter"

        # Make Directories
        self._mkdir()

    def _mkdir(self) -> None:
        for config in [self.user_path]:
            config.mkdir(parents=True, exist_ok=True)

    def get_user_path(self, filename: str) -> Path:
        return self.user_path / filename

    def get_pyproject(self) -> Path:
        return self.ext_path / "pyproject.toml"
