#!/usr/bin/env python3
"""article.md → 公众号富文本 HTML 转换器（零依赖）。

用法：python3 md2wechat.py <article.md 路径>
输出：同目录 article_wechat.html，浏览器打开后一键复制，粘贴进公众号编辑器。
源 md 不做任何修改；md 是唯一事实源，改稿后重跑本脚本即可。

支持的语法子集与 SKILL.md 排版规范一致：
  ## 小标题 / **加粗** / > 引用块 / --- 分割线 / - 列表 / [配图：描述]
"""
import html
import re
import sys
from pathlib import Path

# 品牌色（与模板体系一致：tech 墨绿）
ACCENT = "#1E5C4F"
INK = "#1F2421"
SUB = "#6F7368"
BG_SOFT = "#F6F3EC"

S = {
    "p": f"margin:22px 0;font-size:16px;line-height:1.85;letter-spacing:0.6px;color:{INK};text-align:justify;",
    "h2": (
        f"margin:44px 0 22px;font-size:20px;font-weight:800;line-height:1.5;color:{ACCENT};"
        f"border-left:4px solid {ACCENT};padding-left:12px;letter-spacing:1px;"
    ),
    "quote": (
        f"margin:26px 0;padding:14px 18px;background:{BG_SOFT};border-left:4px solid {ACCENT};"
        f"font-size:15px;line-height:1.8;color:{SUB};letter-spacing:0.5px;"
    ),
    "strong": f"color:{ACCENT};font-weight:700;",
    "hr": "margin:36px 0;border:none;border-top:1px dashed #C9C5B9;",
    "ul": "margin:22px 0;padding-left:24px;",
    "li": f"margin:8px 0;font-size:16px;line-height:1.8;letter-spacing:0.6px;color:{INK};",
    "img_ph": (
        "margin:26px 0;padding:18px;border:2px dashed #B8B4A8;border-radius:8px;"
        f"text-align:center;font-size:14px;color:#9A9D90;letter-spacing:1px;"
    ),
}


def extract_body(md: str) -> str:
    """取 `# 正文` 到下一个一级标题之间的内容。"""
    lines = md.splitlines()
    out, inside = [], False
    for ln in lines:
        if re.match(r"^#\s+正文\s*$", ln):
            inside = True
            continue
        if inside and re.match(r"^#\s+\S", ln):
            break
        if inside:
            out.append(ln)
    if not out:
        sys.exit("错误：未找到『# 正文』一节")
    return "\n".join(out).strip()


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", rf'<strong style="{S["strong"]}">\1</strong>', text)
    return text


def convert(body: str) -> str:
    blocks = re.split(r"\n\s*\n", body)
    parts = []
    for blk in blocks:
        blk = blk.strip()
        if not blk:
            continue
        lines = blk.splitlines()
        if blk == "---":
            parts.append(f'<hr style="{S["hr"]}"/>')
        elif m := re.match(r"^\[配图[:：](.+)\]$", blk):
            parts.append(
                f'<section style="{S["img_ph"]}">🖼 在此插入配图：{html.escape(m.group(1))}（插入后删除本占位块）</section>'
            )
        elif blk.startswith("## "):
            parts.append(f'<h2 style="{S["h2"]}">{inline(blk[3:].strip())}</h2>')
        elif all(l.lstrip().startswith(">") for l in lines):
            text = " ".join(l.lstrip()[1:].strip() for l in lines)
            parts.append(f'<blockquote style="{S["quote"]}">{inline(text)}</blockquote>')
        elif all(l.lstrip().startswith("- ") for l in lines):
            items = "".join(f'<li style="{S["li"]}">{inline(l.lstrip()[2:])}</li>' for l in lines)
            parts.append(f'<ul style="{S["ul"]}">{items}</ul>')
        else:
            parts.append(f'<p style="{S["p"]}">{inline(" ".join(l.strip() for l in lines))}</p>')
    return "\n".join(parts)


PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>公众号富文本 · {name}</title>
<style>
  body {{ margin:0; background:#EDEBE4; font-family:-apple-system,"PingFang SC",sans-serif; }}
  .toolbar {{ position:sticky; top:0; background:{ink}; color:#fff; padding:14px 24px;
             display:flex; align-items:center; gap:16px; z-index:9; }}
  .toolbar button {{ background:{accent}; color:#fff; border:none; border-radius:6px;
                    padding:10px 22px; font-size:15px; cursor:pointer; }}
  .toolbar span {{ font-size:13px; opacity:.75; }}
  .paper {{ max-width:578px; margin:32px auto 80px; background:#fff; padding:32px 28px;
           box-shadow:0 4px 24px rgba(0,0,0,.08); }}
</style>
</head>
<body>
<div class="toolbar">
  <button onclick="copyAll()">复制全文</button>
  <span>点按钮 → 到公众号编辑器 Cmd+V 粘贴 → 在占位块处插入配图。本文件由 article.md 生成，改稿请改 md 后重跑脚本。</span>
</div>
<div class="paper"><section id="content">
{content}
</section></div>
<script>
function copyAll() {{
  const el = document.getElementById('content');
  const range = document.createRange();
  range.selectNodeContents(el);
  const sel = window.getSelection();
  sel.removeAllRanges();
  sel.addRange(range);
  const ok = document.execCommand('copy');
  sel.removeAllRanges();
  document.querySelector('.toolbar button').textContent = ok ? '已复制 ✓' : '复制失败，请手动全选';
}}
</script>
</body>
</html>
"""


def main():
    if len(sys.argv) != 2:
        sys.exit("用法：python3 md2wechat.py <article.md 路径>")
    src = Path(sys.argv[1])
    md = src.read_text(encoding="utf-8")
    out = src.parent / "article_wechat.html"
    out.write_text(
        PAGE.format(name=src.parent.name, content=convert(extract_body(md)), ink=INK, accent=ACCENT),
        encoding="utf-8",
    )
    print(f"已生成：{out}")


if __name__ == "__main__":
    main()
