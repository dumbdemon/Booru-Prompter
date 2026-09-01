import yaml
import folder_paths

# todo:

base_path = folder_paths.get_user_directory() / "default" / "BooruPrompter"

with open(base_path / "settings.yaml", "r") as file:
    config = yaml.safe_load(file)
