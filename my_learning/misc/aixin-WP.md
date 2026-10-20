# MISC 第 5 题「aixin」Writeup

平台：qsnctf（题名 aixin）
标签：pyc 反编译 / ROT 密码 / base64 / 字符串倒序

## 题目特征
- 压缩包 `aixin.zip` 里只有一个 `aixin.pyc`（620 字节，未加密）。
- 该 pyc 的 magic number 被改成 `0x0d55`（非标准 CPython 发布版 magic），直接用 `python aixin.pyc` 或 `marshal.loads` 会被拒（"bad marshal data"）。
- 但 marshal 数据流本身是标准 3.13 格式，用 `uncompyle6` 可直接反编译（它对 magic 校验较宽松/可指定版本）。

## 解题步骤

### 1. 反编译 pyc
```bash
uncompyle6 -o aixin.py aixin.pyc
```
得到 `aixin.py`，最后一行是关键：
```python
print("#Mx12ItE2XjqgYEBDADA0WGEhXQI2W2I4JNIiWEJEA05So2nrlQIU")
```

### 2. 去 # 取 payload
```
Mx12ItE2XjqgYEBDADA0WGEhXQI2W2I4JNIiWEJEA05So2nrlQIU
```

### 3. ROT16（只对字母平移 16 位）
ROT16 后：
```
Cn12YjU2NzgwOURTQTQ0MWUxNGY2M2Y4ZDYyMUZUQ05Ie2doYmfK
```
观察：开头 `Cn12Yj...` 形如 base64（`C`/`n`/`Y`/`j` 都是 base64 字母），确认是 base64 串。

### 4. base64 解码
```
}vb567809DSA441e14f63f8d621FTCNH{galf
```
注意：原串末尾带一个换行 `\n`（解码后变成不可见字符），处理时先 `.strip()`。

### 5. 字符串倒序
```
flag{HNCTF126d8f36f41e144ASD908765bv}
```

## Flag
```
flag{HNCTF126d8f36f41e144ASD908765bv}
```

## 知识点
- **pyc 反编译**：`.pyc` 是 Python 编译后的字节码。工具：`uncompyle6`（支持 2.7–3.8 较全，但对部分 3.13 需版本匹配）、`decompyle3`、`pycdc`（C++ 反编译器，对 magic 不敏感，最稳）。
- **magic number 绕过**：pyc 头部前 4 字节是 magic，标识 Python 版本。CTF 常改 magic 阻止加载，但 marshal 数据不变——用 `uncompyle6` 通常能直接过；若用 `marshal.loads` 需先把前 4 字节改成当前解释器合法 magic（`import importlib._bootstrap_external as e; e._RAW_MAGIC_NUMBER`）。
- **ROT 密码**：凯撒密码变体，ROT16 = 字母表平移 16 位。只作用于字母（A-Z/a-z），数字和符号不动。识别特征：密文只见字母平移、格式像 base64 时，优先试 ROT 再 base64。
- **多层编码套路**：print 出来的字符串往往还要再解码 2~3 层（ROT→base64→倒序），看到 base64 字符集就要 base64 解，解完不像明文就考虑倒序/再 ROT。
- **倒序 flag**：CTF 常见把 `flag{...}` 倒着藏，解码后整体 `[::-1]` 还原。

## 复现脚本（一键验证）
```python
import base64
s = "Mx12ItE2XjqgYEBDADA0WGEhXQI2W2I4JNIiWEJEA05So2nrlQIU"
def rot(t, n):
    o = []
    for c in t:
        if 'a' <= c <= 'z': o.append(chr((ord(c)-97+n)%26+97))
        elif 'A' <= c <= 'Z': o.append(chr((ord(c)-65+n)%26+65))
        else: o.append(c)
    return ''.join(o)
r = rot(s, 16)
b = base64.b64decode(r).decode().strip()   # 注意 strip 掉末尾换行
print(b[::-1])   # flag{HNCTF126d8f36f41e144ASD908765bv}
```
