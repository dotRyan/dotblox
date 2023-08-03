# Changelog
All notable changes to this project will be documented in this file.  
Documentation for front facing tools can be found [here](https://dotryan.github.io/dotblox)

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased
- [beta]: this branch has the latest updates; these commits may be overwritten.

## [2.3.1]
### Fix
- [Mirrorer] not working in maya 2022
- Python 3 compatability

## [2.3.0] - 2023-04-26
### New 
- bootstrap module for installation dccs
- easy installation for houdini and maya 
- houdini show_python_panel
- config library added functions to get current environment

### Changed
- [Code Wall] houdini python panel label
- [Code Wall] config and state settings adjusted along with the dialog

### Fix
- [Code Wall] context menu showing up twice on linux
- [Code Wall] houdini execution switched to runpy

## [2.2.0] - 2022-07-21
### New
- generated docs! https://dotryan.github.io/dotblox/
- [Code Wall] has an option to remove a tabs closeable status

### Changed
- [Code Wall] moved tab order to `StateConfig`

### Fix
- [Code Wall] 
    - adjusted maya/houdini hooks to match dcc
    - general cleanup
    - double-click on folder items attempting to execute script

## [2.1.0] - 2022-07-15
### Fix
- TextEditor QPalette.All not supported
- [Code Wall] houdini code editor background not getting proper color

### New
- [Code Wall]
    - add option to disable drag and drop
    - middle mouse scrolling while alt is pressed

### Changed
- [Code Wall] file icon provider shared pixmap cache

## [2.0.2] - 2022-07-13
### Fix
- [Code Wall] not replacing `\\` on relative paths


## [2.0.1] - 2022-07-12
### Fix
- dobloxmaya `get_qt_fullname` cast to long on some platforms


## [2.0.0] - 2022-07-12
### New
- [Code Wall] tool for directly running snippets. Documentation to follow.

### Changed
- Refactored folder structure


## [1.1.0] - 2021-02-10
### New
- Icons added; `get_icon` function
- Added Axis.N for normal support
- `dotbloxlib.config` module for future tool configurations

### Changed
- [Primitives] tool can now choose axis for selected items
- `get_component_mobject` signature has changed for simplicity

### Fix
- `FlatToolButton` now highlights on hover
- `nodepath` handles underworld nodes
- remove shelve from `dotblox.mod` due to issues with local batch rendering


## [1.0.0] - 2020-05-12
### Changed
- New structure of code base
- Changed maya code base to use `maya.cmds` instead of `pymel`. This is to support a wider range of audience and to support use of the `dotblox.core`
- Run scripts have changed for [Colorizer], [Beveler] and [Mirrorer]

### New 
- [.Modeling] tool
- [Primitives] tool
- [Pivoting] tool
- Unified way of handling mayas new workspace system
- `dotbloxlib` for sharing of non dcc specific code
- `dotbloxlib.qt` for Qt related code
- Widgets `FrameWidget`, `FlatToolButton` `WidgetToolButton`

### Fixed
- `OptionVar` was always returning the default value


## [0.1.1] - 2020-03-05
### Fixed
- `Colorizer` now sets the outliner color as the raw color

## [0.1.0] - 2020-02-05
### New
- [Beveler] tool
- [Colorizer] tool
- [Mirrorer] tool


[beta]: https://github.com/dotRyan/dotblox/compare/main...beta
[2.3.0]: https://github.com/dotRyan/dotblox/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.com/dotRyan/dotblox/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/dotRyan/dotblox/compare/v2.0.2...v2.1.0
[2.0.2]: https://github.com/dotRyan/dotblox/compare/v2.0.1...v2.0.2
[2.0.1]: https://github.com/dotRyan/dotblox/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/dotRyan/dotblox/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/dotRyan/dotblox/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/dotRyan/dotblox/compare/v0.1.1...v1.0.0
[0.1.1]: https://github.com/dotRyan/dotblox/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/dotRyan/dotblox/releases/tag/v0.1.0

[Beveler]: https://dotryan.github.io/dotblox/maya/modeling/#beveler
[Colorizer]: https://dotryan.github.io/dotblox/maya/general/#colorizer
[Mirrorer]: https://dotryan.github.io/dotblox/maya/modeling/#mirrorer
[.Modeling]: https://dotryan.github.io/dotblox/maya/modeling/#modeling
[Primitives]: https://dotryan.github.io/dotblox/maya/modeling/#primatives
[Pivoting]: https://dotryan.github.io/dotblox/maya/general/#pivoting
[Code Wall]: https://dotryan.github.io/dotblox/tools/codewall/
