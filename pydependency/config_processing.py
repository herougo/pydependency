import os
import warnings
from pydependency.utils import GIT_REPO_PATH, file_to_lines
from pydependency.parse_tree import ParseTreeWrapper, AbsoluteImportWrapper, RelativeImportWrapper

CONFIG_PATH = os.path.join(GIT_REPO_PATH, 'config')
_CONFIG_IMPORT_MAPPINGS_PATH = os.path.join(CONFIG_PATH, 'default_import_mappings')
CONFIG_ABSOLUTE_IMPORT_MAPPINGS_PATH = os.path.join(_CONFIG_IMPORT_MAPPINGS_PATH, 'absolute')
CONFIG_RELATIVE_IMPORT_MAPPINGS_PATH = os.path.join(_CONFIG_IMPORT_MAPPINGS_PATH, 'relative')
CONFIG_MIGRATE_FROM_PATH = os.path.join(CONFIG_PATH, 'migrate_from')


class ConfigProcessor:
    '''

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
    def _iter_used_tsv_rows(cls, path):
        for f in os.listdir(path):
            path = os.path.join(path, f)
            if os.path.isfile(path) and f.endswith('.tsv'):
                matrix = cls._tsv_to_matrix(path)
                for row in matrix:
                    yield f, row

    @classmethod
    def read_relative_mappings(cls):
        '''
        :return: dict mapping used_name -> (import_name, import_location)
        '''
        mapping = {}
        for f, row in ConfigProcessor._iter_used_tsv_rows(CONFIG_RELATIVE_IMPORT_MAPPINGS_PATH):
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
        for f, row in ConfigProcessor._iter_used_tsv_rows(CONFIG_ABSOLUTE_IMPORT_MAPPINGS_PATH):
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
    def build_migrate_from_mappings(cls):
        relative_import_mapping = {}
        absolute_import_mapping = {}
        for f in os.listdir(CONFIG_MIGRATE_FROM_PATH):
            path = os.path.join(CONFIG_MIGRATE_FROM_PATH, f)
            if os.path.isfile(path) and f.endswith('.py'):
                tree = ParseTreeWrapper(file_path=path, need_unused_names=False)
                for imp in tree.iter_global_import():
                    if isinstance(imp, AbsoluteImportWrapper):
                        if imp.used_name in absolute_import_mapping.keys():
                            warnings.warn('Naming conflict from {} with name {} from {}'.format(
                                f, imp.used_name, str(imp)))
                        absolute_import_mapping[imp.used_name] = imp.import_location
                    else:
                        for name in imp.names:
                            if name in relative_import_mapping.keys():
                                warnings.warn('Naming conflict from {} with name {} from {}'.format(
                                    f, imp.used_name, str(imp)))
                            relative_import_mapping[name] = imp.import_location
