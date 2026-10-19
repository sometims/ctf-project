#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CTF 源码泄露 / 备份包 后门扫描器
用法:
    python backdoor_scan.py <目录或zip路径> [--top N]

功能:
    递归扫描 .php/.phtml 文件，按"危险度"给每一处可疑代码打分，
    输出文件:行号:命中规则:代码片段。
    专为"1000+ 噪声文件里找 1 个后门"这类题设计。

设计思路:
    噪声文件通常只有 json/正则/rand/date 这类安全代码；真正的后门
    一定会出现"用户输入(超全局) + 危险函数/动态调用"的组合。
    我们按规则命中加权，分数高的排在前面，省去人工翻 1000 个文件。
"""

import os
import re
import sys
import zipfile
import tempfile
import argparse
from collections import defaultdict

# 规则: (名称, 正则, 权重)
# 权重越高越危险。动态回调类(把用户输入当函数名)给最高权。
RULES = [
    # ---- 高危: 动态回调 / 代码执行 ----
    ("变量函数回调(array_filter/array_map+base64_decode)",
     r"array_(?:filter|map|walk)\s*\([^)]*,\s*(?:base64_decode|[$][A-Za-z_])", 10),
    ("create_function", r"create_function\s*\(", 10),
    ("eval/assert 执行", r"\b(?:eval|assert)\s*\(", 9),
    ("preg_replace /e 修饰符", r"preg_replace\s*\([^)]*/e", 10),
    ("base64_decode 接变量", r"base64_decode\s*\(\s*[$]", 8),
    ("变量函数调用 $(var)()", r"[$][A-Za-z_][A-Za-z0-9_]*\s*\(\s*[$]", 7),

    # ---- 中危: 直接命令/文件执行 ----
    ("system/exec 系列", r"\b(?:system|exec|shell_exec|passthru|popen|proc_open)\s*\(", 6),
    ("反引号命令执行", r"`[^`]*[\$][A-Za-z_]", 5),
    ("文件包含变量", r"\b(?:include|require|include_once|require_once)\s*\(\s*[$]", 6),
    ("读取文件到变量", r"\b(?:file_get_contents|readfile|fread|show_source|highlight_file)\s*\(\s*[$]", 5),

    # ---- 低危: 用户输入入口(单独出现也要留意) ----
    ("超全局输入 $_REQUEST/$_GET/$_POST", r"\$_(?:REQUEST|GET|POST|COOKIE|SERVER)\b", 3),
    ("反序列化", r"\b(?:unserialize)\s*\(\s*[$]", 4),
]

# 解码混淆的常见入口(单独高亮, 帮助判断是否是壳)
OBFUSC_RULES = [
    ("gzinflate", r"gzinflate\s*\("),
    ("str_rot13", r"str_rot13\s*\("),
    ("base64 长串", r"base64_decode\s*\(\s*[\"'][A-Za-z0-9+/]{40,}[\"']"),
    ("hex/加密长串", r"[\"'][0-9a-fA-F]{60,}[\"']"),
]


def iter_php_files(path):
    """支持目录、单个 zip、或目录树。返回 (绝对路径, 是否临时解压)。"""
    tmp_dirs = []
    if os.path.isfile(path) and path.lower().endswith(".zip"):
        d = tempfile.mkdtemp(prefix="bdscan_")
        tmp_dirs.append(d)
        with zipfile.ZipFile(path) as z:
            z.extractall(d)
        path = d
    for root, _, files in os.walk(path):
        for fn in files:
            if fn.lower().endswith((".php", ".phtml", ".php3", ".php5")):
                yield os.path.join(root, fn)
    for d in tmp_dirs:
        import shutil
        shutil.rmtree(d, ignore_errors=True)


def scan_file(fpath):
    hits = []
    try:
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return hits
    text = "".join(lines)
    for name, pat, weight in RULES:
        if weight == 0:
            continue
        for i, line in enumerate(lines, 1):
            if re.search(pat, line, re.IGNORECASE):
                snippet = line.strip()[:160]
                hits.append((weight, name, i, snippet))
    # 混淆入口(不计权, 只标记)
    for name, pat in OBFUSC_RULES:
        if re.search(pat, text, re.IGNORECASE):
            hits.append((0, "[混淆] " + name, 0, ""))
    return hits


def run_scan(target, top):
    scores = defaultdict(int)
    detail = defaultdict(list)
    total_files = 0

    for fpath in iter_php_files(target):
        total_files += 1
        hits = scan_file(fpath)
        if not hits:
            continue
        for weight, name, lineno, snippet in hits:
            scores[fpath] += weight
            detail[fpath].append((weight, name, lineno, snippet))

    print(f"[*] 扫描完成: 共 {total_files} 个 PHP 文件, "
          f"{len(scores)} 个命中可疑规则\n")
    if not scores:
        print("[-] 未命中任何规则。")
        return

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    for idx, (fpath, score) in enumerate(ranked[:top], 1):
        rel = os.path.basename(fpath)
        print(f"=== [{idx}] 危险度 {score}  {rel} ===")
        for weight, name, lineno, snippet in sorted(detail[fpath], key=lambda x: -x[0]):
            loc = f"L{lineno}" if lineno else "—"
            extra = f"  | {snippet}" if snippet else ""
            print(f"    ({weight:>2}) {name} @{loc}{extra}")
        print()

    print("[*] 提示: 危险度最高的文件优先审计；")
    print("    重点看 array_filter/base64_decode/eval/create_function/超全局 的组合。")


def main():
    ap = argparse.ArgumentParser(description="CTF 源码后门扫描器")
    ap.add_argument("target", nargs="?", default=None,
                    help="目录 / zip 文件路径（不填则进入交互模式，双击运行用）")
    ap.add_argument("--top", type=int, default=20, help="只显示前 N 个最可疑文件")
    args = ap.parse_args()

    # 双击 / 无参数运行 → 交互模式：问路径
    if args.target is None:
        try:
            target = input("Path: ").strip()
        except EOFError:
            target = ""
        if not target:
            print("[x] 没有输入路径。")
            sys.exit(1)
    else:
        target = args.target

    run_scan(target, args.top)

    # 有控制台窗口时，跑完等一个回车再关，防止窗口闪退
    if sys.stdin.isatty():
        input("\n按回车退出...")


if __name__ == "__main__":
    main()
