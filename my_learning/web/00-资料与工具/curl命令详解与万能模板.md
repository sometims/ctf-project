# curl 命令详解 + 可直接用的指令模板

> 面向：CTF Web 做题。写法按「怎么发 → 带什么 → 怎么收」三段组织，不按字母表背。
> 环境：Windows 下用 Git Bash 就写 `curl`；PowerShell 里必须写 `curl.exe`（`curl` 是 `Invoke-WebRequest` 的别名）。
>
> 配套工具：`curl构造器.html`（双击用浏览器打开）——填空自动生成命令，右侧逐行解释参数，底部附完整选项速查表；支持 Bash / PowerShell / CMD 三种引号规则。记不住语法时先用它拼一条，再对照本文看原理。

---

## 0. 先给模板：一条能直接用的

```bash
curl -sS -i -L --max-time 15 \
  -X POST \
  -H "Cookie: username=admin" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "username=admin" \
  --data-urlencode "password=123456" \
  "http://challenge.qsnctf.com:59051/login.php" \
  -o resp.txt \
  -w "\n[状态码] %{http_code}  [耗时] %{time_total}s  [大小] %{size_download}B  [最终URL] %{url_effective}\n"
```

逐行拆：

| 片段 | 意思 |
|---|---|
| `-sS` | 静默关进度条，但**报错照常显示**（只用 `-s` 会把错误也吞掉） |
| `-i` | 打印响应头（看 `Server` / `X-Powered-By` / `Set-Cookie` / `Location`） |
| `-L` | 跟随 302 跳转（不加就只能看到一条 302 空壳） |
| `--max-time 15` | 整个请求 15 秒不结束就放弃，防止卡死 |
| `-X POST` | 指定方法。其实有 `-d` 时默认就是 POST，写上是让命令自解释 |
| `-H "Cookie: ..."` | 手动带 Cookie，身份伪造/会话测试就改这里 |
| `-H "Content-Type: ..."` | 表单提交的默认类型，显式写出来方便改成 `application/json` |
| `--data-urlencode "k=v"` | 提交参数并做 URL 编码，中文、空格、`&`、`;` 都不会破坏请求 |
| `-o resp.txt` | 响应体存文件，避免刷屏、方便 grep |
| `-w "..."` | 请求结束后追加一行统计，`%{http_code}` 这类是 curl 的占位变量 |

**只需要改三处**：URL、`-H` 里的身份、`--data-urlencode` 里的参数。

---

## 1. 命令结构

```
curl  [选项...]  URL
```

- 选项顺序无所谓，**URL 放最后**是习惯写法。
- 一条命令里选项是全局生效的，不是「只作用于后一个 URL」。
- 所有选项都有短写和长写：`-s` = `--silent`，`-H` = `--header`，`-d` = `--data`。脚本里用长写更好读。

---

## 2. 参数详解

### 2.1 怎么发：方法与数据

> **必填 vs 可选**：curl 只有 `URL` 是必填的；下表所有选项都是可选的，不写就不生效。
> `⭐ 常用` = 做题高频，优先记；`○ 按需` = 遇到场景再查。

| 参数 | 全称 | 作用 | 典型写法 | 坑 | 常用度 |
|---|---|---|---|---|---|
| `-X` | `--request` | 指定 HTTP 方法 | `-X POST` / `-X PUT` / `-X DELETE` | `-X GET` 配 `-d` 会发出「带 body 的 GET」，有些服务端会 400 | ⭐ 常用（有 `-d`/`-F` 时可省略） |
| `-d` | `--data` | 提交数据，**默认方法变成 POST** | `-d "a=1&b=2"` | 不做 URL 编码；多个 `-d` 之间自动用 `&` 拼 | ⭐ 常用 |
| `--data-urlencode` | 同义 | 提交数据并 URL 编码 | `--data-urlencode "q=你好 世界"` | 一次只能一个参数，多个就写多行 | ⭐ 常用 |
| `--data-binary` | 同义 | 原样发，不处理换行 | `--data-binary @payload.json` | 发 JSON 用它，别用 `-d`（`-d` 会吃掉换行） | ○ 按需 |
| `-F` | `--form` | `multipart/form-data`，文件上传 | `-F "file=@shell.php"` | 不要同时写 `-H "Content-Type"`，curl 自己会带上 boundary | ⭐ 常用 |
| `-G` | `--get` | **把 `-d` / `--data-urlencode` 的数据全部搬到 URL，并改用 GET**；不是「POST 转 GET」开关 | `-G --data-urlencode "id=1"` | 加了 `-G` 就没有 body；想同时带 POST body 别用它；单独用无效 | ○ 按需（易错，见下方重点） |
| `--json` | — | 等价于 `-d` + JSON 两个头（curl ≥ 7.82） | `--json '{"a":1}'` | 老版本 curl 没这个参数，稳妥用 `-H` + `-d` | ○ 按需 |
| `--url-query` | — | 把参数追加到 URL 查询串，**不影响方法和 body**（curl ≥ 7.87） | `--url-query "id=1"` | 版本较新；老版本直接用 `URL?id=1` | ○ 按需 |

