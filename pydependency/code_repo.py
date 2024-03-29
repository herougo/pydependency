import collections
import os
from pydependency.parse_tree import ParseTreeWrapper, AbsoluteImportWrapper, RelativeImportWrapper
from pydependency.utils import load_json_if_exists, file_to_lines, LineNumberTracker, json_dump
from pydependency.config import CONFIG_CODE_REPOS_PATH

class CodeFile:
    '''
    WARNING: start_pos and end_pos are not reliable if you modified the file.
    '''
    def __init__(self, file_path, need_unused_names=False):
        self._file_path = file_path
        self._tree = ParseTreeWrapper(file_path, need_unused_names=need_unused_names)
        self._line_number_tracker = LineNumberTracker()

        # self._segmentation contains lines and import classes
        self._segmentation, self._import_map = self._build_code_segmentation_structure()

    def _build_code_segmentation_structure(self):
        # REFACTOR PERFORMANCE: use better data structure than a list
        segmentation = file_to_lines(self._file_path)
        import_map = {}
        for node in self.iter_global_import():
            if isinstance(node, AbsoluteImportWrapper):
                import_map[node.import_location] = node
            else:
                for name in node.names:
                    import_map[name] = node

            start = self._line_number_tracker.transform(node.start_pos[0])
            end = self._line_number_tracker.transform(node.end_pos[0])
            self._line_number_tracker.remove_lines(start, end)
            del segmentation[start:end]  # pop elements in the start:end range
            self._line_number_tracker.add_lines(start, start + 1)
            segmentation.insert(start, node)
        return segmentation, import_map


    def add_import_to_top(self, import_location):
        if import_location in self._import_map.keys():
            return
        self._segmentation.push(0, AbsoluteImportWrapper(import_location))


    def add_import_from_to_top(self, import_location, names):
        if (import_location in self._import_map.keys() and
                all([name in self._import_map[import_location].names for name in names])):
            return
        self._segmentation.push(0, RelativeImportWrapper(import_location, names))


    def add_import_from(self, import_location, name):
        if import_location in self._import_map.keys():
            self._import_map[import_location].add_name(name)

    def add_import(self, import_location):
        self.add_import_to_top(import_location)


    def iter_global_class_names(self):
        for x in self._tree.iter_global_class_names():
            yield x

    def iter_global_func_names(self):
        for x in self._tree.iter_global_func_names():
            yield x

    def iter_global_var_names(self):
        for x in self._tree.iter_global_var_names():
            yield x

    def iter_global_names(self):
        iters = [self.iter_global_var_names(), self.iter_global_func_names(), self.iter_global_class_names()]
        for it in iters:
            for x in it:
                yield x

    def iter_global_import(self):
        for x in self._tree.iter_global_import():
            yield x

    def get_global_names(self):
        # REFACTOR
        return {
            'classes': list(sorted(iter(self.iter_global_class_names()), key=lambda x: x.name)),
            'functions': list(sorted(iter(self.iter_global_func_names()), key=lambda x: x.name)),
            'variables': list(sorted(iter(self.iter_global_var_names()), key=lambda x: x.name))
        }

    def iter_undefined_names(self):
        # REFACTOR: consistent interface
        for name, start_pos, end_pos in self._tree.get_undefined_used_names():
            yield name, start_pos, end_pos

    def save(self):
        new_code = '\n'.join([str(segment) for segment in self._segmentation])
        with open(self._file_path, 'w') as f:
            f.write(new_code)

REPO_NAME = 'repo_name'
FOLDER_PATH = 'folder_path'


