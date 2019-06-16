import os
from pydependency.code_repo import CodeRepo, CodeFile
from tests.utils import EXAMPLE_FILES_PATH

# cr = CodeRepo('not_created_yet', GIT_REPO_PATH)

print()

path = os.path.join(EXAMPLE_FILES_PATH, 'example1.py')
expected_undefined_names = 'do_stuff yu ClassNotDefinedYet other_function_not_defined_yet i.dont.exist'.split()

cf = CodeFile(path)
global_names = cf.get_global_names()
undefined_name_data = list(iter(cf.iter_undefined_names()))
undefined_names = [x[0] for x in undefined_name_data]
assert undefined_names == expected_undefined_names
print()
