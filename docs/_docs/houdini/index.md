---
title: Setup
---

# Installation

## The Easy Way

To install into `$HOUDINI_USER_PREF_DIR/packages` 

##### Run
```python
from dotbloxhoudini import bootstrap
bootstrap.install()
```
Restart Houdini

!!! note
Make sure you follow the instructions on the [Welcome Page](../index.md#installation)

## The Hard Way
 
1. Copy `houdini/dotblox.json` to `$HOUDINI_USER_PREF_DIR/packages`
2. Replace `{path}` with the folder path of the repository  (i.e. `<your_path>/dotblox`) 
 
You can print the path running this in a python shell
```python
import os
print(os.path.join(os.environ["HOUDINI_USER_PREF_DIR"], "packages"))
```
