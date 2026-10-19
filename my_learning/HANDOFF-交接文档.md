# 📋 交接文档｜CTF 学习进度 Handoff

> 最后更新：2026-08-15
> 交接人：Claude（2026-08-01 起）→ opencode 老师持续带教中
> 当前进度：Web 入门 24 题（NSSCTF 11 + CTF-Show 2 + DASCTF 5 + qsnctf 6）
> 专栏位置：敏感信息泄露 ✅ → RCE 基础 ✅ → 文件包含/LFI ✅ → 任意文件读取 ✅ → 反序列化 ✅ → SSRF ✅ → 文件上传 ✅ → sqlmap ✅
> 下一步：SSTI 专栏 / 盲注加深 / 内网渗透进阶

---

## 一、学生档案

- **身份**：CTF 零基础起步的新手，学习热情高、爱提问、较真
- **编程基础**：会一点，Python 正在学（会写简单脚本）
- **目标**：打 CTF 比赛（以比赛为导向）
- **环境**：Windows 10，未装 Linux/WSL/Docker
- **学习偏好**：边做边学 > 纯理论；每道题要复盘；**要求"掰碎讲解"和"极简流程版"**（信息密度大时会晕，需要：①从零重走流程 ②故事线式极简讲解 ③对比演示 ④工具/模板固化套路）
- **重要**：学生要求"老师直接演示解题 + 事后拆解每个为什么"，对"为什么"极其较真

---

## 二、环境与工具现状（Windows 10）

| 工具 | 状态 | 说明 |
|---|---|---|
| Python 3.13 + requests | ✅ | 主要脚本语言（还有 pillow、itsdangerous、biplist） |
| curl.exe | ✅ | 发请求主力（PowerShell 必须写 curl.exe） |
| git + Git Bash | ✅ | 终端 + git 操作 |
| git-dumper | ✅ | .git 泄露下载 |
| flask-unsign | ✅ | Flask cookie 解/爆/签 |
| sensitive_scan.py | ✅ 自写 | 敏感文件扫描 + robots 解析 + 搜 flag + .git 自动下载搜索 |
| combine_scan.py | ✅ 自写 | 目录扫描 + 敏感文件探测 二合一 |
| git_search.py | ✅ 自写 | git 仓库全版本自动搜 flag |
| mini_scanner.py | ✅ 自写 | 目录扫描器（防假200） |
| swp_extract.py | ✅ 自写 | .swp 恢复源码 |
| php_eval_chain.py | ✅ 自写 | $$...$_ 变量链 eval 通用模板（自动扫深度） |
| php_nested_eval.py | ✅ 自写 | 嵌套超全局变量链 exploit（中文 cookie 用） |
| forge_cookie.py | ✅ 自写 | Flask session 伪造通用脚本（payload 参数化；含原 N1Page 专用版功能） |
| post_demo.py | ✅ 自写 | 教学演示（GET/POST） |
| serforge.py | ✅ 自写 | PHP 序列化串构造器（自动算长度，支持 protected/private） |
| ssrf_scanner.py | ✅ 自写 | SSRF 万能探测器（验证/file/回环/内网/搜flag 五步全流程） |
| **工具箱说明书.md** | ✅ | 全部脚本的"怎么用"总手册（新约定：每个脚本必须带说明书） |
| Node.js v24 | ✅ | 执行 JS（JSFuck） |
| dirsearch | ❌ 不可用 | Python 3.13 不兼容，用 mini_scanner |
| HackBar / Burp | ⬜ 未装 | 学生已了解 HackBar 概念，待装 |

### 环境坑（接手者必看）
- Windows 用 `python` 不是 `python3`；PowerShell 里 `curl` 是别名 → 必须 `curl.exe`
- PowerShell 特殊字符地狱：`&`、`$`、嵌套引号 → **复杂 payload 一律写 Python 脚本文件**（多次踩坑）
- 中文 cookie 名（如 CTFshow-QQ群:）→ header 只能 latin-1 → 发 UTF-8 字节（%E7%BE%A4 或 http.client 原始字节）
- curl 输出过长终端截断 → `-o 文件` 再提取
- 假 200：服务器对不存在路径返回首页 → 对比内容判断

