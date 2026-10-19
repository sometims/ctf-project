# 🗺️ CTF Web 知识库 · 总入口与知识图谱

> 老师：opencode（前任，Claude 交接）｜ 当前陪练：WorkBuddy
> 目标：CTF 比赛 ｜ 本库持续**不断完善**——每做一道题、补一个考点，就回来更新对应分类的 `README.md` 和本图谱。
>
> - 📌 **进度交接**：`HANDOFF-交接文档.md`（学生档案/环境/教学约定，新会话先读）
> - 🔖 **参考资料**：`收藏夹-参考资料.md`（题解/教材链接）
> - 🗂️ **旧版方法论文档**：`知识图谱-Web入门.md`（已整合进本文件，保留作历史参考）

---

## 一、目录结构（一目了然）

```
my_learning/
├── README.md                      ← 你正在看（知识图谱总入口）
├── HANDOFF-交接文档.md             ← 教学约定/学生档案
├── 收藏夹-参考资料.md               ← 外部题解/教材链接
├── 知识图谱-Web入门.md             ← 旧版方法论（已整合，保留）
└── web/                           ← 所有 Web 方向内容
    ├── 00-资料与工具/              ← 通用脚本+速查卡+工具说明书（跨题型）
    ├── 01-信息泄露与备份文件/      ← 看源码/注释/JS/备份/.swp
    ├── 02-HTTP与请求基础/          ← GET/POST/请求构造地基
    ├── 03-目录扫描/                ← 字典爆破+假200识别
    ├── 04-RCE与命令注入/           ← 命令拼接/eval链
    ├── 05-PHP基础/                 ← PHP语法速查（字典）
    ├── 06-Git泄露/                 ← .git恢复+搜flag
    ├── 07-文件包含LFI/             ← 伪协议/php://filter/data://
    ├── 08-nginx配置漏洞/           ← alias穿越/autoindex
    ├── 09-PHP反序列化/             ← POP链/魔法方法
    ├── 10-SQL注入/                 ← 联合/报错/盲注/sqlmap/WAF
    ├── 11-文件上传/                ← 解析绕过/.htaccess/路径穿越
    ├── 12-SSRF/                    ← 内网打穿/网关绕过
    ├── 13-Flask与Session/          ← session伪造/SSTI
    └── 14-综合组合题/              ← 多考点串联
```

**每个分类文件夹里**都包含：本题的 `WP-*.md`（题解）+ 相关 `Web笔记*.md`（方法论）+ 图片，以及一篇 `README.md` **分类说明书**（常考考点 / 解决方法 / 已收容题目）。

---

**CTF-Show（2 题）**
- [x] 嵌套eval的RCE（超全局变量链）→ `web/WP-[CTF-Show]嵌套eval的RCE.md` + `php_nested_eval.py`
- [x] 变量的变量eval（extract + 36层$$链）→ `web/WP-[CTF-Show]变量的变量eval.md` + `php_eval_chain.py`

**DASCTF（6 题，任意文件读取/文件包含 + SQL注入 系列）**
- [x] 敏感文件（flag 拆分多文件泄露）→ `web/WP-[DASCTF]敏感文件.md`
- [x] Git测试（.git 泄露）→ `web/WP-[DASCTF]Git测试.md`
- [x] p参数文件包含（LFI + php://filter）→ `web/WP-[DASCTF]p参数文件包含.md`
- [x] u1s1（nginx alias 穿越）→ `web/WP-[DASCTF]u1s1-nginx-alias穿越.md`
- [x] N1Page（穿越+Flask伪造+SSTI 组合题）→ `web/WP-[DASCTF]N1Page-全案笔记.md`
- [x] notes（union SQL注入 + sqlmap 梭哈）→ `web/WP-[DASCTF]notes-union注入.md`
- [x] SSRF（内网IP绕过）→ `web/WP-[DASCTF]SSRF-内网IP绕过.md`

**已学漏洞面**：RCE / RCE过滤绕过 / LFI / 任意文件读取 / SQL注入（union+报错+盲注） / SSRF（内网绕过） / XSS 入门 / 文件上传 / PHP版本后门（8.1.0-dev） / MD5碰撞+MIME伪造 / PHP反序列化POP链

**DASCTF XSS 七关训练（flag 已拿到）**
- [x] XSS 七关（6种XSS手法）→ flag `n1book{xss_is_so_interesting}`（WP 待写）

**DASCTF 其他（flag 已拿到）**
- [x] login 报错注入 → flag `n1book{login_sqli_is_nice}`（WP 待写）

