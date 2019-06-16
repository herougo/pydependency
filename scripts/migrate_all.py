'''
Migrate everything from 'migrate_from' directory to 'default_import_mappings' on a file by file basis.
'''

from pydependency.config_processing import ConfigProcessor

if __name__ == '__main__':
    ConfigProcessor.migrate_all()
    print('Done!')
