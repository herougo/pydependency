# pydependency

A repo (and sublime plugin) for automatically extracting missing python depencies.

# Sublime Package Usage

How to use this repository

1. Clone the repository
2. Install requirements in requirements.txt
3. Run `python scripts/add_repo.py path/to/repo` to add a repo for which you want pydependency to recognize dependencies (the path is the folder containing the .git file).
  If you have a folder containing multiple git repo folders, you can run `python scripts/add_repo_collection.py path/to/folder_of_repos` to add all the repos in that folder (it will ignore folders not directly containing a .git file).
4. From the root directory of the repo, run `PYTHONPATH="." FLASK_APP=app/app.py flask run -p 5001` to run the project as a flask server app.
5. Add `plugins/sublime/resolve_dependencies.py` as a Sublime plugin (copy the file ...)
6. Add a keyboard shortcut for the plugin ......
7. Run the keyboard shortcut and that's it!

# How Dependency Recommendation Works

- Decisions are based on configuration files in the `config` folder.
  - To understand how the configuration files work, check the `config/README.md` file.
- Since recommendations vary from person to person, the user can maintain a set of repos they expose to this project as well as modify the configuration files to best suit their needs.
- The core decision logic is in `DependencyFinder.__getitem__` in the `pydependency/dependency_finder.py` file.
  - First, the "default configuration" files are checked.
  - If no match is found, it searches elsewhere (e.g. sources from added repos)


# To Do

- [x] Detect undefined variables
- [x] Finish core code
- [x] Populate config
- [ ] Add logging functionality
- [ ] Finish Sublime Text plugin
- [ ] Work on plugin Performance
- [ ] Edge cases:
  - [ ] as keyword in relative imports
  - [ ] Look for 'import keras.layers' when looking up default dependencies (currently only considers first
  part such as 'keras')
  - [ ] global variables used as default function parameter values
  - [ ] handle import statements in if blocks
  - [ ] Detect and account for specific python indentation pattern (ie tab, spaces, 4 spaces, etc)
  - [ ] Handle resolving dependencies with dotted names (e.g. keras.layers)
  - [ ] Handle [sum([i]) for i in range(10)] for unused global names
- [ ] Transform relative imports into absolute
- [ ] Transform import * into specific relative import
- [ ] Finish PyCharm plugin
- [ ] Formal unit tests