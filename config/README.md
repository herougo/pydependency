# How the Configuration File Structure Works

### Config Folder Structure

- **code_repos/<folder>**: folders representing understood repos
- (READ ONLY) **default_import_mappings**: folder containing where to check first to resolve dependencies
  - files starting with 'absolute_': absolute import mappings
  - files starting with 'relative': relative import mappings
- **migrate_from**: folder with python files which can be used to migrate to mapping files in the
  default_import_mappings folder structure
Note: if a file is in an ignored folder, it will not be used in migration

### Default Import Mappings

### Code Repo Configuration Folders

- When a repo is "added", pydependency parses the code in the repo and stores a folder of configuration files.

  - **config.json**: contains generic config information like the absolute path to the source repository
  - **absolute_import_set.json**: a json list of names for the repository where you're allowed to absolute import
  
    - e.g. for the numpy library, this list would contain `"numpy"` since you can do `import numpy`.
  
  - **relative_import_map.json**: dict mapping names (you can relatively import from the repo) to a list of relative python file paths containing that importable name.
  
    - e.g. if `"module_not_exists": ["test.completion.usages.py"]` is in the dictionary, that means you can do `from test.completion.usages import module_not_exists`
    