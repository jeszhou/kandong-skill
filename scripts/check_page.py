#!/usr/bin/env python3
"""检查 kandong 生成的页面：必需的区块都在、模板占位字已替换、结论够短。

用法：python3 check_page.py <页面.html>
全部通过输出 OK，退出码 0；有错误逐条列出，退出码 1。提醒（WARN）不影响退出码。
"""
import re
import sys
from html.parser import HTMLParser

REQUIRED = ["kd-conclusion", "kd-map", "kd-concepts", "kd-details", "kd-source"]
PLACEHOLDERS = ["第一句结论。", "读者问题", "问题一", "概念 A", "细节一。", "原文全文", "全局图说明"]
MAX_CONCLUSION_SENTENCES = 3
MAX_SENTENCE_CHARS = 40  # 结论里的单句上限（只数汉字和字母数字）


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.stack = []  # 当前所在的区块 id
        self.text = {k: [] for k in REQUIRED + ["kd-decide", "svg", "dt", "title"]}
        self.in_tag = None
        self.external_scripts = []
        self.svg_in_map = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "section" and a.get("id"):
            self.stack.append(a["id"])
        if tag == "svg" and self.stack and self.stack[-1] == "kd-map":
            self.svg_in_map = True
        if tag == "script" and a.get("src"):
            self.external_scripts.append(a["src"])
        if tag in ("svg", "dt", "title"):
            self.in_tag = tag

    def handle_endtag(self, tag):
        if tag == "section" and self.stack:
            self.stack.pop()
        if tag == self.in_tag:
            self.in_tag = None

    def handle_data(self, data):
        if self.stack and self.stack[-1] in self.text:
            self.text[self.stack[-1]].append(data)
        if self.in_tag:
            self.text[self.in_tag].append(data)


def sentences(text):
    return [s for s in re.split(r"[。！？!?\n]", text) if s.strip()]


def visible_len(s):
    return len(re.findall(r"[一-鿿A-Za-z0-9]", s))


def main(path):
    html = open(path, encoding="utf-8").read()
    p = Page()
    p.feed(html)
    errors, warns = [], []

    for sid in REQUIRED:
        if sid not in p.ids:
            errors.append(f"缺少区块 #{sid}")
    if "kd-map" in p.ids and not p.svg_in_map:
        errors.append("#kd-map 里没有内联 SVG 全局图")
    body = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    for ph in PLACEHOLDERS:
        if ph in body:
            errors.append(f"模板占位字没替换：「{ph}」")
    if "".join(p.text["title"]).strip() == "标题":
        errors.append("<title> 还是「标题」")
    for src in p.external_scripts:
        errors.append(f"引用了外部脚本 {src}，页面要能离线打开")

    concl = sentences("".join(p.text["kd-conclusion"]).replace("结论", "", 1))
    if len(concl) > MAX_CONCLUSION_SENTENCES:
        errors.append(f"结论有 {len(concl)} 句，最多 {MAX_CONCLUSION_SENTENCES} 句")
    for s in concl:
        if visible_len(s) > MAX_SENTENCE_CHARS:
            warns.append(f"结论这句偏长（{visible_len(s)} 字）：{s.strip()[:30]}…")

    svg_text = "".join(p.text["svg"])
    for name in (t.strip() for t in p.text["dt"]):
        if name and name not in svg_text:
            warns.append(f"概念「{name}」没出现在全局图里，确认图里没用别的叫法")

    for w in warns:
        print("WARN", w)
    if errors:
        for e in errors:
            print("ERROR", e)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
