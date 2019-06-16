import os

PYTHON_VERSION = '3.6'
MAX_LINE_LEN = 100
PYTHON_SPACING = ' ' * 4

GIT_REPO_PATH = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),  # pydependency folder
    os.pardir))
CONFIG_PATH = os.path.join(GIT_REPO_PATH, 'config')
CONFIG_CODE_REPOS_PATH = os.path.join(CONFIG_PATH, 'code_repos')
CONFIG_DEFAULT_IMPORT_MAPPINGS_PATH = os.path.join(CONFIG_PATH, 'default_import_mappings')
CONFIG_MIGRATE_FROM_PATH = os.path.join(CONFIG_PATH, 'migrate_from')