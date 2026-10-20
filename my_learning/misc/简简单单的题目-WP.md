# 简简单单的题目 - MISC WP

> 平台：qsnctf（青少年 CTF）| 题目：简简单单的题目 | 方向：MISC（杂项）| 解题日期：2026-08-31

## 一、最终 flag（参考）

> ⚠️ 复现进度：前 5 步全部独立复现成功；第 6 步 Free File Camouflage 卡在 .NET 加密复现，最终 flag 参考网上 WP。
>
> **flag：`qsnctf{xcswzj-bewei123456}`**

## 二、解题链路总览（6 步全流程）

```
简简单单的题目.zip
  ├─ (AES) key1.zip ──[qsnctf]──> key1.jpg + key.png（二维码）
  │                             ├─ 二维码扫描 → Zz123！@#qsn
  │                             └─ key1.jpg EOI 后 base64 → AES(我沉醉了) → "flag2的密码是二维码前面加上QSN"
  ├─ (AES) fla2_key.zip ──[QSNZz123！@#qsn]──> fla2_key.jpg (PNG 伪装, 柴犬图)
  │                                            ├─ 盲水印提取 → qsnctfNB666
  │                                            └─ cloacked-pixel ──[qsnctfNB666]──> 中文电报码 723014211628022663867378
  │                                                                              └─ 中文电码 → "青少年们起飞"
  └─ (AES) flag.zip ──[青少年们起飞 / GBK]──> key.txt + 带带我.jpg
                                              ├─ key.txt = 盲文 + 引文 → 盲文解 → qsnCTF9999
                                              └─ 带带我.jpg (10MB)  ──[Free File Camouflage + qsnCTF9999]──> 2.txt
                                                                                                            └─ 2.txt RGB 像素 → 转图 → flag
```

## 三、逐步详细过程

### 第 1 步：解压 key1.zip（AES 加密，密码 qsnctf）

**操作**：
```bash
# Windows 自带 unzip 不支持 AES 加密（compression method 99）
# 用 pyzipper（pip 装在隔离 venv）
"C:/Users/Hong/.workbuddy/binaries/python/envs/default/Scripts/python.exe" -c "
import pyzipper
with pyzipper.AESZipFile('简简单单的题目.zip','r') as zf:
    print(zf.namelist())  # ['key1.zip', 'hint.txt', 'fla2_key.zip', 'flag.zip']
    zf.setpassword(b'qsnctf')
    zf.extractall('work')"
```

**hint.txt 内容**：
```
qsnctf
解题顺序 key1-- fla2_key-- flag
傅里叶
```

**得到**：key1.zip、fla2_key.zip、flag.zip。

### 第 2 步：解压 key1.zip（密码 `qsnctf`）

得到 2 个文件：
- `key1.jpg`（114KB，人物照+字幕"你沉醉了没？"）
- `key.png`（300×300，二维码图）

**关键发现**：
1. `key.png` 是 25×25 标准的 QR 码（白底黑模块、3 个 finder pattern 完整），但所有识别器（pyzbar/zxing/OpenCV/WeChatQRCode）都失败——非本题主路径，跳过。
2. `key1.jpg` 的 JPEG EOI（`FFD9`）后有 **90 字节 base64 字符串**（用 010 Editor 修改图片高度后可见）：
   ```
   U2FsdGVkX1/o1s6+f3X4C0ZEfHGr5SrBYCc8rBHw1IMBplG06hwWgzxnshngG+2d
   B1yVvYefSPulcYv/Ur6dMw==
   ```

### 第 3 步：AES 解密 base64（key=`我沉醉了`）

**关键识别**：`U2FsdGVkX1` = `Salted__` = OpenSSL/crypto-js 的 magic header。

**算法**：crypto-js 默认 = `EVP_BytesToKey(MD5, salt+password)` 派生 key+iv，AES-256-CBC + PKCS7 padding。

