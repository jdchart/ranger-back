import os
import json

def check_dir_exists(filepath):
    """Check if folder exists, if not, create it."""
    if os.path.isdir(os.path.dirname(filepath)) == False:
        os.makedirs(os.path.dirname(filepath))

def write_json(path : str, content : dict, indent : int = 4) -> None:
    """
    Write to json. Will create folder if doesn't exist.
    """
    if os.path.splitext(path)[1] == ".json":
        check_dir_exists(path)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii = False, indent = indent)
    else:
        print(f"{path} needs to be a json file.")