> ⚠️ **重点：`-G` 的真实行为**
>
> `-G` 不是「把 POST 数据变成 GET 数据」的开关。它实际做两件事：
> 1. 把后面所有 `-d` / `--data-urlencode` 的数据**追加到 URL 查询串**；
> 2. 让 curl 使用 **GET** 方法。
>
> 所以数据不会留在请求体里——**加了 `-G` 就没有 POST body 了**。它只适合「纯 GET 且参数需要自动编码」的场景。
>
> | 你想要的效果 | 正确写法 | 方法 | 参数位置 |
> |---|---|---|---|
> | 纯 GET，参数含中文/特殊字符 | `-G --data-urlencode "q=..."` | GET | 全在 URL |
> | GET 查询参数 + POST body | `--data-urlencode "a=1" "http://target/?id=1"` | POST | URL + body |
> | 同上，不想手拼 URL | `--url-query "id=1" --data-urlencode "a=1"` | POST | URL + body（curl ≥ 7.87） |
> | ❌ 以为能同时带 body | `-G --data-urlencode "a=1"` | GET | 全在 URL，body 为空 |
>
> 一句话：**`-G` = 数据搬去 URL + 方法变 GET；要 POST body 就别加它。**

`-d` 的三种取值形式：

```bash
-d "a=1&b=2"          # 直接写在命令里
-d @data.txt          # 从文件读（会把换行去掉，适合表单）
--data-binary @x.bin  # 从文件原样读（适合 JSON / 二进制）
```

### 2.2 带什么：请求头与身份

| 参数 | 作用 | 典型写法 | 常用度 |
|---|---|---|---|
| `-H` | 加请求头，可写多次 | `-H "Cookie: a=1" -H "X-Forwarded-For: 127.0.0.1"` | ⭐ 常用 |
| `-A` | 设置 User-Agent | `-A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"` | ○ 按需（等价 `-H`） |
| `-e` | 设置 Referer | `-e "http://target/admin.php"` | ○ 按需 |
| `-b` | 带 Cookie，可以是文件也可以是字符串 | `-b cookies.txt` / `-b "username=admin"` | ⭐ 常用 |
| `-c` | 把响应里的 `Set-Cookie` 存进文件 | `-c cookies.txt` | ⭐ 常用 |
| `-u` | Basic 认证 | `-u admin:123456` | ○ 按需 |

CTF 里最常伪造的几个头：

```bash
-H "Cookie: username=admin"
-H "X-Forwarded-For: 127.0.0.1"     # 伪装内网 IP
-H "X-Real-IP: 127.0.0.1"
-H "Referer: http://127.0.0.1/admin.php"   # 绕过 Referer 校验
-H "User-Agent: Mozilla/5.0"         # 绕过 UA 黑名单
```

> `-H "Cookie: ..."` 和 `-b` 等价，前者更灵活（能一次写多个头）。

### 2.3 怎么收：输出控制

