import os
import warnings
from pydependency.utils import GIT_REPO_PATH, file_to_lines
from pydependency.parse_tree import ParseTreeWrapper, AbsoluteImportWrapper
from pydependency.code_repo import CodeRepo

CONFIG_PATH = os.path.join(GIT_REPO_PATH, 'config')
CONFIG_CODE_REPOS_PATH = os.path.join(CONFIG_PATH, 'code_repos')
CONFIG_DEFAULT_IMPORT_MAPPINGS_PATH = os.path.join(CONFIG_PATH, 'default_import_mappings')
CONFIG_MIGRATE_FROM_PATH = os.path.join(CONFIG_PATH, 'migrate_from')
ABSOLUTE_PREFIX = 'absolute_'
RELATIVE_PREFIX = 'relative_'


class ConfigProcessor:
    '''
    config_folder folder structure:
    - code_repos/<folder>: folders representing understood repos
    - (READ ONLY) default_import_mappings: folder containing where to check first to resolve dependencies
      - files starting with 'absolute_': absolute import mappings
      - files starting with 'relative': relative import mappings
    - migrate_from: folder with python files which can be used to migrate to mapping files in the
      default_import_mappings folder structure
    Note: if a file is in an ignored folder, it will not be used by ConfigProcessor
    '''
    @classmethod
    def _tsv_to_matrix(cls, path):
        lines = file_to_lines(path)
        return [line.split('\t') for line in lines]

    @classmethod
    def _matrix_to_tsv(cls, matrix, path):
        text = '\n'.join(['\t'.join(row) for row in matrix])
        with open(path, 'w') as f:
            f.write(text)

    @classmethod
    def _iter_used_tsv_rows(cls, prefix):
        for f in os.listdir(CONFIG_DEFAULT_IMPORT_MAPPINGS_PATH):
            path = os.path.join(path, f)
            if os.path.isfile(path) and f.endswith('.tsv') and f.startswith(prefix):
                matrix = cls._tsv_to_matrix(path)
                for row in matrix:
                    yield f, row

    @classmethod
    def read_relative_mappings(cls):
        '''
        :return: dict mapping used_name -> (import_name, import_location)
        '''
        mapping = {}
        for f, row in ConfigProcessor._iter_used_tsv_rows(RELATIVE_PREFIX):
            if len(row) == 3 and row[0].strip() != '': # as case
                as_name, original_name, import_location = row
                mapping[as_name] = (original_name, import_location)
            elif len(row) == 2 and row[0].strip() != '':
                original_name, import_location = row
                mapping[original_name] = (original_name, import_location)
            else:
                warnings.warn('Unhandled relative {} tsv row: {}'.format(f, row))
        return mapping

    @classmethod
    def read_absolute_mappings(cls):
        '''
        :return: dict mapping used_name -> import_location
        '''
        mapping = {}
        for f, row in ConfigProcessor._iter_used_tsv_rows(ABSOLUTE_PREFIX):
            if len(row) == 2 and row[0].strip() != '':  # as case
                as_name, import_location = row
                mapping[as_name] = import_location
            elif len(row) == 1 and row[0].strip() != '':
                mapping[row[0]] = row[0]
            else:
                warnings.warn('Unhandled absolute {} tsv row: {}'.format(f, row))
        return mapping

    @classmethod
    def write_absolute_mappings(cls, mapping, path):
        matrix = [([import_location] if used_name == import_location else [used_name, import_location])
                  for used_name, import_location in mapping.items()]
        cls._matrix_to_tsv(matrix, path)

    @classmethod
    def write_relative_mappings(cls, mapping, path):
        matrix = [(import_name, import_location) if used_name == import_name
                   else (used_name, import_name, import_location)
                  for (used_name, (import_name, import_location)) in mapping.items()]
        cls._matrix_to_tsv(matrix, path)

    @classmethod
    def _append_to_mappings_with_file(cls, relative_import_mapping, absolute_import_mapping, path, f):
        tree = ParseTreeWrapper(file_path=path, need_unused_names=False)
        for imp in tree.iter_global_import():
            if isinstance(imp, AbsoluteImportWrapper):
                if imp.used_name in absolute_import_mapping.keys():
                    warnings.warn('Naming conflict from {} with name {} from {}'.format(
                        f, imp.used_name, str(imp)))
                absolute_import_mapping[imp.used_name.strip()] = imp.import_location.strip()
            else:
                for name in imp.names:
                    if name in relative_import_mapping.keys():
                        warnings.warn('Naming conflict from {} with name {} from {}'.format(
                            f, imp.used_name, str(imp)))
                    relative_import_mapping[name.strip()] = (name.strip(), imp.import_location.strip())

    @classmethod
    def build_migrate_from_mappings(cls):
        relative_import_mapping = {}
        absolute_import_mapping = {}
        for f in os.listdir(CONFIG_MIGRATE_FROM_PATH):
            path = os.path.join(CONFIG_MIGRATE_FROM_PATH, f)
            if os.path.isfile(path) and f.endswith('.py'):
                cls._append_to_mappings_with_file(cls, relative_import_mapping, absolute_import_mapping, path, f)

        return relative_import_mapping, absolute_import_mapping

    @classmethod
    def migrate_all(cls):
        '''
        Migrate everything from 'migrate_from' directory to 'default_import_mappings' on a file by file basis.
        Example: migrate_from/basic.py
                  -> default_import_mappings/relative_basic.tsv and default_import_mappings/absolute_basic.tsv
        '''
        for f in os.listdir(CONFIG_MIGRATE_FROM_PATH):
            path = os.path.join(CONFIG_MIGRATE_FROM_PATH, f)
            if os.path.isfile(path) and f.endswith('.py'):
                name = f[:-3]
                relative_import_mapping = {}
                absolute_import_mapping = {}
                cls._append_to_mappings_with_file(relative_import_mapping, absolute_import_mapping, path, f)
                if len(absolute_import_mapping) > 0:
                    ConfigProcessor.write_absolute_mappings(
                        absolute_import_mapping, path=os.path.join(CONFIG_DEFAULT_IMPORT_MAPPINGS_PATH,
                                                                   '{}{}.tsv'.format(ABSOLUTE_PREFIX, name)))
                if len(relative_import_mapping) > 0:
                    ConfigProcessor.write_relative_mappings(
                        relative_import_mapping, path=os.path.join(CONFIG_DEFAULT_IMPORT_MAPPINGS_PATH,
                                                                   '{}{}.tsv'.format(RELATIVE_PREFIX, name)))


    @classmethod
    def load_code_repo_config(cls):
        '''
        :return: dict mapping repo_name -> CodeRepo object
        '''
        config_code_repo_dirs = [f for f in os.listdir(CONFIG_CODE_REPOS_PATH)
                                 if os.path.isdir(os.path.join(CONFIG_CODE_REPOS_PATH, f))]
        code_repos_map = {f: CodeRepo(os.path.join(CONFIG_CODE_REPOS_PATH, f))
                          for f in config_code_repo_dirs}
        return code_repos_map
