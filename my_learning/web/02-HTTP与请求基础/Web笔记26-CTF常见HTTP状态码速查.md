# 🗂 Web 笔记 26｜CTF 常见 HTTP 状态码速查（3xx/4xx/5xx 与绕过）

> 记录自：qsnctf 40832「HTTP 请求方法猜谜」等实战 ｜ 2026-08-18 ｜ 做题时沉淀
> 适用：任何「服务器不回正常内容 / 页面行为怪异」的题，先看状态码再猜考点
> 与笔记16 的关系：16 讲「请求怎么伪造」，本篇讲「服务器回给你的三个数字代表什么、怎么顺着它打」

---

## 一、状态码本质（30 秒理解）

响应行长这样：`HTTP/1.1 403 Forbidden` —— **状态码 = 服务器对这次请求的一句话总结**。

| 分类 | 含义 | 一句话记忆 |
|---|---|---|
| **1xx** | 信息性（还在继续） | 还没结束，别慌 |
| **2xx** | 成功 | 一切正常 |
| **3xx** | 重定向 | 你找的地方挪走了 |
| **4xx** | 客户端错误 | 你的请求有问题 |
| **5xx** | 服务器错误 | 服务器自己炸了 |

> 💡 做题第一步永远是 `curl -i URL` 看**状态码 + 响应头**，别只盯着页面文字。状态码常常直接告诉你考点（405 = 让你换方法，403 = 让你伪造身份）。

---

## 二、CTF 高频状态码详解（★=重点）

### 3xx 重定向（★★ 常考）

| 码 | 名称 | 含义 | CTF 考点 |
|---|---|---|---|
| **301** | Moved Permanently | 永久重定向 | 和 302 一样看 Location 头 |
| **302** | Found | 临时重定向 | ★ 最常见：flag 藏在跳转**前**的响应体，或 Location 参数可控（SSRF/开放重定向） |
| 303 | See Other | 重定向后用 GET | 少见 |
| 304 | Not Modified | 命中缓存，没变化 | 看到它不是错——一般是 `If-Modified-Since`/`If-None-Match` 触发的，清缓存重试 |
| **307/308** | Temporary/Permanent Redirect | 重定向但**保留方法和请求体** | 踩坑点：POST 数据没跟过去，绕不过鉴权 |

> 💡 307 和 302 的区别：302 重定向时很多客户端会把 POST 变 GET、丢掉 body；307/308 原样转发。做题时 307 还在丢 body = 你的请求头/方法没对。

### 4xx 客户端错误（★★★★ 考点密集区）

| 码 | 名称 | 含义 | CTF 考点 |
|---|---|---|---|
| **400** | Bad Request | 请求语法错 | URL 编码错误、Cookie 格式错、POST 体格式错；提示你「请求没拼对」 |
| **401** | Unauthorized | 未认证 | ★ 响应头带 `WWW-Authenticate: Basic realm=...` → 要发 `Authorization: Basic base64(用户名:密码)` |
| **403** | Forbidden | 有资源但没权限 | ★★ 高频！目录限制 / IP 限制 / UA 限制 / Referer 限制 → 伪造身份或绕过（见第三节） |
| **404** | Not Found | 不存在 | 目录扫描时注意：很多工具把 403 报成 404，别漏 |
| **405** | Method Not Allowed | 方法不允许 | ★★ 高频！响应头 `Allow: GET, POST, ...` 直接给出可用方法；换方法重试（见第三节） |
| **406** | Not Acceptable | Accept 头不可接受 | 改 `Accept` 头（如要求 JSON：`Accept: application/json`） |
| 413 | Payload Too Large | 请求体太大 | 上传题：文件太大被拒，或提示该走别的方式 |
| 414 | URI Too Long | URL 太长 | 参数塞太多时出现；改用 POST |
| 415 | Unsupported Media Type | Content-Type 不对 | 改 `Content-Type: application/json` / `multipart/form-data` |
| **426** | Upgrade Required | 要求升级协议 | 少见但考过：把 HTTP/1.0 改 1.1，或加 Upgrade 头 |
| **429** | Too Many Requests | 限速 | ★ 爆破触发；放慢速度、换 UA/IP、加延时重试 |
| 431 | Request Header Fields Too Large | 请求头太大 | 头塞太多 |

> ⚠️ 418 I'm a Teapot 是 HTTP 彩蛋，不是错误——真有题拿它当考点（问你认不认识它）。

### 5xx 服务器错误（★★ 报错泄露考点）

| 码 | 名称 | 含义 | CTF 考点 |
|---|---|---|---|
| **500** | Internal Server Error | 服务器内部错误 | ★ 报错页可能泄露**绝对路径、函数名、SQL 语句**；触发它：传特殊字符、改参数类型、传空值 |
| 501 | Not Implemented | 方法未实现 | 换方法 |
| **502** | Bad Gateway | 网关/后端挂了 | 反向代理场景（nginx 后面服务崩了）；提示「后端服务」存在 |
| **503** | Service Unavailable | 服务不可用 | 少见但考过：加参数/改方法/改 Referer 可绕过（出题人故意让你加条件） |
| 504 | Gateway Timeout | 网关超时 | 后端卡死（可配合命令执行耗时间） |
| 505 | HTTP Version Not Supported | 协议版本不支持 | 改 HTTP 版本（如 0.9 / 1.0 / 2.0） |

