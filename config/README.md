# How the Configuration File Structure Works

### Config Folder Structure

- **code_repos/\<folder\>**: folders representing understood repos
- **default_import_mappings (READ ONLY)**: folder containing where to check first to resolve dependencies
  - files starting with 'absolute_': absolute import mappings
  - files starting with 'relative': relative import mappings
- **migrate_from**: folder with python files which can be used to migrate to mapping files in the
  default_import_mappings folder structure
Note: if a file is in an ignored folder, it will not be used in migration

### Default Import Mappings

- These configuration files are tab-separated (.tsv) files which come in 2 formats:

  - **files starting with `absolute_`**: contain absolute import names (with optional as name as the "second column")
    - e.g. `keras` line representing `import keras`
    - e.g. `tensorflow  tf` line representing ` import tensorflow as tf` 
  - **files starting with `relative_`**: contain relative import names with locations
    - e.g. `defaultdict	collections` line representing `from collections import defaultdict`

### Code Repo Configuration Folders

- When a repo is "added", pydependency parses the code in the repo and stores a folder of configuration files.

  - **config.json**: contains generic config information like the absolute path to the source repository
  - **absolute_import_set.json**: a json list of names for the repository where you're allowed to absolute import
  
    - e.g. for the numpy library, this list would contain `"numpy"` since you can do `import numpy`.
  
  - **relative_import_map.json**: dict mapping names (you can relatively import from the repo) to a list of relative python file paths containing that importable name.
  
    - e.g. if `"module_not_exists": ["test.completion.usages.py"]` is in the dictionary, that means you can do `from test.completion.usages import module_not_exists`

### Adding Code Repos

(in the main README.md)

### Adding Default Mappings

- If you know what you're doing and you maintain the proper format, you can modify/add files in the `default_import_mappings` folder
- A safer way is migrating dependencies from python files.

### Migrating Python Files to Default Import Mappings

1. Add a python file(s) into the `config/migrate_from` folder.
2. (Optional) move undesired python files to the ignored folder.
3. Run `scripts/migrate_all.py`.
  - This will look at all python files in`config/migrate_from` (except those in the ignored folder), and generate relative and absolute mapping files in `config/default_import_mappings`.
  - e.g. `config/migrate_from/built_in.py` will result in generating:
    - `config/default_import_mappings/relative_built_in.tsv`
    - `config/default_import_mappings/absolute_built_in.tsv`