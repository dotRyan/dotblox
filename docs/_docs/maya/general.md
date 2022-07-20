---
title: General
---

# General Maya Tools

## Code Wall
For the full docs [see here](../tools/codewall.md).

![img](../img/tools_codewall.png)  


###### Run
```python
from dotbloxmaya.general import codewall
codewall.dock.show()
```
## Colorizer
Colorize objects using [material design colors](https://material.io/design/color/the-color-system.html#tools-for-picking-colors)  

![img](../img/maya_colorizer.png)  

Applies to `display layers`, `objects` and the `outliner`
###### Run

```python
from dotbloxmaya.general import colorizer
colorizer.dock.show()
```

## Pivoting
Move the pivot relative to the bounding box  

![img](../img/maya_pivoting.png)

###### Run

```python
from dotbloxmaya.general import pivoting
pivoting.dock.show()
```