| 参数 | 作用 | 什么时候用 | 常用度 |
|---|---|---|---|
| `-i` | 响应头 + 响应体一起打印 | 想看 `Set-Cookie` / `Server` / `Location` | ⭐ 常用 |
| `-I` | 只发 HEAD，只要响应头 | 快速看状态码和头，不下载内容 | ○ 按需 |
| `-s` | 静默：去进度条、去错误提示 | 脚本里用 | ⭐ 常用（配 `-S`） |
| `-S` | 与 `-s` 连用，把错误显示出来 | 永远写成 `-sS` | ⭐ 常用 |
| `-v` | 调试模式，打印完整请求/响应报文 | 排查「为什么服务端没收到我的参数」 | ⭐ 常用 |
| `-o 文件` | 响应体写入指定文件 | `-o resp.html` | ⭐ 常用 |
| `-O` | 用远端文件名保存 | 下载文件时 | ○ 按需 |
| `-w "格式"` | 结束后按格式输出统计 | `-w "%{http_code}"` | ⭐ 常用 |
| `-D 文件` | 把响应头单独写到文件 | `-D headers.txt` | ○ 按需 |

`-w` 常用占位变量：

```
%{http_code}      状态码
%{size_download}  响应体字节数
%{time_total}     总耗时（秒）
%{url_effective}  最终 URL（配 -L 看跳到哪了）
%{content_type}   Content-Type
%{redirect_url}   重定向目标
```

批量探目录的标准写法（只输出状态码，不打印正文）：

```bash
curl -s -o /dev/null -w "%{http_code}  %{url_effective}\n" "http://target/admin.php"
```

### 2.4 连接、代理与重定向

| 参数 | 作用 | 说明 | 常用度 |
|---|---|---|---|
| `-L` | 跟随 3xx 跳转 | **登录题必加**，不加只看得到 302 | ⭐ 常用 |
| `--max-redirs N` | 最多跟几次 | 防跳转环 | ○ 按需 |
| `-k` | 忽略 HTTPS 证书错误 | 自签名证书靶场用 | ○ 按需 |
| `--connect-timeout 5` | 连接阶段超时 | 扫描时防长时间挂起 | ○ 按需 |
| `-m 15` | 整个请求超时 | 等价 `--max-time` | ⭐ 常用 |
| `-x http://127.0.0.1:7890` | 走代理 | 需要科学上网/抓包时 | ○ 按需 |
| `--noproxy '*'` | **本次请求不走代理** | 环境变量里有 `http_proxy` 时强制直连 | ○ 按需（排 502 时用） |
| `--resolve host:port:ip` | 强制把域名解析到指定 IP | 测虚拟主机、绑 host | ○ 按需 |

代理这条是踩过的真坑：环境里存在 `http_proxy=127.0.0.1:xxxx` 时，`curl` 会默认走它，代理挂了就返回 `502 Bad Gateway`，看起来像靶机挂了。判断方法：

```bash
curl -v http://target/ 2>&1 | head -5
# 出现 "Uses proxy env variable http_proxy == ..." 就是走了代理
curl --noproxy '*' -v http://target/   # 强制直连对比
```

### 2.5 其他

| 参数 | 作用 | 常用度 |
|---|---|---|
| `--compressed` | 自动请求并解压 gzip/deflate/br | ○ 按需 |
| `--http1.1` | 强制 HTTP/1.1（有些靶场对 HTTP/2 处理异常） | ○ 按需 |
| `-T 文件` | PUT 上传 | ○ 按需 |
| `-r 0-99` | 只取前 100 字节（Range） | ○ 按需 |
| `--trace-ascii out.txt` | 把完整流量存文件，排查二进制/编码问题 | ○ 按需 |

---

## 3. 逐字拆解一条真实命令

```bash
curl -s -H "Cookie: username=admin" http://challenge.qsnctf.com:59051/index.php
```

| 片段 | 含义 | 去掉会怎样 |
|---|---|---|
| `curl` | 调用 curl 程序 | — |
| `-s` | 静默，不打印进度条 | 终端多出 `% Total % Received` 几行，结果一样 |
| `-H "Cookie: username=admin"` | 加一个请求头，内容是 Cookie | 服务端收不到 Cookie，返回「请先登录」 |
| `http://...index.php` | 目标 URL，放最后 | 没有目标，curl 直接报错 |

这条命令之所以能拿 flag，是因为服务端直接信任了 Cookie 里的 `username`，而 Cookie 是客户端完全可控的输入。

---

## 4. 八个必踩的坑

