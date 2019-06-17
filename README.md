# pydependency

A repo (and sublime plugin) for automatically extracting missing python depencies.


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