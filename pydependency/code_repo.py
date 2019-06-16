import collections
import os
from pydependency.parse_tree import ParseTreeWrapper
from pydependency.utils import load_json_if_exists, file_to_lines


class CodeFile:
    def __init__(self, file_path):
        self._file_path = file_path
        self._tree = ParseTreeWrapper(file_path)
        self._lines = file_to_lines(file_path)
        self._line_segmentation = self._segment_code()

    def _segment_code(self):
        pass

    def add_import_from(self, import_location, name):
        pass

    def add_import(self, import_location):
        pass

    def iter_global_class_names(self):
        for x in self._tree.iter_global_class_names():
            yield x

    def iter_global_func_names(self):
        for x in self._tree.iter_global_func_names():
            yield x

    def iter_global_var_names(self):
        for x in self._tree.iter_global_var_names():
            yield x

    def iter_global_import(self):
        for x in self._tree.iter_global_import():
            yield x

    def iter_undefined_names(self):
        raise NotImplementedError()

class CodeRepo:
    def __init__(self, config_folder, folder_path=None):
        if folder_path is None:
            self._config = load_json_if_exists(os.path.join(config_folder, 'config.json'))
            self._folder_path = self._config['folder_path']
        else:
            self._folder_path = folder_path
        #self._code_files = [CodeFile(file_path) for file_path in file_paths]
        # keys are folder_names and leaf values are CodeFile objects
        self._name_map = self._build_name_map()
        self._relative_import_map = self._build_relative_import_map()

    @property
    def repo_name(self):
        return os.path.basename(self._folder_path)

    def _get_python_file_paths_old(self):
        result = []
        for paths, subdirs, files in os.walk(self._folder_path):
            for file in files:
                if file.endswith('.py'):
                    pure_path = os.path.join(paths, file)
                    result.append(pure_path)
        return result

    def _build_name_map(self):
        result = {}

        def _build_name_map_recursion(folder_path, d):
            for f in os.listdir(folder_path):
                path = os.path.join(folder_path, f)
                if os.path.isdir(path):
                    dir_name = os.path.basename(path)
                    if os.path.isfile(os.path.join(path, '__init__.py')):
                        d[dir_name] = {}
                        _build_name_map_recursion(path, d[dir_name])
                elif os.path.isfile(path) and path.endswith('.py'):
                    file_name = os.path.basename(path)
                    d[file_name] = CodeFile(path)

        _build_name_map_recursion(self._folder_path, result)

        return result

    def _build_relative_import_map(self):
        result = collections.defaultdict(list)

        def _build_map_recursion(prefix_list, node):
            if isinstance(node, dict):
                for k, v in node.items():
                    _build_map_recursion(prefix_list + [k], v)
            else:
                if prefix_list[-1] == '__init__.py':
                    prefix = '.'.join(prefix_list[:-1])
                else:
                    prefix = '.'.join(prefix_list)
                for name in node.iter_names():
                    self._relative_import_map[name].append(prefix)

        _build_map_recursion([], result)

        return result

    def _iter_names(self, func_name):
        def _iter_names_recursion(prefix_list, node):
            if isinstance(node, dict):
                for k, v in node.items():
                    _iter_names_recursion(prefix_list + [k], v)
            else:
                if prefix_list[-1] == '__init__.py':
                    prefix = '.'.join(prefix_list[:-1])
                else:
                    prefix = '.'.join(prefix_list)
                for name in getattr(node, func_name)():
                    yield '{}.{}'.format(prefix, name)
        _iter_names_recursion([], self._name_map)

    def iter_class_names(self):
        # iter_classdefs
        self._iter_names('iter_class_names')

    def iter_function_names(self):
        # iter_funcdefs
        self._iter_names('iter_function_names')

    def iter_global_var_names(self):
        self._iter_names('iter_global_var_names')

    def iter_imports(self):
        # iter_imports
        pass

    def get_relative_import_dependencies(self, name):
        '''
        Input: name of a directory or name in the repo_path
        Output: relative import statements from the repo which can load this name
        Example: 'path' -> ['from os import path']
        '''
        self._relative_import_map[name]

    def transform_import_star(self, import_str):
        # ????
        pass