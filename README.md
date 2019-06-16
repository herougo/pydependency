# pydependency

A repo (and sublime plugin) for automatically extracting missing python depencies.


# To Do

- [x] Detect undefined variables
- [ ] Finish core code
- [ ] Populate config
- [ ] Add logging functionality
- [ ] Finish Sublime Text plugin
- [ ] Work on plugin Performance
- [ ] Finish PyCharm plugin
- [ ] Edge cases:
  - [ ] as keyword in relative imports
  - [ ] Look for 'import keras.layers' when looking up default dependencies (currently only considers first
  part such as 'keras')
  - [ ] global variables used as default function parameter values
  - [ ] handle import statements in if blocks
  - [ ] Detect and account for specific python indentation pattern (ie tab, spaces, 4 spaces, etc)
- [ ] Transform relative imports into absolute
- [ ] Transform import * into specific relative import