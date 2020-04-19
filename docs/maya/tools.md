
# [.Blox](../../README.md) > [Maya](./maya.md) > Tools

## General

### Colorizer
Colorize objects using [material design colors](https://material.io/design/color/the-color-system.html#tools-for-picking-colors)  
![img](./img/colorizer.png)  

Applies to `display layers`, `objects` and the `outliner`
###### Run
```python
from dotblox.general import colorizer
colorizer.run()
```

### Pivoting
Move the pivot relative to the bounding box  
![img](./img/pivoting.png)

###### Run
```python
from dotblox.general import pivoting
pivoting.run()
```

## Modeling

### Beveler
Edit bevel history on the selected mesh.  

![img](./img/beveler.png)

###### Run
```python
from dotblox.modeling import beveler
beveler.run()
````

### Mirrorer 
Mirror geometry across the `world pivot`, `object pivot` or the `bounding box`  
![img](./img/mirror.png)

###### Run
```python
from dotblox.modeling import mirrorer
mirrorer.run()
```
