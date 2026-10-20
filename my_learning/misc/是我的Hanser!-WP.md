# 是我的Hanser! - MISC WP

> 平台：qsnctf（青少年 CTF）| 题目：是我的Hanser! | 方向：MISC（杂项）| 解题日期：2026-08-31
> **Flag：`qsnctf{bb3bdea1fba9b8b940c3cb788d3f0aae}`** ✅ 已独立复现

## 解题链路

```
是我的Hanser!.zip
  ├─ -ร+สม-Hanser!.txt（1979B，爱沙尼亚语《追风筝的人》节选）
  │    └─ 零宽字符隐写（U+200B/C/D/E/F + U+FEFF）
  │         └─ 5 进制解码 → "Password is : Hanser2024"
  └─ Hanser.zip（AES 加密，密码 Hanser2024）
       └─ Hanser.psd（2400×1499 Photoshop 文件）
            └─ 图层名 = FLAG，图层文本 = flag
```

## 第 1 步：零宽字符隐写（Zero-Width Steganography）

txt 文件（UTF-8）开头是大量**零宽字符**：
- `U+200B` (ZWSP 零宽空格)、`U+200C` (ZWNJ)、`U+200D` (ZWJ)、`U+200E` (LRM)、`U+200F` (RLM)、`U+FEFF` (BOM)

**统计**：共 95 个零宽字符；其中 `U+200B` 23 个作为**分隔符**，其余 72 个 = 24 组 × 每组 3 个。

**解码规则**（5 进制）：
- 5 种编码字符映射数字：`\u200e`=0, `\u200f`=1, `\u200c`=2, `\u200d`=3, `\ufeff`=4
- 每组 3 字符 = 5 进制数（位1×25 + 位2×5 + 位3）→ ASCII
- 24 组 → 24 个 ASCII 字符

**Python 解码**：
```python
import os
# 读 txt
text = open(txt_path, 'rb').read().decode('utf-8')
# 提取零宽字符
zw = set('\u200b\u200c\u200d\u200e\u200f\ufeff')
seq = [c for c in text if c in zw]
# 按 \u200b 分组（每组 3 字符）
groups, cur = [], []
for c in seq:
    if c == '\u200b': groups.append(''.join(cur)); cur = []
    else: cur.append(c)
if cur: groups.append(''.join(cur))
# 5 进制 → ASCII
m = {'\u200e':0, '\u200f':1, '\u200c':2, '\u200d':3, '\ufeff':4}
out = ''.join(chr(m[g[0]]*25 + m[g[1]]*5 + m[g[2]]) for g in groups)
print(out)  # Password is : Hanser2024
```

**得到**：Hanser.zip 密码 = **`Hanser2024`**

## 第 2 步：解压 Hanser.zip（AES 加密）

```python
import pyzipper
with pyzipper.AESZipFile('Hanser.zip','r') as zf:
    zf.setpassword(b'Hanser2024')
    zf.extractall('hanser_out')   # → Hanser.psd (16.4MB)
```

## 第 3 步：Hanser.psd 图层分析

**Hanser.psd**：2400×1499 RGB Photoshop 文件。

**关键**：PSD 的图层元数据（XMP 描述）里存有**图层名和图层文本**！

```python
import re
data = open('Hanser.psd','rb').read()
# 图层名
names = re.findall(rb'<photoshop:LayerName>([^<]+)</photoshop:LayerName>', data)
# 图层文本
texts = re.findall(rb'<photoshop:LayerText>([^<]+)</photoshop:LayerText>', data)
```

**结果**：
- 图层名：`FLAG`
- 图层文本：`qsnctf{bb3bdea1fba9b8b940c3cb788d3f0aae}`

→ **Flag = `qsnctf{bb3bdea1fba9b8b940c3cb788d3f0aae}`**

## 知识要点

| 技术点 | 说明 |
|--------|------|
| **零宽字符隐写** | 用 U+200B/C/D/E/F、U+FEFF 等不可见字符编码信息；常见工具有 stegcloak、zwsp-steg |
| **5 进制编码** | 5 种字符映射 0-4，每 3 字符 = 5^3 = 125 种组合，对应 ASCII 可打印区 |
| **爱沙尼亚语干扰** | txt 主体是《追风筝的人》(Kite Runner) 爱沙尼亚语节选——干扰项，藏信息的是零宽字符 |
| **PSD 图层元数据** | `<photoshop:LayerName>` / `<photoshop:LayerText>` 存在 PSD 的 XML 描述区，可直接字符串搜索 |
| **题目梗** | "Hanser"=《追风筝的人》主角 Hassan 谐音；密码 Hanser2024 与此呼应 |

## 避坑

1. **看到 txt 开头有"隐形字符"** → 先检查零宽字符（转 unicode_escape 查看）。
2. **零宽字符编码不一定是 2 进制**：本题用 5 种字符 = 5 进制，需穷举/分析分组。
3. **PSD 文件**：不止图像像素，图层名/图层文本/注释都是隐藏信息载体，`strings`/正则直接搜。
4. **文件名乱码**（`-ร+สม-Hanser!.txt`）是 GBK/UTF-8 编码问题，不影响内容。