---

## 三、已完成题目（共 18 题）

### NSSCTF 入门题单（11 题，题单 14392）
| # | 题号 | 题目 | 考点 | flag |
|---|---|---|---|---|
| 1 | 3861 | 我Flag呢？ | 查看源代码 | （未记录） |
| 2 | 3862 | 就当无事发生 | .git 泄露 | （未记录） |
| 3 | 3863 | 导弹迷踪 | JS 硬编码 | `NSSCTF{y0u_w1n_th1s_!!!}` |
| 4 | 3871 | 1zjs | 注释+JSFuck | `NSSCTF{8d55061f-...}` |
| 5 | 3866 | Vim yyds | .swp+RCE | `NSSCTF{49196411-...}` |
| 6 | 3864 | Follow me and hack me | GET/POST | `NSSCTF{d0fc6c97-...}` |
| 7 | 3865 | PHP是世界上最好的语言 | RCE | `NSSCTF{44d076f7-...}` |
| 8 | 3867 | 作业管理系统 | 上传+任意读 | `NSSCTF{1bfb317b-...}` |
| 9 | 3868 | 这是什么？SQL注一下 | union注入 | `NSSCTF{9992a616-...}` |
| 10 | 3873 | Ping-Ping | 命令注入 | `NSSCTF{50998fb6-...}` |
| 11 | 3872 | Flask的session伪装 | cookie伪造 | `NSSCTF{48121a55-...}` |

### CTF-Show（2 题）
| # | 题目 | 考点 | flag |
|---|---|---|---|
| 12 | 嵌套eval的RCE | 超全局变量链+嵌套数组 | `ctfshow{94570b49-...}` |
| 13 | 变量的变量eval | extract+36层$$链 | `ctfshow{092ebb97-...}` |

### DASCTF（5 题，读文件系列）
| # | 题目 | 考点 | flag |
|---|---|---|---|
| 14 | 敏感文件 | flag拆分多文件泄露 | `n1book{info_1s_v3ry_imp0rtant_hack}` |
| 15 | Git测试 | .git 泄露 | `n1book{git_looks_s0_easyfun}` |
| 16 | p参数文件包含 | LFI+php://filter | `n1book{afr_1_solved}` |
| 17 | u1s1 | nginx alias 穿越 | `n1book{afr_2_solved}` |
| 18 | N1Page | 穿越+Flask伪造+SSTI 组合 | `n1book{afr_3_solved}` |

### qsnctf（6 题，08-15）
| # | 题目 | 考点 | flag |
|---|---|---|---|
| 19 | 40507 反序列化绕过黑名单 | unserialize+黑名单filter | `flag{3d98dbb9832e445a904193aae6c06d8d}` |
| 20 | 40514 文件包含data协议 | LFI+黑名单绕过 | （见WP） |
| 21 | 40515 反序列化POP链 | __destruct/__toString+eval | `flag{544d4a6f5fc54e888f0862c8ff8de015}` |
| 22 | 40517 SQL注入登录绕过 | error/time盲注+sqlmap | `flag{eb343e3467ad4ccf8abfe1c065c6a90a}` |
| 23 | 40536 文件上传gets hell | 路径穿越+解析绕过 | `flag{3ff4d00c191847bb9898b1da0ff3ea6b}` |
| 24 | 40555 SSRF绕过回环 | 回环黑名单→172.17.0.1网关→内网容器 | `flag{aeab080a8087419db1b0618981912d86}` |

> 备注：08-10 的 qsnctf 搜索引擎题（盲注）靶机已过期，脚本已清理（2026-08-15）。
> NSSCTF 题单：https://www.nssctf.cn/problem/sheet/14392

---

## 四、已学知识清单（按难度递进）