class CodeRepo:
    def __init__(self, config_folder, rebuild=True):
        self._config_json_path = os.path.join(config_folder, 'config.json')
        self._relative_import_map_path = os.path.join(config_folder, 'relative_import_map.json')
        self._absolute_import_set_path = os.path.join(config_folder, 'absolute_import_set.json')

        self._config_path = config_folder
        self._config = load_json_if_exists(self._config_json_path)

        folder_path = self._config.get(FOLDER_PATH)
        if folder_path is None or not rebuild:
            self._name_map = {}
            self._relative_import_map = load_json_if_exists(self._relative_import_map_path)
            self._absolute_import_set = set(load_json_if_exists(self._absolute_import_set_path))
        else:
            # REFACTOR: not recompute from scratch?
            self._build(folder_path)

    def _build(self, folder_path):
        self._config[FOLDER_PATH] = folder_path
        self._config[REPO_NAME] = os.path.basename(self._config_path)
        self._name_map = self._build_name_map()
        self._relative_import_map = self._build_relative_import_map(self._name_map)
        self._absolute_import_set = self._build_absolute_import_set()

    def save_config(self):
        if not os.path.isdir(self._config_path):
            os.makedirs(self._config_path)
        json_dump(self._config, self._config_json_path)
        json_dump(self._relative_import_map, self._relative_import_map_path)
        json_dump(list(self._absolute_import_set), self._absolute_import_set_path)

    @classmethod
    def load_from_repo_path(cls, repo_path):
        base_name = os.path.basename(repo_path)
        repo_config_path = os.path.join(CONFIG_CODE_REPOS_PATH, base_name)
        code_repo = CodeRepo(repo_config_path)
        code_repo._build(repo_path)
        return code_repo

    @property
    def repo_name(self):
        return self._config.get(REPO_NAME)

    @property
    def folder_path(self):
        return self._config.get(FOLDER_PATH)

    def _build_name_map(self):
        '''
        Builds a map that can be used to acces the CodeFiles of the repo (e.g. result['pydependency']['code_repo.py'])
        :return: dict mapping folder_name -> (dict of the same form or CodeFile object)
        '''
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

        _build_name_map_recursion(self.folder_path, result)

        return result

    def _build_relative_import_map(self, name_map):
        '''
        :param name_map: self._name_map
        :return: dict mapping name -> list of import_location values (ie 'keras.layers')
        '''
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
                for node_wrapper in node.iter_global_names():
                    result[node_wrapper.name].append(prefix)

        _build_map_recursion([], name_map)

        return result

    def _build_absolute_import_set(self):
        result = set()
        for f in os.listdir(self.folder_path):
            path = os.path.join(self.folder_path, f)
            if os.path.isdir(path):
                dir_name = os.path.basename(path)
                if os.path.isfile(os.path.join(path, '__init__.py')):
                    result.add(dir_name)
            elif os.path.isfile(path) and path.endswith('.py'):
                name = f[:-3]
                result.add(name)

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

    def iter_global_class_names(self):
        self._iter_names('iter_global_class_names')

    def iter_global_func_names(self):
        self._iter_names('iter_global_func_names')

    def iter_global_var_names(self):
        self._iter_names('iter_global_var_names')

    def iter_global_import(self):
        self._iter_names('iter_global_import')

    def get_relative_import_dependencies(self, name):
        '''
        Determine relative import dependencies for name.
        :param name: str name of a directory or name in the repo_path
        :return: list of RelativeImportWrappers of relative import statements from the repo which can load this name
        Example: 'path' -> list  with RelativeImportWrapper for 'from os import path'
        '''
        return [RelativeImportWrapper(import_location=import_location, names=[name])
                for import_location in self._relative_import_map.get(name, [])]

    def get_absolute_import_dependencies(self, name):
        '''
        Determine absolute import dependencies for name.
        :param name: str name of a directory or name in the repo_path
        :return: list of AbsoluteImportWrappers of absolute import statements from the repo which can load this name
        Example: 'path' -> list  with AbsoluteImportWrapper for 'from os import path'
        '''
        prefix = name.split('.')[0]
        return [AbsoluteImportWrapper(import_location=import_location)
                for import_location in self._absolute_import_set
                if import_location.split('.')[0] == prefix]


    def transform_import_star(self, import_str):
        # ????
        pass