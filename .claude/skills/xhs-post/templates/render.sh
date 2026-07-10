#!/bin/bash
# 用法: render.sh <文件夹>  —— 将文件夹内所有 .html 渲染为同名 .png (1242x1656, 小红书 3:4)
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [ ! -x "$CHROME" ]; then echo "未找到 Chrome: $CHROME" >&2; exit 1; fi
DIR=$(cd "$1" && pwd) || exit 1
for f in "$DIR"/*.html; do
  [ -e "$f" ] || continue
  out="${f%.html}.png"
  "$CHROME" --headless --disable-gpu --hide-scrollbars --window-size=1242,1656 --screenshot="$out" "file://$f" 2>/dev/null
  echo "rendered: $out"
done
