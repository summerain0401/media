#!/bin/bash
# 用法: render.sh <文件夹> —— 渲染文件夹内所有 .html 为同名 .png
# 尺寸从文件名读取：name_2350x1000.html → 2350x1000；无标记默认 1800x1013（公众号文内 16:9 横图）
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [ ! -x "$CHROME" ]; then echo "未找到 Chrome: $CHROME" >&2; exit 1; fi
DIR=$(cd "$1" && pwd) || exit 1
for f in "$DIR"/*.html; do
  [ -e "$f" ] || continue
  base=$(basename "$f" .html)
  size=$(echo "$base" | grep -oE '[0-9]{3,4}x[0-9]{3,4}$')
  [ -z "$size" ] && size=1800x1013
  w=${size%x*}; h=${size#*x}
  out="${f%.html}.png"
  "$CHROME" --headless --disable-gpu --hide-scrollbars --window-size=$w,$h --screenshot="$out" "file://$f" 2>/dev/null
  echo "rendered: $out ($size)"
done
