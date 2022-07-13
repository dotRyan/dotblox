# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased
- [beta]: this branch has the latest changes; these commits may be overwritten.

## [2.0.2] - 2022-07-13
### Fix
- Code Wall not replacing `\\` on relative paths


## [2.0.1] - 2022-07-12
### Fix
- dobloxmaya `get_qt_fullname` cast to long on some platforms


## [2.0.0] - 2022-07-12
### New
- `Code Wall` tool for directly running snippets. Documentation to follow.

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


[beta]: https://github.com/dotRyan/dotblox/compare/master...beta
[2.0.2]: https://github.com/dotRyan/dotblox/compare/v2.0.0...v2.0.1
[2.0.1]: https://github.com/dotRyan/dotblox/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/dotRyan/dotblox/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/dotRyan/dotblox/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/dotRyan/dotblox/compare/v0.1.1...v1.0.0
[0.1.1]: https://github.com/dotRyan/dotblox/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/dotRyan/dotblox/releases/tag/v0.1.0

[Beveler]: docs/maya/tools.md#Beveler
[Colorizer]: docs/maya/tools.md#Colorizer
[Mirrorer]: docs/maya/tools.md#Mirrorer
[.Modeling]: docs/maya/tools.md#.Modeling
[Primitives]: docs/maya/tools.md#Primitives
[Pivoting]: docs/maya/tools.md#Pivoting
