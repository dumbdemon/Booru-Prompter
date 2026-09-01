import yaml
import folder_paths

#todo:

with open(folder_paths.get_user_directory() / "default" / "BooruPrompter" / "settings.yaml", "r") as file:
    config = yaml.safe_load(file)
