
# [.Blox](../../README.md) > [Maya](./maya.md) > Tools

## General

### Colorizer
Colorize objects using [material design colors](https://material.io/design/color/the-color-system.html#tools-for-picking-colors)  
![img](./img/colorizer.png)  

Applies to `display layers`, `objects` and the `outliner`
###### Run

```python
from dotbloxmaya import colorizer

colorizer.dock.show()
```

### Pivoting
Move the pivot relative to the bounding box  
![img](./img/pivoting.png)

###### Run

```python

from dotbloxmaya.general import pivoting

pivoting.dock.show()
```

## Modeling

### Beveler
Edit bevel history on the selected mesh.  

![img](./img/beveler.png)

###### Run

```python
from dotbloxmaya import beveler

beveler.dock.show()
````

### .Modeling
One window for primatives, mirrorer and pivoting  
![img](./img/dotmodeling.png)

###### Run

```python

from dotbloxmaya.modeling import dotmodeling

dotmodeling.dock.show()
````

### Mirrorer 
Mirror geometry across the `world pivot`, `object pivot` or the `bounding box`  
![img](./img/mirror.png)

###### Run

```python
from dotbloxmaya import mirrorer

mirrorer.dock.show()
```

### Primatives
Create a primitive at the selected components  
Optionally select a face and move the selected objects  
![img](./img/primatives.png)

###### Run

```python
from dotbloxmaya import primitives

primitives.dock.show()
```