**qsnctf XSS 挑战（10 关，反射型XSS入门）**
- [x] L1~L10 全通 → `web/WP-[qsnctf]XSS十关-精细笔记.md`（教材级：考点/思路/命令/原理/拓展）

**qsnctf 其他（11 题）**
- [x] PHP反序列化-pswd属性构造（unserialize 可控+filter形同虚设）→ `web/WP-[qsnctf]反序列化-pswd属性构造.md`
- [x] Flask文档查询（任意文件读取+/proc/1/environ真flag+no_FLAG假线索）→ `web/WP-[qsnctf]Flask任意文件读取-proc泄露.md`
- [x] RCE挑战（登录爆破+eval函数白名单绕过+f1ag数字1陷阱）→ `web/WP-[qsnctf]RCE挑战-白名单绕过与flag陷阱.md`
- [x] PHP 8.1.0-dev 后门 RCE → `web/WP-[qsnctf]PHP8.1.0-dev后门RCE.md`（版本泄露→User-Agentt头 zerodium RCE）
- [x] It is DT's day 双文件上传（MD5碰撞+MIME伪造）→ `web/WP-[qsnctf]DT上传-MD5碰撞.md`
- [x] Login 布尔盲注（自写提取引擎拖库）→ `web/WP-[qsnctf]Login布尔盲注.md`
- [x] Login 加密后门+反序列化 POP 链 → `web/WP-[qsnctf]登录反序列化POP链.md`（www.zip泄源码→混淆解码→POP链RCE）
- [x] 穿梭隐藏的密钥（SSRF绕过+data://伪协议+PHP审计三连关）→ `web/WP-[qsnctf]穿梭隐藏的密钥.md`
- [x] ping命令注入-分号过滤（源码开卷，`|`绕过）→ 与 LitCTF Ping-Ping 同族，见 `web/WP-[NSSCTF]Ping-Ping-命令注入.md`
- [x] ez_http 六连关（方法/参数/Referer/UA/XFF/Cookie）→ `web/WP-[qsnctf]ez_http六连关.md`
- [x] Directory Search（LFI+`....//`点斜杠穿越）→ `web/WP-[qsnctf]DirectorySearch-点斜杠穿越.md`
- [x] Sql Page（sqlmap梭哈+ctf库flag表+fake_flag陷阱）→ `web/WP-[qsnctf]SqlPage-sqlmap梭哈.md`
- [x] 文件包含大师（LFI+日志包含+蚁剑，双引号/反斜杠坑）→ `web/WP-[qsnctf]LFI日志包含蚁剑.md`
- [x] 上传-前端校验绕过（curl 绕过 JS，.php 直接过 → getshell）→ `web/WP-[qsnctf]上传-前端校验绕过.md`
- [x] 上传-Content-Type校验绕过（`;type=image/jpeg` 伪造传 .php）→ `web/WP-[qsnctf]上传-Content-Type校验绕过.md`
- [x] TYctf（extract变量覆盖+sha1弱比较数组绕过+call_user_func）→ `web/WP-[qsnctf]TYctf-变量覆盖与任意函数调用.md`
- [x] Monitor 目录浏览器监控（反序列化 POP 链 + 变量函数调用 system RCE）→ `web/WP-[qsnctf]反序列化变量函数调用RCE.md`

### 笔记（web/）
- [x] 01 敏感信息泄露与JS分析 ｜ 02 HTTP基础 ｜ 03 目录扫描 ｜ 04 RCE命令速查
- [x] 05 发请求与命令注入重点 ｜ 06 PHP快速入门速查
- [x] 07 敏感信息泄露速查表 ｜ 08 工具箱手册 ｜ 09 Git泄露解题手册
- [x] 10 文件包含LFI解题手册 ｜ 11 nginx基础与alias穿越
- [x] 12 服务器架构与文件系统（"服务器"三义/接待员+厨师/一棵树/读源码扫雷/三兄弟）
- [x] 13 sqlmap 速查（SQL注入一把梭，日常三连）
- [x] 14 RCE 过滤绕过速查（空格/分隔符/关键字/无回显 + 翻车反例 + 靶机用法）
- [x] 15 MD5碰撞与假文件构造（fastcoll/魔数/MIME伪造/上传黑盒推断）
- [x] 16 HTTP请求要素速查（四段式结构/7个可伪造要素/POST的&格式/伪造命令）
- [x] 17 sqlmap核心打法模板（四步下钻：固定前缀+4动作，配图 sqlmap四步下钻模板.svg）
- [x] 18 PHP伪协议大全（filter读源码/input POST-RCE/data注入/file/phar反序列化 + include结合场景表）
- [x] 19 Webshell速查（命令马/eval马/base64马 + 前端校验绕过 + 马的选择）
- [x] 20 Burp上传文件全攻略（multipart格式 + 拦截改包 + Repeater手写 + 常见坑）
- [x] 21 文件上传解题手册（五类校验+绕过速查表 + 做题流程 + 两题实战对比）
- [x] 22 PHP语法零基础速查（8符号/弱比较坑/危险函数全家桶/call_user_func/payload模板）
- [x] 23 Burp密码爆破全流程（Intruder 六步 + Length 排序认命中 + 字典位置 + 常见坑）
- [x] 15 MD5 碰撞 & 假文件构造（fastcoll 用法/能力边界 + MIME 伪造 + 魔数欺骗 + 上传黑盒推断）
- [x] 最小工具集速查卡（curl 万能骨架）

