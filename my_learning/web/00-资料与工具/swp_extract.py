# -*- coding: utf-8 -*-
"""
.swp 文件恢复工具 swp_extract.py
用法：
  1. 命令行带参：python swp_extract.py 下载到的.swp文件
  2. 直接运行后手动输入路径
原理：.swp 是 Vim 的二进制交换文件，但里面被编辑的可见字符会原样保留，
      所以提取可读字符串就能还原源码。
"""
import re
import sys


def extract(path):
    data = open(path, "rb").read()
    print(f"[*] 文件: {path}  ({len(data)} 字节)\n")

    # 提取所有可打印 ASCII 字符串（连续 >=4 个可读字符）
    strings = re.findall(rb'[\x20-\x7e]{4,}', data)

    # 过滤：优先显示像源码/flag 的，但也保留其他较长文本
    keywords = ['<?php', 'flag', 'NSSCTF', '$', 'echo', 'function',
                'include', 'eval', 'password', 'if', 'POST', 'GET', 'select']
    code_lines = []
    for s in strings:
        t = s.decode('latin1')
        if any(k in t for k in keywords):
            code_lines.append(t)
        elif len(t) >= 30:
            code_lines.append(t)

    print(f"[*] 提取到 {len(strings)} 段文本，其中 {len(code_lines)} 段像代码/线索\n")
    if not code_lines:
        print("[-] 没提取到明显内容，试试：vim -r <文件> 恢复")
        return
    print("=" * 50)
    for t in code_lines:
        print(t)
        print("-" * 50)


if __name__ == "__main__":
    path = ""
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = input("请输入 .swp 文件路径：").strip()
    if not path:
        print("[!] 没有输入路径，退出")
        sys.exit(1)
    extract(path)
    print("\n按回车键退出...")
    try:
        input()
    except EOFError:
        pass
