# Changelog

All notable changes to this project since v2 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Dependency `xcolor`

### Changed

- Needed LaTeX version updated to 2024-11-01
- Needed `l3kernel` version updated to 2025-03-10
- `step` tracing is disabled by default
- Unknown options now raise errors instead of being silently ignored
- More reliable `hypreref` glue code

### Deprecated

### Removed

- Removed declaration of historic v2021 release
- Removed dependency `ninecolors`

### Fixed

- `text` as hline/vline was fully expanded (lvjr/tabularray#303)
- No braces are stripped from cells (lvjr/tabularray#501, #4)
  Now to protect non-number `S`-column cells, only one pair of braces
  is needed, rather than three pairs as before.

### Security

[unreleased]: https://github.com/muzimuzhi/tabularray/compare/2024A...HEAD
