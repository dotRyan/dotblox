# Setup


## Installation
Eventually there will be a script to install by drag and drop, but for now it is 
manual process.
  
1. Copy `maya/dotblox.mod` to `$MAYA_APP_DIR/modules`
2. Replace `{path}` with the folder path of the repository  (i.e. `<your_path>/dotblox`) 
 
You can print the path running this in the script editor
```python
import os
print(os.path.join(os.environ["MAYA_APP_DIR"], "modules"))
```

## Structure
Following mayas tools most should fit into the same categories  

- general
- modeling
- rendering
- animation
- rigging
- fx
