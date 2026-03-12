#!/bin/bash
# 构建可分发的 macOS 成品（内置 Python 运行时）

set -euo pipefail

APP_NAME="ChatFilter"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DIST_DIR="$PROJECT_DIR/dist"
PYINSTALLER_SPEC="$PROJECT_DIR/packaging/pyinstaller/ChatFilterBinary.spec"
XCODE_PROJECT="$PROJECT_DIR/ui/ChatFilter.xcodeproj"
STAMP="$(date +%Y%m%d-%H%M%S)"
BUILD_ROOT="$PROJECT_DIR/build/release-$STAMP"
DERIVED_DATA_DIR="$BUILD_ROOT/xcode"
RELEASE_DIR="$DIST_DIR/release-$STAMP"
APP_BUILD_PATH="$DERIVED_DATA_DIR/Build/Products/Release/${APP_NAME}.app"
APP_RELEASE_PATH="$RELEASE_DIR/${APP_NAME}.app"
DMG_STAGE_DIR="$BUILD_ROOT/dmg"
DMG_PATH="$RELEASE_DIR/${APP_NAME}.dmg"
ZIP_PATH="$RELEASE_DIR/${APP_NAME}.zip"
FIRST_LAUNCH_NOTE="$PROJECT_DIR/packaging/First Launch Instructions.txt"
export PYINSTALLER_CONFIG_DIR="$BUILD_ROOT/pyinstaller-config"

mkdir -p "$BUILD_ROOT"
mkdir -p "$RELEASE_DIR"
mkdir -p "$PYINSTALLER_CONFIG_DIR"

echo "==> Building bundled CLI binary with PyInstaller"
python3 -m PyInstaller "$PYINSTALLER_SPEC" \
  --noconfirm \
  --clean \
  --distpath "$DIST_DIR" \
  --workpath "$BUILD_ROOT/pyinstaller"

if [[ ! -x "$DIST_DIR/ChatFilterBinary/ChatFilterBinary" ]]; then
  echo "错误: PyInstaller 产物不存在: $DIST_DIR/ChatFilterBinary/ChatFilterBinary"
  exit 1
fi

echo "==> Building SwiftUI app bundle"
xcodebuild \
  -project "$XCODE_PROJECT" \
  -scheme "$APP_NAME" \
  -configuration Release \
  -derivedDataPath "$DERIVED_DATA_DIR" \
  CODE_SIGNING_ALLOWED=NO \
  build

if [[ ! -d "$APP_BUILD_PATH" ]]; then
  echo "错误: Xcode 未生成 app bundle: $APP_BUILD_PATH"
  exit 1
fi

echo "==> Copying release app"
ditto "$APP_BUILD_PATH" "$APP_RELEASE_PATH"

echo "==> Creating ZIP archive"
ditto -c -k --sequesterRsrc --keepParent "$APP_RELEASE_PATH" "$ZIP_PATH"

echo "==> Preparing DMG staging folder"
mkdir -p "$DMG_STAGE_DIR"
ditto "$APP_RELEASE_PATH" "$DMG_STAGE_DIR/${APP_NAME}.app"
ln -s /Applications "$DMG_STAGE_DIR/Applications"
cp "$FIRST_LAUNCH_NOTE" "$DMG_STAGE_DIR/"

echo "==> Creating DMG archive"
if hdiutil create \
  -volname "$APP_NAME" \
  -srcfolder "$DMG_STAGE_DIR" \
  -ov \
  -format UDZO \
  "$DMG_PATH"; then
  DMG_STATUS="ok"
else
  DMG_STATUS="failed"
  echo "警告: DMG 创建失败，已保留 APP 和 ZIP 成品。"
fi

echo
echo "构建完成:"
echo "APP: $APP_RELEASE_PATH"
echo "ZIP: $ZIP_PATH"
if [[ "${DMG_STATUS:-failed}" == "ok" ]]; then
  echo "DMG: $DMG_PATH"
fi