1. **查看源代码**（F12/Ctrl+U 注释藏 flag）
2. **.git 源码泄露**（git log/show 翻历史）
3. **JS 硬编码 flag**（grep 搜索；万能正则）
4. **JSFuck**（`[]()!+` 混淆，eval 执行）
5. **.swp 泄露**（交换文件提取源码）
6. **命令执行 RCE**（eval/system/shell_exec）
7. **HTTP 基础**（GET/POST/cookie/状态码 2xx-5xx）
8. **文件上传 + 任意文件读取入门**（目录穿越）
9. **SQL 注入入门**（union、括号绕过、注释）
10. **目录扫描原理**（词表穷举、假 200）
11. **前端校验绕过**（JS 只拦浏览器，curl/HackBar 直连）
12. **命令注入进阶**（`;` `&&` `||` `|`、无空格 `cat</flag` `${IFS}`、BusyBox 识别）
13. **curl 系统学习**（万能骨架：怎么发/带什么/怎么收；GET 进 URL POST 进 body）
14. **cookie/session 概念**（无状态 HTTP、Set-Cookie、存单/带单）
15. **Flask 识别 + session 伪造**（三段式、HMAC 签名、弱密钥爆破、重签名）
16. **PHP 基础速查**（超全局变量、危险函数表、读题三步法）
17. **敏感信息泄露 12 种**（注释/JS/.git/.svn/.hg/.DS_Store/.bak/robots/SSL/历史/接口/.swp）
18. **flag 拆分套路**（多文件各藏一段，l33t 命名、诱饵 env）
19. **.git 泄露完整流程**（HEAD 验证→git-dumper→git_search 自动搜）
20. **LFI 文件包含**（php://filter 读源码、include 机制、base64 消磁原理）
21. **任意文件读取家族**（路径穿越/LFI/nginx alias 穿越）
22. **nginx 基础**（root vs alias 映射、目录列表 autoindex、配置错误漏洞）
23. **/proc/self 系列**（cwd/cmdline/environ 读源码技巧）
24. **SSTI 初步**（render_template_string、{{}} 执行、__class__.__mro__.__subclasses__ 链）
25. **攻击面转移**（表单过滤 → 伪造 session 绕过）

### 已建立的核心方法论
- **三步法**：自己试 → 搜 → 看 WP 合上重做
- **解题链思维**：信息收集 → 分析 → 利用 → 拿 flag
- **黑盒推断 + 对比实验**（带/不带、存在/不存在）
- **实测原则**（参考解答也验证）
- **读源码 = 设计图**（能读文件先读主文件）
- **三问法**：目标文件是什么？被什么堵住？有没有侧门？
- **工具固化套路**（每类漏洞沉淀脚本）
- **命令不背原理要懂**（查速查卡）

---

## 五、已建笔记与工具

```
my_learning/
├── README.md                    ← 进度总表（18 题清单）
├── HANDOFF-交接文档.md           ← 本文件
├── 知识图谱-Web入门.md           ← 总览一张图
├── 收藏夹-参考资料.md            ← 题解/教材链接
└── web/
    ├── Web笔记01~04             ← 早期：敏感信息/HTTP/目录扫描/RCE速查
    ├── Web笔记05-发请求与命令注入重点.md
    ├── Web笔记06-PHP快速入门速查.md
    ├── Web笔记07-敏感信息泄露速查表.md
    ├── Web笔记08-工具箱手册.md
    ├── Web笔记09-Git泄露解题手册.md
    ├── Web笔记10-文件包含LFI解题手册.md
    ├── Web笔记11-nginx基础与alias穿越.md
    ├── Web最小工具集速查卡.md     ← curl 万能骨架
    ├── WP-[NSSCTF]Ping-Ping-命令注入.md
    ├── WP-[NSSCTF]Flask的session伪装-弱密钥伪造.md
    ├── WP-[CTF-Show]嵌套eval的RCE.md
    ├── WP-[CTF-Show]变量的变量eval.md
    ├── WP-[DASCTF]敏感文件.md
    ├── WP-[DASCTF]Git测试.md
    ├── WP-[DASCTF]p参数文件包含.md
    ├── WP-[DASCTF]u1s1-nginx-alias穿越.md
    ├── WP-[DASCTF]N1Page-全案笔记.md   ← 组合题全案（含所有概念）
    ├── sensitive_scan.py / combine_scan.py / git_search.py
    ├── mini_scanner.py / swp_extract.py / post_demo.py
    ├── php_eval_chain.py / php_nested_eval.py / forge_cookie.py
    └── （ds_store 解析：临时脚本，未留存）
```

