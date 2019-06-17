import os
from tests.utils import EXAMPLE_FILES_PATH
from pydependency.dependency_finder import DependencyFinder
from pydependency.utils import *

df = DependencyFinder()
path = '/home/henri/Documents/Git/jedi/jedi'
df.set_current_repo(get_repo_path(path))

script_lookup = df['Script']
sorted_definitions_lookup = df['jedi.api.helpers.sorted_definitions']
tf_lookup = df['tf']
tf_var_lookup = df['tf.Variable']

path = os.path.join(EXAMPLE_FILES_PATH, 'resolve_dependencies_example.py')
df.set_current_file(path)
assert df._current_code_file._tree._jedi_interpreter is not None
header = df.extract_missing_dependency_header()

print()