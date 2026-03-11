#!/bin/bash
# 构建 macOS App 包

set -euo pipefail

APP_NAME="ChatFilter"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DIST_DIR="$PROJECT_DIR/dist"
BUILD_DIR="$DIST_DIR/$APP_NAME.app"
STARTUP_SCRIPT="$PROJECT_DIR/packaging/pyinstaller/startup.py"

if [[ ! -d "$DIST_DIR/ChatFilterBinary" ]]; then
  echo "错误: 未找到 $DIST_DIR/ChatFilterBinary，请先运行 PyInstaller 打包。"
  exit 1
fi

# 清理旧构建
rm -rf "$BUILD_DIR"

# 创建 app bundle 结构
mkdir -p "$BUILD_DIR/Contents/MacOS"
mkdir -p "$BUILD_DIR/Contents/Resources"

# 复制打包的 Python（从现有 dist）
cp -R "$DIST_DIR/ChatFilterBinary/_internal" "$BUILD_DIR/Contents/Resources/"

# 复制 Python 可执行文件
cp "$DIST_DIR/ChatFilterBinary/ChatFilterBinary" "$BUILD_DIR/Contents/MacOS/ChatFilter"

# 复制资源文件
cp -R "$PROJECT_DIR/core" "$BUILD_DIR/Contents/Resources/"
cp "$STARTUP_SCRIPT" "$BUILD_DIR/Contents/Resources/startup.py"

# 创建 Info.plist
cat > "$BUILD_DIR/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>ChatFilter</string>
    <key>CFBundleIdentifier</key>
    <string>com.chatfilter.app</string>
    <key>CFBundleName</key>
    <string>ChatFilter</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
EOF

echo "App bundle created: $BUILD_DIR"
echo "Contents:"
ls -la "$BUILD_DIR/Contents/"
ls -la "$BUILD_DIR/Contents/MacOS/"
ls -la "$BUILD_DIR/Contents/Resources/" | head -10
