# MISC 第 7 题「多情」（qsnctf / 青少年CTF训练）

标签：PNG 串联分离 / IHDR 高度篡改修复 / 二进制索引排序 / HTML 实体编码

**Flag：`qsnctf{Lrp5mJcdEbbv2bnf6HQSNh}`**

## 题目特征

附件 `多情.zip` 解开后是两个东西：

| 文件 | 说明 |
| --- | --- |
| `多情.zip`（内层） | 里面是 10 个极小的 txt，文件名形如「第一个0.txt」「第一个1.txt」 |
| `看看我.png` | 442×186 的图片，画面是「自古多情空余恨」 |

两个都是伏笔：图片名字在叫你「看看我」，内层压缩包里的文件名在暗示排序。

## 解题步骤

### 1. 先确认压缩包是真加密还是假警报

外层 `多情.zip` 的条目 flags 显示 `0x0002`，很容易被误判成加密。实际上 ZIP 的标志位要拆开看：

- `0x0001` = 文件已加密（**真加密**）
- `0x0002` = deflate 最大压缩（**跟加密无关**，正常压缩包也会有）

本题 flags 只有 `0x0002`，没有 `0x0001`，所以 Python 的 `zipfile` 可以直接读：

```python
import zipfile
z = zipfile.ZipFile('多情.zip')
for i in z.infolist():
    data = z.read(i.filename)      # 不需要密码
```

> 判断题眼：flags 里有 `0x0001` 才是加密；只有 `0x0002` 只是压缩选项位。伪加密的特征则是**本地文件头和中央目录的标志位不一致**。

### 2. 「看看我.png」里其实串着两张 PNG

把文件按 PNG 签名切分，发现不是一张图，而是两张首尾相接：

```
段1：偏移 0      → 6714    442×186  「自古多情空余恨」
段2：偏移 6714   → 17621   721×150  ← 打不开
```

正常情况下一个 PNG 的 `IEND` 块之后就不该有数据了。这里 `IEND` 后面又跟了一个完整的 PNG 签名，说明有人把两张图拼成了一个文件。

### 3. 第二张图打不开：高度被改了

用 PIL 打开第二段会报 `UnidentifiedImageError`，但 chunk 结构其实是完整的。问题出在 IHDR：

- IHDR 声称：721 × **150**
- IDAT 解压后长度：1,148,230 字节
- 每行字节数 = 1（滤波字节）+ 721 × 4（RGBA）= 2885
- 1148230 ÷ 2885 = **398**

也就是说图片真实高度是 **398**，被改成了 150，多出来的 248 行就成了「看不见」的隐藏区域。修 IHDR 的高度并重算 CRC 即可：

```python
import zlib, struct
p = bytearray(open('png_2.png', 'rb').read())
p[20:24] = struct.pack('>I', 398)                    # 改高度
crc = zlib.crc32(bytes(p[12:29])) & 0xffffffff       # 重算 IHDR 的 CRC
p[29:33] = struct.pack('>I', crc)
open('png_2_fixed.png', 'wb').write(p)
```

修完打开，图里露出两行内容：

```
长安在何处，只在马蹄下。
996
```

**996 就是下一步的钥匙。**

### 4. 用 996 的二进制决定拼接顺序

内层压缩包里有 10 个 txt：6 个以「1」结尾、4 个以「0」结尾。

```
996 = 1111100100（二进制）
      └ 6 个 1、4 个 0 —— 数量刚好对上
```

于是二进制串的每一位就是「第几个 0/1 文件」的取用顺序：

| 位序 | 位值 | 取哪个文件 | 内容 |
| --- | --- | --- | --- |
| 1 | 1 | 第一个1.txt | Lr |
| 2 | 1 | 第二个1.txt | p5 |
| 3 | 1 | 第三个1.txt | mJ |
| 4 | 1 | 第四个1.txt | cd |
| 5 | 1 | 第五个1.txt | Eb |
| 6 | 0 | 第一个0.txt | bv2 |
| 7 | 0 | 第二个0.txt | bn |
| 8 | 1 | 第六个1.txt | f6H |
| 9 | 0 | 第三个0.txt | QS |
| 10 | 0 | 第四个0.txt | Nh |

> 注意「0 的序号」和「1 的序号」是**各自独立计数**的：第 6 位是这一串里第 1 个 0，所以取「第一个0.txt」，不是「第六个0.txt」。

### 5. 内容是 HTML 实体，不是密文

每个 txt 打开是这样的：

```
&#98;&#118;&#50;
```

这是 HTML 十进制字符实体（`&#数字;`），`&#98;` 就是 ASCII 98 = `b`。用 `html.unescape` 一次解掉：

```python
import html
v = html.unescape('&#98;&#118;&#50;')   # -> 'bv2'
```

十段按上表顺序拼起来：

```
Lr + p5 + mJ + cd + Eb + bv2 + bn + f6H + QS + Nh
= Lrp5mJcdEbbv2bnf6HQSNh
```

