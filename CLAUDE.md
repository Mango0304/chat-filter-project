# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Chat Filter is a macOS app for filtering and exporting chat records from HTML files. It supports both CLI and GUI (SwiftUI) interfaces, with PDF/HTML export capabilities.

## Architecture

```
chat-filter-project/
├── core/                    # Python core modules
│   ├── chat_filter.py       # CLI entry point
│   ├── file_reader.py       # Large file streaming reader
│   ├── parser.py           # HTML chat parser
│   ├── matcher.py           # Keyword matching engine
│   └── exporter.py          # HTML/PDF export (uses ReportLab)
├── ui/                      # SwiftUI macOS app
│   ├── ChatFilterApp.swift  # App entry point
│   ├── FilterViewModel.swift # Business logic bridge to Python
│   └── ContentView.swift    # Main UI
├── scripts/                 # Build/generator scripts
├── packaging/pyinstaller/   # PyInstaller specs + startup wrapper
└── ui/project.yml           # XcodeGen config
```

## Build Commands

```bash
# Run tests
python3 -m pytest tests/ -v

# CLI usage
python3 -m core.chat_filter --input chat.html --keywords "关键词" --output result.pdf

# Package Python with PyInstaller (use python3 -m PyInstaller)
python3 -m PyInstaller packaging/pyinstaller/chat_filter.spec --clean

# Generate Xcode project
cd ui && xcodegen generate

# Build Xcode app
xcodebuild -project ChatFilter.xcodeproj -scheme ChatFilter -configuration Release build

# Full rebuild pipeline
python3 -m PyInstaller packaging/pyinstaller/chat_filter.spec --clean  # Rebuild Python binary
bash scripts/build_app.sh                                              # Create app bundle structure
cd ui && xcodegen generate                      # Generate Xcode project
xcodebuild -project ChatFilter.xcodeproj -scheme ChatFilter -configuration Release build
```

## Key Implementation Details

1. **PDF Export**: Uses ReportLab (not wkhtmltopdf). Chinese fonts are bundled from `resources/fonts/` directory in the project. Fonts are copied to `_internal/fonts/` during PyInstaller build.

2. **Python Packaging**: The app bundles a PyInstaller-packed Python binary with bundled Python3.framework. The build process:
   - PyInstaller creates `dist/ChatFilterBinary/` with `_internal/` containing Python framework and dependencies
   - `scripts/build_app.sh` copies this into the Xcode app bundle

3. **Swift-Python Bridge**: `FilterViewModel.swift` detects bundled Python at runtime and executes it via `Process` to run the filter logic. Falls back to system Python (`/usr/bin/python3`) in development.

4. **Frozen Detection**: Code uses `getattr(sys, 'frozen', False)` to detect if running as packaged app, adjusting font/resource paths via `sys._MEIPASS`.

5. **Large File Support**: The parser automatically switches to streaming mode for files >= 100MB. Memory usage stays constant (~100-200MB) regardless of file size.

6. **Distribution**: Fonts are bundled in the app bundle at `Contents/Resources/_internal/fonts/` to ensure cross-machine compatibility without hardcoded system paths.

## Common Tasks

- Adding new Python dependencies: Update `packaging/pyinstaller/chat_filter.spec` with the module name in `hiddenimports`
- Adding resources to bundle: Add to `datas` list in `packaging/pyinstaller/chat_filter.spec`
- Adding fonts: Copy font files to `resources/fonts/`, they will be included automatically
- Rebuilding after code changes: Run PyInstaller, then Xcode build

## Important Paths

- Bundled fonts: `resources/fonts/` (STHeiti Medium.ttc, STHeiti Light.ttc)
- App bundle fonts: `dist/ChatFilter.app/Contents/Resources/_internal/fonts/`
- Python bundled: `dist/ChatFilter.app/Contents/Resources/_internal/Python3.framework/`
