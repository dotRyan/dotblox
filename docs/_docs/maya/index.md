---
title: Setup
---

# Installation

## The Easy Way
To install into `$MAYA_APP_DIR/modules`

##### Run 
```python
from dotbloxmaya import bootstrap
bootstrap.install()
```

Restart Maya

!!! note
Make sure you follow the instructions on the [Welcome Page](../index.md#installation)

## The Hard Way

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