1. **PowerShell 里 `curl` 不是 curl**。它是 `Invoke-WebRequest` 的别名，不认 `-H`/`-d` 这套参数。写 `curl.exe`，或者用 Git Bash。
2. **`-s` 会把错误一起吞掉**。请求失败时终端一片空白，容易误判成「靶机没响应」。永远用 `-sS`。
3. **`-d` 会偷偷把方法变成 POST**。想发**纯 GET** 带参数，要么直接写进 URL，要么 `-G -d`；要保留 POST body 就别加 `-G`。
4. **`&` 是 shell 的特殊字符**。`-d "a=1&b=2"` 必须加引号，否则 shell 把 `&` 当后台执行符，命令会被切成两半。
5. **不加 `-L` 只能看到 302**。登录成功后跳转的题，不加 `-L` 会以为「登录失败」。
6. **`-d` 会吃掉换行**。发 JSON 用 `--data-binary` 或 `--json`，否则多行 JSON 变成一行还丢缩进。
7. **代理环境变量会劫持请求**。见 2.4，返回 `502` 先怀疑代理，不是靶机。
8. **`-G` 会把 body 搬空**。它不是「POST 转 GET」的开关，而是把 `-d` / `--data-urlencode` 的数据全部移到 URL，并改用 GET。想同时带 GET 查询参数和 POST body，**不要加 `-G`**，把查询参数直接写进 URL。

---

## 5. 模板变体

**① 只探测存活与状态码**

```bash
curl -sS -o /dev/null -w "%{http_code}  %{size_download}B  %{url_effective}\n" "http://target/index.php"
```

**② GET 带参数（含中文/特殊符号）**

```bash
curl -sS -i -G --data-urlencode "q=1' or '1'='1" --data-urlencode "page=1" "http://target/search.php"
```

**③ POST 表单（登录、传参）**

```bash
curl -sS -i -c cookies.txt -X POST \
  --data-urlencode "username=admin" \
  --data-urlencode "password=admin" \
  "http://target/login.php"
```

**④ 带会话继续访问**

```bash
curl -sS -i -b cookies.txt "http://target/index.php"
```

**⑤ 文件上传**

```bash
curl -sS -i -b cookies.txt -F "file=@shell.php;type=image/jpeg" "http://target/upload.php"
```

**⑥ JSON 接口**

```bash
curl -sS -i -X POST \
  -H "Content-Type: application/json" \
  --data-binary '{"username":"admin","role":"admin"}' \
  "http://target/api/login"
```

**⑦ 批量扫路径（读字典）**

```bash
while read p; do
  code=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 6 "http://target/$p")
  [ "$code" != "404" ] && echo "$code  $p"
done < paths.txt
```

**⑧ 同时带 GET 查询参数和 POST body**

```bash
curl -sS -i -L -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "username=admin" \
  --data-urlencode "password=123456" \
  "http://target/login.php?id=1&debug=1"
```

- `?id=1&debug=1` → 服务端的 `$_GET`
- `--data-urlencode ...` → 服务端的 `$_POST`
- 不要在中间加 `-G`，否则两个参数都会跑到 URL，POST body 变空

---

## 6. 一页速查

```
curl  URL  [怎么发] [带什么] [怎么收]

怎么发  -X POST | -d "k=v" | --data-urlencode "k=v" | -F "f=@文件" | -G（仅纯 GET）
带什么  -H "K: V" | -b cookie文件 | -c 存cookie | -A UA | -e Referer | -u 用户:密码
怎么收  -i 带头 | -I 只要头 | -sS 静默但报错 | -v 调试 | -o 存文件 | -w 统计
连接    -L 跟跳转 | -k 忽略证书 | -m 超时 | --noproxy '*' 不走代理
```

> 记住一句话：**curl 是「手工拼一个 HTTP 请求」，参数只是决定这个请求长什么样。**
> 看不懂某个参数时，`-v` 打一遍，报文里就能看到它到底改了什么。

---

相关：`Web最小工具集速查卡.md`（做题抄命令版）、`../02-HTTP与请求基础/Web笔记16-HTTP请求要素速查.md`（请求头/状态码对照）。

> 返回总入口：`../../README.md`