### 工具（web/）
- [x] page_scan.py（页面源码侦察器：注释/表单/JS/关键词）
- [x] sensitive_scan.py（敏感文件扫描 + .git 自动挖掘）
- [x] mini_scanner.py（目录扫描，防假200）
- [x] combine_scan.py（目录扫描 + 敏感文件 二合一）
- [x] git_search.py（git 仓库自动搜 flag：全版本+悬空对象+提交说明）
- [x] swp_extract.py（.swp 交换文件恢复源码）
- [x] php_eval_chain.py（$$变量链 eval 通用模板，自动扫深度；含原 ctfshow_dollar_eval 功能）
- [x] php_nested_eval.py（嵌套超全局变量链 exploit，中文 cookie 用）
- [x] forge_cookie.py（Flask session 伪造通用脚本，payload 参数化；含原 forge_n1code 功能）
- [x] blind_rce_extract.py（布尔盲注 RCE 逐字节提取引擎）
- [x] sql_blind_extract.py（SQL 布尔盲注提取引擎：二分搜长度+ASCII，通用模板）
- [x] php_obf_decode.py（PHP 混淆解码器：urldecode字母表+下标拼函数名+eval(base64)模板，国产CTF通用）
- [x] php_ser_builder.py（PHP 序列化 payload 生成器：JSON 规格→序列化串，反序列化/POP链题通用）
- [x] post_demo.py（GET/POST 教学演示）
- [x] lab_rce_bypass.py（本地 RCE 过滤绕过靶机：lv0-lv4 + /read，纯 Python+Git Bash 跑）
- [x] md5coll/（MD5 碰撞工具箱：fastcoll.exe + 现成碰撞对 m1/m2，配合 `;type=application/pdf` 伪造 MIME）
- 完整用法见 `Web笔记08-工具箱手册.md`

### 第三方工具（外部）
- [x] sqlmap（`C:\Users\Hong\Desktop\ctf_tools\web_tools\sqlmap-master\sqlmap-master\sqlmap.py`）—— SQL 注入梭哈
## 二、分类总表（考点 → 题数 → 入口）

| # | 分类 | 常考考点一句话 | 收容题数 | 说明书 |
|---|---|---|---|---|
| 00 | 资料与工具 | 通用脚本/速查卡/说明书 | 4 笔记+17 工具 | [README](web/00-资料与工具/README.md) |
| 01 | 信息泄露与备份文件 | 看源码/JS/注释/`.swp`/`.bak` | 5 | [README](web/01-信息泄露与备份文件/README.md) |
| 02 | HTTP与请求基础 | GET/POST/请求构造地基 | 3 | [README](web/02-HTTP与请求基础/README.md) |
| 03 | 目录扫描 | 字典爆破/假200识别 | 1 | [README](web/03-目录扫描/README.md) |
| 04 | RCE与命令注入 | 拼接符/无空格/`$$`链 | 9 | [README](web/04-RCE与命令注入/README.md) |
| 05 | PHP基础 | 超全局变量/危险函数/弱类型 | 2 | [README](web/05-PHP基础/README.md) |
| 06 | Git泄露 | `.git`恢复/仓库搜flag | 2 | [README](web/06-Git泄露/README.md) |
| 07 | 文件包含LFI | 伪协议/`php://filter`/`data://` | 9 | [README](web/07-文件包含LFI/README.md) |
| 08 | nginx配置漏洞 | `alias`穿越/autoindex | 2 | [README](web/08-nginx配置漏洞/README.md) |
| 09 | PHP反序列化 | POP链/魔法方法/属性覆盖 | 5 | [README](web/09-PHP反序列化/README.md) |
| 10 | SQL注入 | 联合/报错/盲注/sqlmap/WAF | 5 | [README](web/10-SQL注入/README.md) |
| 11 | 文件上传 | 解析绕过/`.htaccess`/路径穿越 | 6 | [README](web/11-文件上传/README.md) |
| 12 | SSRF | 内网打穿/网关绕过 | 2 | [README](web/12-SSRF/README.md) |
| 13 | Flask与Session | session伪造/SSTI | 1 | [README](web/13-Flask与Session/README.md) |
| 14 | 综合组合题 | 多考点串联 | 1 | [README](web/14-综合组合题/README.md) |