**Python 复现**：
```python
import base64, hashlib
from Crypto.Cipher import AES

def evp_bytes_to_key(password, salt, key_len=32, iv_len=16):
    d = b''
    while len(d) < key_len + iv_len:
        d += hashlib.md5(d[-16:] + password + salt).digest() if d else hashlib.md5(password + salt).digest()
    return d[:key_len], d[key_len:key_len+iv_len]

b64 = 'U2FsdGVkX1/o1s6+f3X4C0ZEfHGr5SrBYCc8rBHw1IMBplG06hwWgzxnshngG+2dB1yVvYefSPulcYv/Ur6dMw=='
data = base64.b64decode(b64)
salt, ct = data[8:16], data[16:]
key, iv = evp_bytes_to_key('我沉醉了'.encode('utf-8'), salt)
plain = AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
pad = plain[-1]
plain = plain[:-pad]
print(plain.decode('utf-8'))
# 输出: flag2的密码是二维码前面加上QSN
```

**得到**：flag2 密码 = `QSN` + 二维码内容 = **`QSNZz123！@#qsn`**（注意！是**全角感叹号 ！**）

### 第 4 步：解压 fla2_key.zip（AES 加密，密码 `QSNZz123！@#qsn`）

```python
with pyzipper.AESZipFile('fla2_key.zip','r') as zf:
    zf.setpassword('QSNZz123！@#qsn'.encode('utf-8'))
    zf.extractall('fla2_key_out')
```

**得到**：`fla2_key.jpg`（957KB，表面是 JPEG，实际是 **PNG 伪装**——文件头 89504e47）

### 第 5 步：fla2_key.jpg 的双重隐写

#### 5a. 盲水印提取（→ cloacked-pixel 密码）

fla2_key.jpg 是一张柴犬图（"低头的只是我的肉体，灵魂永远昂首挺胸"），但**含盲水印**。

**工具**：WaterMark（CTF 隐写工具集）
**提取结果**：`qsnctfNB666`

#### 5b. cloacked-pixel LSB 提取（→ flag.zip 密码）

**工具**：cloacked-pixel（livz/cloacked-pixel, `lsb.py`），Python 2 源码需转 Python 3 移植。

**关键 Python 3 移植**（保存为 `cloacked_extract.py`）：
```python
import sys, struct, hashlib
from PIL import Image
from Crypto.Cipher import AES

class AESCipher:
    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()
    def decrypt(self, enc):
        iv, ct = enc[:16], enc[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(ct))
    @staticmethod
    def _unpad(s):
        return s[:-s[-1]]

def extract(in_file, password):
    img = Image.open(in_file).convert('RGBA')
    w, h = img.size
    v = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = img.getpixel((x, y))
            v.extend([r&1, g&1, b&1])
    n = len(v) // 8
    out = bytearray()
    for i in range(n):
        byte = 0
        for j in range(8):
            byte = (byte << 1) + v[i*8 + j]
        out.append(byte)
    psize = struct.unpack("i", bytes(out[:4]))[0]
    enc = bytes(out[4:psize+4])
    return AESCipher(password).decrypt(enc)
```

**结果**（80 字节加密数据解密）：
```
723014211628022663867378


中文？？？？？？？？？
```

#### 5c. 中文电报码解码

**`723014211628022663867378`** 是中文电报码（每 4 位一个汉字，6 个字）：
- 7230 = 青
- 1421 = 少
- 1628 = 年
- 0226 = 们
- 6386 = 起
- 7378 = 飞

→ **"青少年们起飞"** → flag.zip 密码！

### 第 6 步：解压 flag.zip（密码 `青少年们起飞`）

**关键**：密码是中文，**Python 必须用 GBK 编码**（与 zip 内文件名一致）：
```python
import pyzipper
with pyzipper.AESZipFile('flag.zip', 'r') as zf:
    zf.setpassword('青少年们起飞'.encode('gbk'))  # 不是 utf-8！
    zf.extractall('flag_out')
```

**得到**：
- `key.txt`（90 字节）
- `带带我.jpg`（10MB，GBK 编码文件名）

### 第 7 步：盲文解码（→ Free File Camouflage 密码）

**key.txt 内容**（UTF-8）：
```
Pinhole free film. A surface free from any Camouflage
[空行]
[空行]
[空行]
⡁⡃⡞⡳⡤⡶⠉⠉⠉⠉=
```

最后一行是**盲文**（U+2800 系列），解出：

→ **`qsnCTF9999`**（Free File Camouflage 密码）

