# Changelog

All notable changes to this project will be documented in this file.

## [1.2.0] - 2024-11-13

### Added

- Added `editconfig` command to edit the config file with the specified editor (default is nano).

### Changed

- Updated the `create` command to copy to folder within folder.
- Updated the `update` command to be compatible with the `create` command and made it more aggregated
- Removed unused modules

## [1.1.0] - 2024-11-12

### Added

- Added `info` command to display additional information about specific commands and their features.
- Added `list` command to list all items in the configuration.

### Changed

- Updated the `create` command to allow adding both regular files and folders.
- Replaced the `recreate` command with the `update` function, which now updates files instead of rewriting them entirely.

## [1.0.0] - 2024-11-10

### Added

- Initial release with basic functionality for managing dotfiles with `create`, `recreate`, and `list` commands.
