import os
from pydependency.utils import get_folder_paths, load_json_if_exists, file_to_lines
from pydependency.code_repo import CodeRepo

class DependencyFinder:
    '''
    config_folder folder structure:
    - code_repos/<folder>: folders representing repos
    - default.json (names go through this first when resolving dependencies; if there
      it is in there, use that; otherwise, try everywhere else)
    - packages.txt (contains package names (e.g. 'os'))

    TODO:
    Integrate current repo
    Refactor getitem
    '''
    def __init__(self, config_folder):
        self._config_folder = config_folder
        self._current_repo = None
        if not os.path.exists(config_folder):
            os.makedirs(config_folder)
        self._code_repos = [CodeRepo(config_path) for config_path in get_folder_paths(config_folder)]
        self._default_map = load_json_if_exists(os.path.join(config_folder, 'default.json'))
        self._packages = file_to_lines(os.path.join(config_folder, 'packages.txt'))

    def add_repo(self, base_path):
        base_name = os.path.basename(base_path)
        repo_config_path = os.path.join(self._config_folder, base_name)
        add_directory(repo_config_path)
        self._code_repos.append(CodeRepo(repo_config_path, base_path))

    def set_current_repo(self, repo_path):
        if self._current_repo == repo_path:
            return
        self._current_repo = repo_path

        # ???????
        pass

    def migrate_to_default(self, python_file_path):
        # ?????
        pass

    def __getitem__(self, item):
        split = item.split('.')
        if len(split) > 1:
            if split[0] in self._packages:
                return AbsoluteImport(split[0])
            # (try current repo)
        else:
            yo = self._default_map.get(item)
            # (try current repo)
            # (try self._code_repos)

    def transform_import_star(self, import_str):
        # ????
        pass
