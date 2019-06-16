import os
from pydependency.utils import get_folder_paths, load_json_if_exists, file_to_lines
from pydependency.code_repo import CodeRepo
from pydependency.config_processing import ConfigProcessor
from pydependency.parse_tree import AbsoluteImportWrapper, RelativeImportWrapper
from pydependency.config import CONFIG_CODE_REPOS_PATH


class DependencyFinder:
    def __init__(self):
        self._current_repo_name = None
        self._code_repos = ConfigProcessor.load_code_repo_config()
        self._config_absolute_import_mapping = ConfigProcessor.read_absolute_mappings()
        self._config_relative_import_mapping = ConfigProcessor.read_relative_mappings()

    def add_repo(self, repo_path):
        assert repo_path is not None
        base_name = os.path.basename(repo_path)
        repo_config_path = os.path.join(CONFIG_CODE_REPOS_PATH, base_name)
        if not os.path.isdir(repo_config_path):
            code_repo = CodeRepo.load_from_repo_path(repo_path)
            self._code_repos[base_name] = code_repo
            code_repo.save_config()
        else:
            # REFACTOR: Ignored for now
            pass

    def set_current_repo(self, repo_path):
        assert repo_path is not None
        base_name = os.path.basename(repo_path)
        if self._current_repo_name == base_name:
            return
        if base_name not in self._code_repos.keys():
            self.add_repo(repo_path)

        self._current_repo_name = base_name

    def __getitem__(self, name):
        '''
        Resolve dependency
        :param name: str
        :return: list of ImportWrapper objects corresponding to the recommended import statement(s)
        '''
        # try absolute import default
        import_location = self._config_absolute_import_mapping.get(name)
        if import_location is not None:
            as_name = None if name == import_location else name
            return [AbsoluteImportWrapper(import_location, as_name=as_name)]

        # try relative import default
        default_lookup = self._config_relative_import_mapping.get(name)
        if default_lookup is not None:
            import_name, import_location = default_lookup
            return [RelativeImportWrapper(import_location, [import_name])]

        # try current repo (absolute)
        if self._current_repo_name is not None:
            import_wrappers = self._code_repos[self._current_repo_name].get_absolute_import_dependencies(name)
            if len(import_wrappers) > 0:
                return import_wrappers

        # try current repo (relative
        if self._current_repo_name is not None:
            import_wrappers = self._code_repos[self._current_repo_name].get_relative_import_dependencies(name)
            if len(import_wrappers) > 0:
                return import_wrappers

        # try other repos (absolute)
        import_wrappers = []
        for repo_name, code_repo in self._code_repos.items():
            if repo_name != self._current_repo_name:
                import_wrappers.extend(code_repo.get_absolute_import_dependencies(name))
        if len(import_wrappers) > 0:
            return import_wrappers

        # try other repos (relative)
        import_wrappers = []
        for repo_name, code_repo in self._code_repos.items():
            if repo_name != self._current_repo_name:
                import_wrappers.extend(code_repo.get_relative_import_dependencies(name))

        return import_wrappers

    def transform_import_star(self, import_str):
        # ????
        pass