---

## 六、当前进度 & 下一步建议

**2026-08-03 重做 N1Page（追加记录）**：
- 用真实靶机完整重走 18 题 N1Page，flag 复现：`n1book{afr_3_solved}`
- **实测推翻初版猜测**：cwd 真实路径 = `/home/sssssserver`（不是源码硬编码的 `/home/nu11111111l`）→ WP 2.2 已修正为证据版目录树
- 新发现：`/proc/self/environ` 里的 `FLAG=CTF2{...}` 是**诱饵 flag**（平台陷阱，提交不算数）
- 新技能：报错信息泄露画地图（`[Errno 2]` 泄露真实拼接路径）
- 新增工具：`forge_cookie.py`（Flask session 伪造通用脚本）
- 新笔记：`Web笔记12-服务器架构与文件系统.md`（"服务器"三义/接待员+厨师/一棵树理论/读源码扫雷/三兄弟区分表）
- 教学动作：针对学生"力竭"做了全部知识点落档；下一步复习用笔记12+N1Page WP

**2026-08-03 追加（SSRF 题 + XSS 七关 + SQL 注入系）**：
- DASCTF SSRF 题（内网IP绕过）：flag `n1book{ug9thaevi2JoobaiLiiLah4zae6fie4r}` → WP 已写
- DASCTF XSS 七关训练（6种XSS手法）：flag `n1book{xss_is_so_interesting}` → WP 待写
- DASCTF login 报错注入：flag `n1book{login_sqli_is_nice}` → WP 待写
- DASCTF notes union注入：flag `n1book{union_select_is_so_cool}` → WP 已写
- 新增工具：`page_scan.py`（页面源码侦察器，抓注释/表单/JS/关键词）、`forge_cookie.py`
- 新增笔记：`Web笔记13-sqlmap速查.md`；工具箱手册补三扫描器分工+combine盲区
- 外部工具：sqlmap 已装（含 `--tamper=randomcase` 绕过大小写过滤）
- 学生已会：手动 SQL 注入（union/报错）、sqlmap 梭哈、SSRF 绕过原理、XSS 基本概念
- 已学漏洞面：RCE / LFI / 任意文件读 / SQL注入 / SSRF / XSS 入门
- **2026-08-04 NN007路由器题（命令注入+布尔盲注提取）**：flag `n1book{6fa82809179d7f19c67259aa285a7729}` → WP 已写
  - 新套路：换行绕过过滤、退出码布尔oracle、dd+printf+cmp逐字节提取、`-`被拦改用无`-`写法、大写FLAG文件名坑
  - 新增工具：`blind_rce_extract.py`（布尔盲注逐字节提取引擎，常备）
  - 学生状态：这题耗时耗神，首次盲注提取，自述"很可怕"，已安抚并鼓励——标记为"硬核但套路化"，下次遇同类题直接套模板
  - 情绪记录：题目难度叠加时学生容易崩，用"拆层看都有旧知识+已有模板"来缓解