这串就是 flag 内文，直接套上平台前缀：

```
qsnctf{Lrp5mJcdEbbv2bnf6HQSNh}
```

## 完整复现脚本

```python
import zipfile, zlib, struct, html, os, io
from PIL import Image

# 1. 解开外层（无真加密）
z = zipfile.ZipFile('多情.zip')
for i in z.infolist():
    nm = i.filename.encode('cp437').decode('gbk')
    open(nm, 'wb').write(z.read(i.filename))

# 2. 拆分串联的 PNG
d = open('看看我.png', 'rb').read()
SIG, END = b'\x89PNG\r\n\x1a\n', b'IEND\xaeB`\x82'
starts = []; i = 0
while (j := d.find(SIG, i)) >= 0:
    k = d.find(END, j); starts.append((j, k + 8)); i = k + 8
open('png_1.png', 'wb').write(d[starts[0][0]:starts[0][1]])
p = bytearray(d[starts[1][0]:starts[1][1]])

# 3. 修 IHDR 高度（150 -> 398）+ 重算 CRC
p[20:24] = struct.pack('>I', 398)
p[29:33] = struct.pack('>I', zlib.crc32(bytes(p[12:29])) & 0xffffffff)
open('png_2_fixed.png', 'wb').write(p)      # 打开可看到 996

# 4. 按 996 的二进制顺序取文件
CN = ['零', '一', '二', '三', '四', '五', '六']
z2 = zipfile.ZipFile('多情.zip')  # 内层同名，此处指内层解出的文件
bits = bin(996)[2:]
out = ''
for pos, b in enumerate(bits, 1):
    idx = sum(1 for x in bits[:pos] if x == b)      # 同值第几次出现
    name = f'第{CN[idx]}个{b}.txt'
    out += html.unescape(open(name, encoding='utf-8').read().strip())

print('qsnctf{%s}' % out)   # qsnctf{Lrp5mJcdEbbv2bnf6HQSNh}
```

## 知识点

1. **ZIP 标志位要拆开看**：`0x0001` 才是加密；`0x0002` 是 deflate 压缩选项。把 `0x0002` 当成加密是本题第一个假警报。
2. **PNG 可以首尾串联**：一个文件里可以有多个 `\x89PNG` 签名，按签名切分就能取出来。判断依据是「`IEND` 之后还有数据」。
3. **改高度是最常见的 PNG 隐写**：IHDR 里的高度调小，多出来的像素行不会被渲染，但 IDAT 里数据还在。识别方法是**用 IDAT 解压长度反推真实高度**：`高 = 解压长度 ÷ (1 + 宽 × 每像素字节数)`。
4. **改完 IHDR 必须重算 CRC**：PNG 每个 chunk 尾部都有 CRC32，只改数值不改校验，多数工具会直接报错或拒绝加载。
5. **图片里的文字可以是纯提示**：「996」不是装饰，是这个题目的索引表。图片题首先要「看图说话」。
6. **二进制当索引**：一个十进制数转成 0/1 串后，每一位既能当值也能当顺序，这类「用数字指路」在 MISC 里很常见。关键是先数清楚两边数量对不对得上（6 个 1、4 个 0）。
7. **HTML 实体编码**：`&#数字;` 是十进制、`&#x十六进制;` 是十六进制，`html.unescape` 一条命令解掉，别手动替换。

## 踩过的坑（复盘）

- **一开始按文档顺序拼接**：直接按「第一个0、第一个1、第二个0……」拼出 `bv2Lrbnp5QSmJNhcdEbf6H`，然后把它当 Base64 解，穷举了 10 个片段的全部 3,628,800 种排列都解不出可读文本。**根因不是顺序，是压根不该做 Base64** —— 这串拼完就是 flag 内文本身。教训：先确认「这串东西应该是什么」，再决定解码方式，别默认它是 Base64。
- **0 和 1 的编号各自独立**：一度想成「第六个0.txt」，但二进制第 6 位是整串里**第 1 个 0**，应该取「第一个0.txt」。数错了就整串全错。
- **第二张图打不开时不要急着当"损坏文件"丢掉**：结构完整但 PIL 报错，优先怀疑 IHDR 尺寸和 CRC，而不是数据坏了。

## 同类题防御清单（下次遇到图片+压缩包组合）

1. 压缩包先查 flags：`0x0001` 才要密码，`0x0002` 别慌。
2. 图片先 `binwalk` / 手动找多个文件签名，看有没有串联文件。
3. 图片打不开 → 核对 IHDR 宽高与实际 IDAT 长度是否匹配，改了记得重算 CRC。
4. 图片能打开 → 读图上的文字，它经常是提示而不是干扰。
5. 一堆小文件按数字/0-1 命名 → 找一个「数量刚好对上」的数，转成二进制当索引。
6. 内容像 `&#xx;` → HTML 实体；像 `\uXXXX` → Unicode 转义；先做这层再谈解码。
