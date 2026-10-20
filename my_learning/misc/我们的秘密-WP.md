# MISC 第 4 题「我们的秘密」Writeup

平台：qsnctf
标签：DNS TXT 记录隐写 / 信息收集

## 题目特征
- 给一个压缩包 `我们的秘密.zip`，里面只有一个 txt。
- txt 原文件名是 GBK 编码乱码（解压后显示为「题目附件.txt」），内容只有一行：`flag.qsnctf.com`。

## 解题步骤

### 1. 解压并修复文件名乱码
zip 内文件名用的是 GBK 编码，默认按 cp437 读会乱码。Python 修复：
```python
import zipfile
z = zipfile.ZipFile('我们的秘密.zip')
for info in z.infolist():
    name = info.filename.encode('cp437').decode('gbk')  # 还原中文名
    open(name, 'wb').write(z.read(info))
```
解出 `题目附件.txt`，内容：`flag.qsnctf.com`。

### 2. 访问网页是陷阱
直接用浏览器/curl 打 `http://flag.qsnctf.com` → 502 / DNS 解析失败。
说明这个子域**没有 A 记录**，网页路线走不通。

### 3. 查 DNS TXT 记录（正解）
flag 藏在 DNS 的 TXT 记录里：
```bash
nslookup -type=TXT flag.qsnctf.com
```
返回：
```
flag.qsnctf.com  text = "qsnctf{4647894508d335fb4d32b1862b40e6a5}"
```

## Flag
```
qsnctf{4647894508d335fb4d32b1862b40e6a5}
```

## 知识点
- **DNS 记录类型**：A（IPv4）、CNAME（别名）、MX（邮件）、TXT（文本）。CTF 常把 flag 塞进 TXT 记录，因为浏览器访问网页看不到，必须主动查 DNS。
- **解题命令模板**：`nslookup -type=TXT <域名>` 或 `dig TXT <域名>`。
- **文件名 GBK 乱码**：Windows 下打的 zip 用 GBK 编码文件名，Linux/Python 默认 cp437 会乱码，用 `encode('cp437').decode('gbk')` 还原。
- **信息收集题思路**：拿到一个域名，不要只想着开网页。先看 DNS 有没有 A/CNAME/TXT 记录，TXT 经常藏彩蛋。

## 同类题防御清单
下次遇到"只给一个域名/网址"的 MISC 题，按这个顺序排查：
1. `nslookup -type=TXT 域名` —— 先看 TXT 有没有 flag
2. `nslookup -type=A 域名` —— A 记录能否解析
3. 访问 http/https 看网页源码、注释、F12
4. whois / 子域爆破（如果域名本身可疑）