**2026-08-06 qsnctf XSS 十关（反射型XSS入门）** → 精细笔记已写
  - L1~L10 全通；L6（on/src/data/href子串过滤）现代浏览器卡关未解
  - 新套路：撬引号 / 事件属性(autofocus onfocus) / javascript伪协议 / 实体编码救值 / 双写绕过(scrscriptipt) / //注释骗URL校验 / type覆盖hidden / 第二反射点(href)
  - 学生本次领悟的三条铁律：①值能救属性名不能救（实体编码只对值有效）②过滤器看字符串浏览器执行 ③执行上下文决定过关（父页面vs iframe原生alert）
  - 新增笔记：`WP-[qsnctf]XSS十关-精细笔记.md`（教材级，12章）
  - 情绪：L5~L10 连续关卡学生喊"真他妈难/恶心"，但啃完后自己推导出"值vs属性名"规律，已大大鼓励
  - 学生需求：要求"精细笔记"（不是随便两下），已满足；以后笔记要写透每关：题目面貌/探测/过滤结论/解法/原理/拓展/复盘

**2026-08-10 RCE 过滤绕过（handoff 下一步 #1 开练）** → 新靶机 + 新笔记
  - 方向：接手老师按 handoff「下一步 #1」开 RCE 进阶层，专攻最实用的「过滤绕过」一块（空格/分隔符/关键字/无回显），高级货（FastCGI/Redis/GC UAF/Java反射）留到后面
  - 新建本地靶机：`web/lab_rce_bypass.py`（纯 Python + `bash -c` 执行，5 关 lv0-lv4，每关**只拦一种**隔离练；lv4 无回显配合 `/read?f=` 取回）
    - 为什么用 bash -c：真实 RCE 跑在 Linux sh/bash，绕过手法是 Shell 层；学生 Windows 用 Git Bash 跑，`bash -c` 行为=真实靶机，无需装 PHP/Docker
    - 每关预期结果已实测：lv0 `127.0.0.1;cat%20secret.txt`、lv1 `cat<secret.txt`、lv2 `c""at secret.txt`、lv3 `127.0.0.1%0acat secret.txt`、lv4 `cat secret.txt > out.txt` + `/read?f=out.txt` 全部出 flag
  - 实测验证的**可靠套路**：空格→`cat<f`/`cat${IFS}f`/`ca$@t<f`；cat→`c""at f`/`c''at f`/`ca$@t f`/通配`*`；分隔符→`%0a`换行；无回显→`> out.txt`
  - 实测验证的**翻车反例**（当教学点）：`c\at` 时灵时不灵（`\a`=响铃符）；`c${IFS}at` 变 `c at` 两词直接废
  - WAF 拦截逻辑用纯正则测 10 组全 PASS（沙箱限制：后台进程不能再套娃起子进程，故靶机 HTTP 自测超时，但绕过语法前台 bash 实测全过；学生本机 Git Bash 跑正常）
  - 新笔记：`Web笔记14-RCE过滤绕过速查.md`（心法 + 四类绕过 + 翻车反例 + 靶机用法 + 速查卡）
  - 学生状态：本会话为「阅读交接文档后续学」首节；学生未在线实操，仅完成备课（靶机+笔记+图谱+HANDOFF）。下一步让其本机跑靶机、逐关实打。
  - 情绪/需求：沿用全部教学约定（一步一步/思路→命令→预期→拓展/每日收尾三处记录/精细笔记优先）

**2026-08-10 qsnctf 实战第1题：PHP 8.1.0-dev 后门 RCE** → WP 已写
  - 靶机：http://challenge.qsnctf.com:39928/，flag `flag{dea4a9c80d994f95ae45655f9f520077}`
  - 解法链：响应头 `X-Powered-By: PHP/8.1.0-dev` + 页面提示「你应该知道这是哪个版本的PHP吧！」→ 识别 2021-09 源码投毒后门 → `-H "User-Agentt: zerodium<PHP代码>"` 即 RCE（root）
  - 新套路入库：**版本/指纹泄露 → 已知后门**（敏感信息泄露的第 13 种：版本号）；速查「X-Powered-By: PHP/8.1.0-dev → User-Agentt 双t + zerodium」
  - 新 WP：`web/WP-[qsnctf]PHP8.1.0-dev后门RCE.md`（精细：面貌/探测/解法/原理/拓展/复盘）
  - 教学方式：老师先实测拿 flag（含两种读法验证）→ 写 WP → 给一步一命令教案（学生本机照打）
  - 学生状态：待学生本机用 curl 走一遍全流程（版本识别→验证id→ls→cat flag）