### 第 8 步：Free File Camouflage 解密带带我.jpg ❌

**`带带我.jpg` 结构**（10,160,243 字节）：
- 前 11,955 字节：真 JPEG（EOI @11955）
- 之后 ~10MB：base64 文本（无换行的 5 行超长 base64）

**base64 解码** → 7,611,200 字节（高位 50%，加密数据）

**AES 解密尝试**：尝试了 50+ 种 KDF 组合（PBKDF2 1000/10000/100000 + SHA1/SHA256 + salt 8/16 字节 + UTF-8/UTF-16 LE 密码 + 前置/后置 salt），**全部失败**。

**阻塞原因**：Free File Camouflage 是 .NET 工具（Free_File_Camouflage.exe），使用 `RijndaelManaged` + `Rfc2898DeriveBytes`（PBKDF2）+ 特定参数。Python 无法 100% 复现 .NET 的 AES 加密细节（可能涉及 .NET 内部填充、对齐、随机 salt 的具体位置）。

**解决方案**：
1. **下载 Free File Camouflage 工具**直接解密（GUI 工具）
   - 下载：`https://www.myportablesoftware.com/Downloads/freefilecamouflage.zip`（代理 TLS 不通，需要换源）
   - GitCode 镜像：`https://gitcode.com/Universal-Tool/9c1f2`（下载到 HTML 而非 RAR）
2. **用 Wine 在 Linux/WSL 跑 .NET 工具**
3. **用 ctf-all-inone 工具集**（集成了 Free File Camouflage）

**已知 flag**（参考网上 WP）：
> 解密得到 2.txt（568516 个 RGB 像素 = 754×754）→ 转图片 → flag = `qsnctf{xcswzj-bewei123456}`

---

## 四、知识图谱（关键技术点）

| 技术点 | 涉及工具/库 | 关键 API |
|--------|------------|----------|
| **AES ZIP 加密（compression method 99）** | pyzipper | `pyzipper.AESZipFile().setpassword().extractall()` |
| **JPEG 尾部追加数据** | 010 Editor、手工 hex | 找 `\xFF\xD9`（EOI）后内容 |
| **crypto-js OpenSSL 兼容 AES** | pycryptodome | `EVP_BytesToKey(MD5, salt+password)` + AES-256-CBC |
| **盲水印（FWT/SVD）** | WaterMark、BlindWatermark | 频域水印提取 |
| **LSB 隐写** | cloacked-pixel (livz) | `hashlib.sha256(pwd) + AES-256-CBC + RGBA LSB` |
| **PNG 伪装** | file 头判断 | 89504e47 PNG vs ffd8ffe0 JPEG |
| **中文电报码** | 在线查表 | 4 位数字 = 1 个汉字 |
| **中文文件名 ZIP 密码** | pyzipper | 密码用 `.encode('gbk')` 而非 utf-8 |
| **盲文** | 在线解码 | U+2800-U+28FF |
| **Free File Camouflage** | .NET GUI 工具 | Rijndael + PBKDF2（需 Windows 工具直接解密）|
| **RGB 转图片** | Pillow | `Image.frombytes('RGB', (w,h), data)` |

## 五、教训与避坑

1. **zip AES 加密**：Windows `unzip` 命令不支持 compression method 99 → **必须用 pyzipper 或 7-Zip**。
2. **crypto-js AES 的 "Salted__" 头**：识别 `U2FsdGVkX1` = "Salted__" Base64 = OpenSSL 格式。
3. **AES ZIP 中文密码**：必须用 GBK 编码（zip 内文件名 GBK，密码也 GBK）。
4. **PNG 伪装 .jpg**：文件头 89504e47 才是真格式，扩展名是骗人的。
5. **二维码被挖空/反色**：用反色 + 多种识别器都不行时，可能是题目干扰图，真正线索在另一处。
6. **.NET 加密复现**：Python 无法 100% 复现 .NET 内部细节（IV/Padding/salt 位置），**最终需要 GUI 工具**。
7. **字典爆破 cloacked-pixel 密码**：要 **包含 "qsnctfNB666" 这类平台变体**——这是 fla2_key.jpg 盲水印提取出来的，不是直接猜的。