**当前总计**：28 篇 WP + 29 篇笔记 + 25 个工具 + 15 篇分类说明书。

---

## 三、总方法论（所有题通用的"心法"）

```
                    ┌─────────────────────────────────────────┐
                    │            Web 做题心法                   │
                    └─────────────────────────────────────────┘
        ┌──────────────────┬──────────────────┬──────────────────┐
        ▼                  ▼                  ▼                  ▼
   ①信息收集           ②分析               ③利用              ④复盘
   页面/响应头/注释     入口是什么？          选漏洞类型         写WP/更新图谱
   表单/cookie/JS      后端怎么处理输入？    构造请求拿flag
   (技术栈判断)        (黑盒推断→读源码)
```

**核心心法（背下来）**
1. **数据 vs 代码**：用户输入被当代码/命令执行 = 漏洞根源。
2. **黑盒推断 + 读源码验证**：能读文件先读主文件（设计图）。
3. **对比实验**：带/不带、存在/不存在，差异即线索。
4. **前端校验=纸老虎**：JS 只拦浏览器，拦不住 curl/HackBar。
5. **三问法**（组合题卡住时）：目标文件？被什么堵住？有没有侧门？
6. **实测原则**：参考解答也自己验证。
7. **工具固化**：每类漏洞沉淀脚本（见 `web/00-资料与工具/`）。

---

## 四、技术栈识别（认"厨师"，决定漏洞范围）

| 你看到的线索 | 大概率技术栈 | 常考漏洞 |
|---|---|---|
| `.php` / `X-Powered-By: PHP` / `php-fpm` | PHP | 文件上传 / 文件包含 / 反序列化 / SQLi |
| `Server: Apache` + `.php` | PHP（mod_php 最常见） | 同上 |
| `Server: gunicorn` / `Werkzeug` | Python / Flask | SSTI / SSRF / 调试模式 / session |
| `Server: nginx`（反代） | 背后啥都有 | 配置错误 / 路径穿越 / 反代滥用 |
| `Tomcat` / `Java` 报错 | Java | 原生反序列化 / 表达式注入 |
| `Express` / `Node` | Node.js | 原型链污染 / SSRF |

> 简易记法：**带 `gunicorn`/`Werkzeug`/`Flask` → Python**；**带 `.php`/`php-fpm` → PHP**。其余当背景板。

---

## 五、专题速查（高频打法）

**SSRF 黑名单绕过（秒拒 vs 超时 二分法）**
- 秒拒=被拦（没发出）；超时=发出去了只是没服务（**没被拦**）。
- 回环被拦 → 用 Docker 网关 `172.17.0.1:端口` 访问服务器自身。

**文件包含伪协议分工**
- 读源码 → `php://filter/convert.base64-encode/resource=目标`
- 执行代码 → `data://text/plain,<?php ...?>`（黑名单漏 `data:` 无双斜杠可绕）

**SQL 注入选择树**
- 能 UNION → `UNION SELECT`；UNION 被拦 → **报错注入**（extractvalue）
- 纯盲 → 脚本二分逐位；上 sqlmap（POST 必带 `--data`+`-p`+`--batch`）

**反序列化**
- 读源码找危险魔法方法 → 定 POP 链 → `serforge.py` 构造串 → 属性覆盖

---

## 六、完善指南（让知识图谱持续生长）

1. **新增题目** → 把 `WP` + 相关笔记 + 图片移入对应分类文件夹，更新该分类 `README.md` 的"已收容题目"表。
2. **新考点** → 若在现有分类装不下，新建 `XX-新分类/` 并在本表登记一行。
3. **新工具** → 丢进 `web/00-资料与工具/`，在本库存总表 + 对应分类说明书登记。
4. **组合题** → 记入 `14-综合组合题/`，并在"三问法"链路里标注涉及哪些分类。
5. **复盘必做**：每题结束 → 写 WP → 更新分类说明书 → 回本图谱核对心法是否覆盖。

> 知识图谱不是一次写完的，是**边做边长**的。每次回来都更完整一点。