**2026-08-10 qsnctf 实战第2题：It is DT's day 双文件上传（MD5碰撞+MIME伪造）** → WP 已写
  - 靶机：http://challenge.qsnctf.com:39929/，flag `flag{38f334ffb26d452e99033ad7fcd4d89d}`
  - 解法链：双文件上传(d1/d2) → 黑盒推断出三校验(内容不同→是PDF→MD5相同) → fastcoll 生成 MD5 碰撞对 → curl `-F ";type=application/pdf"` 伪造 MIME → 全过回显 flag（无需 getshell）
  - 关键实测结论：PDF 校验**只看 MIME type（浏览器可伪造），不查内容**（纯文本碰撞对也能过）；`/flag.php` 是诱饵
  - 工具：下载 fastcoll（GitHub 镜像 iamjazz/Md5collision，官网 win.tue.nl 已失效），沙箱无编译器故用 Windows exe
  - 新套路入库：报错信息=校验规则说明书；MIME 可伪造；MD5 判重可碰撞；双文件上传同 MD5 同内容校验
  - 新 WP：`web/WP-[qsnctf]DT上传-MD5碰撞.md`
  - 学生状态：待学生本机复现（fastcoll 生成对 + curl 上传）。**2026-08-10 记录：学生看到「两文件内容不同但 MD5 相同」的校验要求时喊"晕了"→ 已用「极简故事线 + 三步傻瓜流程（前缀→fastcoll→上传，含实时演示）」重新带过，学生要求先给"照抄就能用"的命令再讲原理。下次讲 MD5 碰撞先演示后理论。**
  - 教学全过程记录：学生连环提问「前缀是什么」「为什么两文件内容不同」「fastcoll 支持什么格式」「只改 Content-Type 行不行」→ 逐题掰碎回答（接力赛比喻讲 Merkle-Damgård、结构图可视化、实测证明 MIME 只过一道校验）。学生已理解：前缀=两文件共有开头、碰撞块=工具造的差异、MIME 可伪造但 MD5 必须靠碰撞对、扩展名无关。
  - 新交付：`md5coll/fastcoll使用说明书.html`（图文版说明书）+ `Web笔记15-MD5碰撞与假文件构造.md`（精细笔记：概念/用法/黑盒推断/魔数/MIME/坑/速查卡）

**2026-08-10 qsnctf 实战第3题：Login 布尔盲注** → 自写工具拖库，WP 已写
  - 靶机：http://challenge.qsnctf.com:39947/login.php，flag `flag{5b6bcba81cb0421192e890b0926b8ab}`
  - 解法链：登录页 `and 1=1#` vs `and 1=2#` 响应不同 = 布尔盲注 oracle → 自写 `sql_blind_extract.py`（二分搜长度+ASCII）→ 库 qsnctf → 表 users → 列 id,username,password → 拖出 flag（藏在 password 列）
  - 新工具：`web/sql_blind_extract.py`（SQL 布尔盲注提取引擎，通用模板，sqlmap 替代品）→ 已登记工具箱手册 12.5
  - 教学动作：学生原想用本地 sqlmap 梭哈 → 学生机器上 sqlmap 路径异常（沙箱视角缺 sqlmap.py，pip 版坏、git clone 慢）→ 学生喊「你做题呀」→ 老师直接用自写脚本解完，顺便固化新工具。**下次 sqlmap 不可用时的兜底路径 = sql_blind_extract.py**
  - 新 WP：`web/WP-[qsnctf]Login布尔盲注.md`
  - 学生状态：待学生本机用 sqlmap 或新工具自行复现
  - **2026-08-10 补充：学生已自行补齐本地 sqlmap 主文件（ctf_tools 路径，16:55，版本 1.10.7.253#dev，启动/版本输出正常，可用）。39947 靶机后续过期（HTTP 000），未及用 sqlmap 复测该题。下次打靶遇布尔盲注可先上 sqlmap 梭哈。**

