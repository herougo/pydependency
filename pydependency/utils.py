import os
import json


def load_json_if_exists(path):
    if not os.path.isfile(path):
        return {}
    with open(path) as f:
        return json.load(f)

def json_dump(obj, file_path):
    with open(file_path, 'w') as f:
        json.dump(obj, f)

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


class LineNumberTracker:
    '''
    When deleting/adding lines in a file, this allows you to translate original line numbers into transformed ones,
    '''
    def __init__(self):
        self._log = []

    def transform(self, line_num):
        for is_add, start, end in self._log:
            if line_num < start:
                pass
            elif line_num < end and not is_add:
                assert False, 'Line Deleted: {} {}'.format(line_num, self._log)
            else:
                if is_add:
                    line_num += (end - start)
                else:
                    line_num -= (end - start)
        return line_num

    def remove_lines(self, start, end):
        self._log.append((False, start, end))

    def add_lines(self, start, end):
        self._log.append((True, start, end))


