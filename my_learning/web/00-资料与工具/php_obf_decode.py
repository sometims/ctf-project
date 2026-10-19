# -*- coding: utf-8 -*-
"""php_obf_decode.py —— PHP 混淆后门通用解码器
结构：alphabet 字符表 + 索引拼函数名 + eval(base64_decode(...)) 多层嵌套
用法：python php_obf_decode.py <混淆PHP文件>   （不传参则默认读同目录 qsnctf.php）
"""
import urllib.parse
import base64
import re
import sys
import os

DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qsnctf.php")
src = open(sys.argv[1] if len(sys.argv) > 1 else DEFAULT, encoding="utf-8", errors="replace").read()

# ---------- 第 1 层：最外层 eval ----------
m = re.search(r'\$O00OO0=urldecode\("([^"]+)"\);', src)
alpha = urllib.parse.unquote(m.group(1))
print("[alpha] len=%d : %r" % (len(alpha), alpha))

def g(i): return alpha[i]

# 拼函数名（和源码一致）
O00O0O = g(3)+g(6)+g(33)+g(30) + g(22)+g(36)+g(29)+g(26)+g(30)+g(32)+g(35)+g(26)+g(30)
O0OO00 = g(33)+g(10)+g(24)+g(10)+g(24)
OO0O00 = O0OO00[0]+g(18)+g(3)+O0OO00[0]+O0OO00[1]+g(24)
OO0000 = g(7)+g(13)
print("[funcs] O00O0O=%r O0OO00=%r OO0O00=%r OO0000=%r" % (O00O0O, O0OO00, OO0O00, OO0000))

m2 = re.search(r'eval\(\$O00O0O\("([A-Za-z0-9+/=]+)"\)\);', src)
b64_1 = m2.group(1)
layer1 = base64.b64decode(b64_1).decode("utf-8", errors="replace")
print("\n===== 第1层解码后（PHP）=====")
print(layer1)
print("===== 第1层结束 =====")

# ---------- 第 2 层：内层 eval('?>'.base64_decode(strtr(...))) ----------
m3 = re.search(r'\$O0O000="([A-Za-z0-9+/=]+)"', layer1)
S = m3.group(1)
half = int(OO0000)  # 52
s1 = S[0:half]        # substr(S,0,52)
s2 = S[half:half*2]   # substr(S,52,52)
s3 = S[half*2:]       # substr(S,104)
# strtr(s3, s2, s1)：把 s3 中出现的 s2 字符替换为 s1 对应字符
trans = str.maketrans(s2, s1)
layer2_b64 = s3.translate(trans)
layer2 = base64.b64decode(layer2_b64).decode("utf-8", errors="replace")
print("\n===== 第2层解码后（PHP 明文）=====")
print(layer2)
print("===== 第2层结束 =====")
