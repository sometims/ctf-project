# 上号 - MISC WP（流量分析 + steghide 隐写）

> 平台：qsnctf（青少年 CTF）| 题目：上号 | 方向：MISC（杂项）| 解题日期：2026-08-31
> **Flag：`qsnctf{07f453cd-8fd2-44e4-bdd1-160b0c503d10}`** ✅ 已独立复现

## 解题链路

```
上号.zip
  └─ files.pcapng（Wireshark 流量包，101KB）
       └─ 导出 HTTP 对象 → shanghao.zip
            └─ 解压 → shanghao.jpg（表情包"上号"）
                 ├─ jpg 尾部 7 字节: " qsnctf"（= steghide 密码提示）
                 └─ steghide extract -p qsnctf → flag.txt ← FLAG 在这里！
```

## 第 1 步：流量包导出 HTTP 对象（pcapng → shanghao.zip）

**Wireshark 操作**：
1. 打开 `files.pcapng`
2. 菜单：**文件 → 导出对象 → HTTP**
3. 列表里有 `shanghao.zip`（还有 flag.txt、shanghao.jpg，但只有 zip 被真正下载了）
4. 选中 → 保存

**Python 复现**（dpkt 按 TCP seq 重组）：
```python
import dpkt
pcap = dpkt.pcapng.Reader(open('files.pcapng','rb'))
streams = {}
for ts, buf in pcap:
    eth = dpkt.ethernet.Ethernet(buf)
    ip = eth.data
    t = ip.data
    if t.sport == 8000 and len(t.data) > 0:   # 服务器 8000 端口
        streams.setdefault(t.dport, []).append((t.seq, t.data))
for dport, pkts in streams.items():
    pkts.sort()
    data = b''.join(d for _, d in pkts)
    if data.startswith(b'HTTP/'):
        body = data[data.find(b'\r\n\r\n')+4:]
        if body[:2] == b'PK':    # ZIP 头
            open(f'shanghao_{dport}.zip','wb').write(body)
```

> 考点：**8000 端口 = Python SimpleHTTP 文件服务器**（HTTP 头显示 `Server: SimpleHTTP/0.6 Python/3.10.4`）。

## 第 2 步：解压 shanghao.zip → shanghao.jpg

shanghao.zip 无密码，解压得到 shanghao.jpg（7412 字节，248×170 表情包）。

## 第 3 步：010 Editor 看 jpg 尾部，发现密码

jpg 的 EOI（`FF D9`）之后还有 7 字节：
```
FF D9 20 71 73 6E 63 74 66   →  " qsnctf"
```
明文写着 `qsnctf` —— 这就是 steghide 的解密密码。

## 第 4 步：steghide 提取 flag.txt（核心考点）

```bash
steghide extract -sf shanghao.jpg -p qsnctf -xf flag.txt
# → wrote extracted data to "flag.txt"
# flag.txt: qsnctf{07f453cd-8fd2-44e4-bdd1-160b0c503d10}
```

**steghide 特点**（记住，CTF 高频）：
- 支持格式：**JPEG、BMP、WAV、AU**（jpg 图大概率是 steghide！）
- 默认加密：Rijndael-128（AES）CBC
- 嵌入方式：图论算法改像素值，统计上不易察觉
- 密码写 jpg 尾部是常见出题套路

## 工具就位（已下载到桌面 ctf_tools）

- **steghide**：`Desktop\ctf_tools\stego_tools\steghide_win32\steghide\steghide.exe`（Cygwin 版，dll 在同目录）
  - 用法：`steghide.exe extract -sf 图片 -p 密码 -xf 输出文件`
- **dpkt**（Python 流量解析）：已装隔离 venv

## 避坑

1. **steghide 没有官方 Windows 版**：下载 cygwin 编译版（steghide.exe + cygwin1.dll 等必须同目录）
2. **jpg 尾部找密码**：很多题把密码明文追加在图片末尾（010 Editor 拉到底）
3. **流量包先导出 HTTP 对象**：Wireshark「文件→导出对象→HTTP」比手工抓包重组快
4. **识别 steghide 隐写**：jpg/bmp/wav 图 + 尾部有密码字样 → 优先试 steghide
