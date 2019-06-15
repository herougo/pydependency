import os
import json

def load_json_if_exists(path):
    if not os.path.isfile(path):
        return {}
    with open(filename) as f:
        return json.load(f)

def get_folder_paths(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]


def file_to_lines(file_path):
    if len(file_path) == 0:
        return []
    with open(file_path) as f:
        lines = list(f.read().splitlines())
    return lines


def file_to_repo_path(file_path):
    folder_path = os.path.abspath(os.path.join(file_path, os.pardir))
    for i in range(100):
        if folder_path == '/':
            return None
        if '.git' in os.listdir(folder_path):
            break
        folder_path = os.path.abspath(os.path.join(folder_path, os.pardir))
    return folder_path
