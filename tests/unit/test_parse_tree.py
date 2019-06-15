'''

defined_class_functions = ['Large.adder', 'Large.say_hi']
defined_functions = ['my_func', 'func', 'unused_func']
import_statements = [
    'import sort', 'from sort.bad import *', 'from sorting import There', 'import yes.good.hello'
]

used_global_variables = defined_global_variables
used_classes = ['Large', 'Hi', 'Empty']
used_functions = ['my_func', 'func']
used_imported_variables = [
    'yes.good.hello.hi', 'sort.bell', 'There', 'ClassNotDefinedYet', 
    'ClassNotDefinedYet.function_not_defined_yet', 'other_function_not_defined_yet'
]

used_imported_variables = [
    'yes.good.hello.hi', 'sort.bell', 'There', 'ClassNotDefinedYet', 
    'ClassNotDefinedYet.function_not_defined_yet', 'other_function_not_defined_yet'
]

'''

'''
from pydependency.dependency_finder import DependencyFinder
from pydependency.utils import *
df = DependencyFinder('/Users/hromel/dependency_finder')
df.set_current_repo(file_to_repo_path(current_file_path))
df['functions.low_detail_search.main']
'''

from pydependency.parse_tree import ParseTreeWrapper
from tests.utils import iter_example_files


for path in iter_example_files():
    tree = ParseTreeWrapper(file_path=path)
    defined_global_variables = ['YU', 'MODIFIED_TWICE', 'MODIFIED_TWICE', 'USED_BY_CLASS_1', 'USED_BY_CLASS_2']
    defined_classes = ['Large', 'Hi', 'Empty', 'UnusedClass']
    data = {}
    data['class'] = list(iter(tree.iter_global_class_names()))
    data['func'] = list(iter(tree.iter_global_func_names()))
    data['global_var'] = list(iter(tree.iter_global_var_names()))
    data['import'] = list(iter(tree.iter_global_import()))

    #assert defined_global_variables == data['global_var']
    #assert defined_classes == data['class']
    print()