---

## 三、状态码背后的 7 个题型套路（核心）

### 1. 405 → 换方法（方法猜谜题）
- 特征：`wrong request method` / `Method Not Allowed`。
- 解法：先 `OPTIONS` 探测或看 `Allow` 头，再逐个试方法全家桶：
```bash
for m in POST PUT DELETE PATCH OPTIONS TRACE CONNECT PROPFIND; do
  echo "== $m =="; curl -s -X "$m" URL
done
```
- 实战：qsnctf 40832，GET 提示 wrong request method，换 **POST** 直接出 flag（见同目录 WP）。
- 提示信号：「试 N 次后给 hint」= 出题人默认你在浏览器瞎点，提示你换工具。

### 2. 403 → 伪造身份（权限/来源校验）
- 特征：页面/接口提示无权限、只允许本地访问、只允许某来源。
- 解法（按顺序试）：
```bash
curl -H "X-Forwarded-For: 127.0.0.1" URL      # 伪造成本地
curl -H "X-Real-IP: 127.0.0.1" URL            # nginx 常用这个
curl -H "Client-IP: 127.0.0.1" URL
curl -H "Referer: http://内部域名/" URL        # 伪造成站内跳转
curl -H "User-Agent: Googlebot" URL           # 伪装搜索引擎
```
- 目录 403 的绕过：`/admin` → `/admin/`（补斜杠）、`//admin`、`/admin/.`、`/ADMIN`（大小写）、URL 编码（`%61dmin`）。
- ⚠️ 目录扫描时把 403 和 404 分开记录——**403 说明路径存在但权限不够，往往就是考点**。

### 3. 401 → Basic 认证爆破
- 特征：响应头有 `WWW-Authenticate: Basic realm="..."`。
- 解法：
```bash
# 用户名:密码 先 base64，再放 Authorization 头
echo -n "admin:admin" | base64
curl -H "Authorization: Basic YWRtaW46YWRtaW4=" URL
```
- 弱口令字典爆破：常见 `admin/admin`、`admin/123456`、`root/root`。

### 4. 302/301 → 抓跳转（重定向题）
- 特征：访问页面自动跳到别处，但 flag 可能就藏在**跳转前的响应体**里。
- 解法：
```bash
curl -i URL                # 不跟随，直接看状态行 + Location + 响应体
curl -v URL                # 看更详细
curl -L URL                # 需要时再跟随
```
- Burp Repeater 默认会显示跳转后的结果——**记得看历史/关掉 follow redirects**，跳转前的响应才有 flag。
- Location 参数如果可控（`?url=xxx`），可能是开放重定向 / SSRF 考点。

### 5. 500 → 报错信息泄露
- 特征：正常请求 200，传特殊参数后 500。
- 作用：报错页会暴露**绝对路径**（`/var/www/html/...`）、**函数名**、**SQL 语句**、甚至**源码片段**——这些都是下一步利用的弹药。
- 触发方式：给数字参数传字符串、传空、传超长、传数组（`?id[]=1`）、传特殊字符（`'` `"` `\`）。

### 6. 503 → 条件绕过
- 特征：页面提示服务不可用 / 维护中，但有时**只是某个条件没满足**。
- 解法：加参数（`?debug=1`）、换方法、换 Referer/UA，逐个试。
- 判断依据：状态码是 503 但页面内容「像提示」而不是「真错误页」，多半能绕。

### 7. 429 → 限速（爆破提示）
- 特征：爆破打太快返回 429。
- 解法：加 `--rate` 限速、换 UA/IP、加随机延时；或者这说明**该换思路**（不走爆破，走别的漏洞点）。

---

## 四、curl 看状态码的命令（速查）

```bash
curl -s -o /dev/null -w "%{http_code}\n" URL   # 只输出状态码
curl -i URL                                     # 完整响应（状态行+头+体）
curl -v URL                                     # 更详细（含请求头，排错用）
curl -L URL                                     # 跟随重定向
curl -s -X OPTIONS URL -i                       # 探测允许的方法（看 Allow 头）
```

---

## 五、速查卡（贴墙用）

```
状态码 = 服务器对请求的一句话总结:  1xx 信息 / 2xx 成功 / 3xx 重定向 / 4xx 客户端错 / 5xx 服务器错

405 换方法:      Allow 头给答案, 全家桶逐个试 (POST/PUT/PATCH/DELETE/OPTIONS/TRACE)
403 伪造身份:    X-Forwarded-For / X-Real-IP / Client-IP = 127.0.0.1, 改 Referer/UA
401 Basic认证:   Authorization: Basic base64(用户名:密码)
302 抓跳转:      curl -i 看 Location 和跳转前响应体, Burp 记得关跟随
500 报错泄露:    传特殊参数触发, 收集路径/函数名/SQL 当下一步弹药
503 条件绕过:    加参数 / 改方法 / 改 Referer 逐个试
429 限速:        放慢 / 换 IP / 换 UA, 或换思路别死磕爆破
406 改 Accept:   Accept: application/json
415 改类型:      Content-Type: application/json / multipart/form-data
一句话:         状态码是线索不是终点 —— 顺着它找「服务器在校验什么」
```
