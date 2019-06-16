import os
from tests.utils import EXAMPLE_FILES_PATH
from pydependency.dependency_finder import DependencyFinder
from pydependency.utils import *

df = DependencyFinder()
path = '/home/henri/Documents/Git/jedi/jedi'
df.set_current_repo(file_to_repo_path(path))

script_lookup = df['Script']
sorted_definitions_lookup = df['jedi.api.helpers.sorted_definitions']
tf_lookup = df['tf']

path = os.path.join(EXAMPLE_FILES_PATH, 'resolve_dependencies_example.py')


print()