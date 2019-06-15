import os

GIT_REPO_PATH = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),  # tests folder
    os.pardir))
EXAMPLE_FILES_PATH = os.path.join(os.path.join(GIT_REPO_PATH, 'tests'), 'example_files')

def iter_example_files():
    for f in os.listdir(EXAMPLE_FILES_PATH):
        if f.endswith('.py'):
            yield os.path.join(EXAMPLE_FILES_PATH, f)