**2026-08-10 qsnctf 实战第4题：登录页加密后门 + PHP 反序列化 POP 链** → WP 已写
  - 靶机：http://challenge.qsnctf.com:39967/，flag `flag{2a63616a95724195bee4971bebb6ce01}`
  - 解法链：所有注入测试响应 MD5 全同（排除 SQLi）→ `/www.zip` 源码泄露（robots 明示 qsnctf.php）→ 多层混淆 PHP（urldecode字母表+下标拼函数名+eval(base64)+strtr重排）→ 自写 `php_obf_decode.py` 解出明文 → `@unserialize($username)` 反序列化入口 → POP 链（wo:__destruct→inspect→echo触发 shi:__toString→next::PLZ(pass)→Demo:__callStatic→$b(pass)=password参数当函数）→ password=system → RCE → cat /flag
  - 新漏洞面：**PHP 反序列化 POP 链**（新！待系统学教材反序列化章节）；新工具：`php_obf_decode.py`（国产 CTF 混淆模板解码器）
  - 教学要点：响应完全不变 ≠ 没漏洞，先挖源码；www.zip/robots 是源码泄露三件套
  - 新 WP：`web/WP-[qsnctf]登录反序列化POP链.md`
  - 学生状态：学生未亲自操作（老师全流程代打+演示），待学生自己复现解码+构造 payload

**2026-08-10 qsnctf 实战第5题：穿梭隐藏的密钥（SSRF 绕过 + PHP 审计三连关）** → WP 已写
  - 靶机：http://challenge.qsnctf.com:39972/，flag（实测）`flag{4f4fcf4f5e45430589bcf62ef3b9210d}`
  - 解法链：c3s4f.php?shell= SSRF（字符串黑名单 WAF 拦 127 变体）→ **localtest.me/sudo.cc（A记录=127.0.0.1 且字符串干净）** 绕过 → secret.php 给 key=MSIBLG → cha11eng3.php 三连关：① DrKn=data://text/plain,MSIBLG（data 伪协议）→ key1=M_ore.8 ② M[ore.8=0e001233333333333334557778889（**方括号代替下划线**避「GET 参数名点转下划线」+ md4 0e 弱比较）→ wtf/mC ③ POST wtf[]=1&mC[]=2（数组：strlen=null 过长度、md5=null===null 过强比较）→ flag
  - 教学教训（老师亲踩）：SSRF 测试用例全部自带黑名单子串（127.0.0.1.nip.io 含 127 等）→ 误判 WAF 为 DNS 解析型；正确做法是测「字符串干净但解析到 127 的域名」。
  - 新套路：字符串黑名单 SSRF 用「指向 127 的干净域名」；data:// 伪协议；0e 魔法串；数组绕过。
  - 学生状态：学生提供题解（flag 为旧实例的），老师对活靶机全链实测拿到本实例 flag 并写 WP。

**当前位置**：
- 专栏：敏感信息泄露 ✅（教材读完+2题实战）→ RCE 基础 ✅（概念课）→ 文件包含 ✅（2题）→ 任意文件读取 ✅（3题）→ **RCE 过滤绕过 ✅（靶机+笔记已建，待学生实打）**
- 技术栈：PHP ✅ / Python-Flask ✅（识别+session+SSTI 初步）/ nginx 配置 ✅
- 工具链：扫描自动化（3 个扫描器）+ Flask 伪造 + LFI + eval 链模板

