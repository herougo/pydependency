import os
from pydependency.config import GIT_REPO_PATH

EXAMPLE_FILES_PATH = os.path.join(os.path.join(GIT_REPO_PATH, 'tests'), 'example_files')

def iter_example_files():
    for f in os.listdir(EXAMPLE_FILES_PATH):
        if f.endswith('.py'):
            yield os.path.join(EXAMPLE_FILES_PATH, f)