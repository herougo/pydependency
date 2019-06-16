import argparse
from pydependency.config_processing import ConfigProcessor


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('relative_import_output_path')
    parser.add_argument('absolute_import_output_path')
    args = parser.parse_args()
    return args.absolute_import_output_path, args.relative_import_output_path


if __name__ == '__main__':
    absolute_import_output_path, relative_import_output_path = get_args()
    relative_import_mapping, absolute_import_mapping = ConfigProcessor.build_migrate_from_mappings()
    ConfigProcessor.write_absolute_mappings(absolute_import_mapping, absolute_import_output_path)
    ConfigProcessor.write_relative_mappings(relative_import_mapping, relative_import_output_path)
    print('Done!')
