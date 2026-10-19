# -*- coding: utf-8 -*-
# POST 传参演示：requests 库
import requests

BASE = "http://node5.anna.nssctf.cn:28716"

# 1. 先发 GET：参数写在网址 ? 后面
print("=== 第1步：GET ?CTF=Lit2023 ===")
r1 = requests.get(BASE + "/?CTF=Lit2023")
print("服务器说:", r1.text[r1.text.find('<div class'):r1.text.find('</div>')+6][:80])

# 2. 再发 POST：参数放进 data= 字典（requests 会自动帮你 urlencode）
print("\n=== 第2步：POST Challenge=i'm_c0m1ng ===")
r2 = requests.post(BASE + "/?CTF=Lit2023", data={"Challenge": "i'm_c0m1ng"})
import re
m = re.findall(r'NSSCTF\{[^}]*\}|[a-z-]*message">[^<]*', r2.text)
print("拿到:", m)

# 防闪退：Windows 双击运行完别闪关，按任意键退出
print("\n按任意键退出...")
try:
    input()
except EOFError:
    pass