**建议下一步**（接手者按此带）：
1. **RCE 专栏进阶层**：空格/关键字绕过（%20、$IFS、通配符）、过滤绕过题目 —— 🔵 2026-08-10 已开（靶机+笔记14），待学生本机实打 lv0-lv4
2. **SSTI 专栏**（教材 ssti.md）：学生已在 N1Page 接触，正好系统化
3. SQL 注入加深（盲注/sqlmap）——题单剩余
4. 装 HackBar / Burp 抓包入门
5. 中期目标：独立打小型比赛

**学生状态记录（重要）**：
- 已能独立分析"读文件"类题；组合题（N1Page）会"晕"
- 晕时应对：①极简故事线重走 ②掰碎单个零件 ③比喻教学 ④让 TA 复述
- 爱问"为什么"，必须诚实回答（含"猜的/教材给的/实测的"区分）
- 喜欢把套路固化成工具/模板，反感重复劳动

---

## 七、教学约定（接手者保持一致）

1. 中文教学，多用比喻（大楼/厨师/前台/快递等固定比喻体系）
2. 动手 > 理论；每题复盘写 WP
3. 做题流程固定：信息收集 → 探测 → 分析 → 利用 → 复盘
4. 学生"晕"时：停下来，从零重走 + 极简故事线
5. 学生较真要"为什么"：耐心解答，诚实区分"推断/教材/实测"
6. 新会话接手：先读本文档 + README + 知识图谱
7. 复杂 payload 用 Python 脚本文件（PowerShell 引号地狱）
8. 每类新漏洞沉淀工具/模板
9. 对比演示讲概念（眼见为实）
10. **★一切指导都必须"一步一步来"**（2026-08-03 学生明确要求）：无论做题讲解、写 WP、记录笔记，都拆成小步。禁止一次甩一大坨。工具教程要给"照抄就能用"的完整命令 + 每步预期结果。
11. **★每一步必须写全「思路逻辑 → 命令 → 具体操作/预期结果」+ 中途拓展**（2026-08-03 深化）：
    - **思路逻辑**：这一步要干什么、为什么这么做（不只要"是什么"，要讲"为什么"）
    - **命令**：完整可复制的命令，PowerShell 里照抄就能用
    - **具体操作/预期结果**：动手要怎么做、敲完预期看到什么输出
    - **中途拓展**：碰到新知识点或卡点必须停下来单独展开讲清楚，讲完再回主线
12. **★输出节奏**（2026-08-03 修订）：学生**自己决定节奏**。默认把每一步都写全后**一次性全部输出**，学生慢慢看、不懂再问；**不要**每走一步就停下来等"看懂了吗"，那会太卡。学生若主动要求交互式再改。若中途产出大，可分几次输出，但每次都要给足某几步的完整内容。
13. **★每日收尾必记录**（2026-08-06 学生明确要求）：**每天练习结束，必须记录三处**：
    - **笔记/WP**：当天题目写 WP；知识密度大时写**精细笔记**（每关/每点写透：面貌/探测/结论/解法/原理/拓展/复盘，不糊弄）
    - **知识图谱**：更新题目地图、新套路、已学漏洞面
    - **HANDOFF 交接文档**：当天进度、新套路、工具、情绪记录、学生需求变化
    - 学生明确表示"要精细的笔记，不是随便写两下的"——笔记质量是第一优先级

---

## 八、已知坑 / 注意事项

- 靶机频繁过期断连（DASCTF/NSSCTF 都遇到）→ 做题抓紧，重启后地址和 flag 会变
- 教材 docs/ 是公开项目：新环境 `git clone https://github.com/ProbiusOfficial/Hello-CTF.git`
- GitHub raw 拉取可能被墙（SSL 错误）→ 工具用 pip 装，或自己写解析
- PowerShell：curl 别名、`&`/`$` 特殊字符、嵌套引号 → 用 curl.exe + 脚本文件
- 中文 cookie 名编码坑（见环境坑）
- dirsearch 不可用；扫描用自建三件套（sensitive/combine/mini）
- 学生情绪：信息密度大时"晕" → 放慢、拆零件、鼓励（N1Page 已验证有效）
