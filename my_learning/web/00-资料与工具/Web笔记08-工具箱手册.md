# Web 工具箱手册（所有自建工具 + 第三方工具）

> 更新：2026-08-01 ｜ 用法原则：**信息收集自动化，利用靠知识**
> 做题流程：sensitive_scan（敏感文件）→ mini_scanner（目录）→ 分析技术栈 → 选利用工具

---

## 一、自建工具（都在 my_learning/web/）

### 1. sensitive_scan.py —— 敏感文件扫描器 ★最新
```bash
python sensitive_scan.py <靶机URL>
```
| 项目 | 说明 |
|---|---|
| 干什么 | 爆破 100+ 常见敏感路径，自动解析 robots.txt 跟进，下载文件搜 flag 特征 |
| 适用 | 敏感信息泄露类题（flag 藏在文件里） |
| 特点 | 防假200（与首页相同跳过）、识别不闭合的 flag 片段（flag2:xxx） |
| 输出 | [状态码] 路径 → 找到的 flag 片段 |

### 2. mini_scanner.py —— 目录扫描器（早期）
```bash
python mini_scanner.py
```
- 词表穷举目录/文件，支持手动输入，**防假200**（判断内容而非状态码）
- 适用：找隐藏目录/后台（/admin /upload /flag.php...）
- 特点：不依赖 dirsearch（Python 3.13 装不了）

### 2.5 sensitive_scan vs mini_scanner（区别速记）

| | mini_scanner | sensitive_scan |
|---|---|---|
| 回答的问题 | 网站还有**哪些路径/目录**？ | 有没有**泄露已知敏感文件**？ |
| 原理 | 大字典穷举（几千词，找未知） | 精选清单（几十个，查已知敏感点） |
| 范围 | 广 | 精 |
| 附加能力 | 假200 判断 | 解析 robots.txt + 下载文件搜 flag 片段 |
| 耗时 | 慢 | 快（1分钟） |
| 比喻 | 翻遍每个房间找暗室 | 直奔众所周知的保险柜位置 |

**使用顺序**：先 sensitive_scan（捡漏）→ 再 mini_scanner（普查）→ 分析利用

### 3. php_eval_chain.py —— PHP 变量链 eval 通用模板
```bash
python php_eval_chain.py <靶机> <深度> "<代码>"
python php_eval_chain.py <靶机> 0 "<代码>" scan   # 自动扫正确深度
```
- 适用：`eval($$$$...$_);` 这类"变量的变量"题
- 原理：N 个 $ = N 层链 = N 个变量接力，最后一个变量的值 = 代码

### 4. ctfshow_nested_eval.py —— 嵌套超全局变量链 exploit
```bash
python ctfshow_nested_eval.py "<代码>"
```
- 适用：`eval($_REQUEST[$_GET[$_POST[$_COOKIE[..]]]][6][0]..);` 题
- 原理：cookie→POST→GET→REQUEST 接力 + 表单嵌套数组 `c[6][0]...[4]=代码`
- 特点：http.client 发**原始 UTF-8 字节**（中文 cookie 名场景）

### 5. swp_extract.py —— .swp 交换文件恢复工具（早期）
- 适用：vim 交换文件泄露，提取被编辑的源码
- 用法：下载 .swp → 工具恢复 → 读源码找 flag

### 6. post_demo.py —— GET/POST 演示脚本（早期，教学用）

---

## 二、第三方工具（已安装）

| 工具 | 干什么 | 关键命令 |
|---|---|---|
| **flask-unsign** | Flask cookie 解/爆/签 | `--decode` / `--unsign --wordlist` / `--sign --secret` |
| **git-dumper** | .git 泄露全量下载 | `git-dumper <url>/.git/ <本地目录>` |
| **curl.exe** | 发请求万能工具 | 见速查卡（Web最小工具集速查卡.md） |
| **Python + requests** | 脚本化请求 | 盲注/爆破/自动化 |
| **itsdangerous** | Flask 签名底层库 | 手写 cookie 伪造（原理演示） |
| **Node.js v24** | 执行 JS | JSFuck 等 JS 混淆题 |

---

## 三、场景 → 工具对照表

| 场景 | 用什么 |
|---|---|
| 新靶机第一件事 | sensitive_scan.py + mini_scanner.py |
| 页面只有输入框 | 先测输入点 → 判断漏洞类型 |
| PHP 源码出现 eval | php_eval_chain.py / ctfshow_nested_eval.py（看 eval 参数结构） |
| 响应头 Werkzeug/Python | flask-unsign 三连（解→爆→签） |
| 有 .git 目录 | git-dumper |
| 有 .swp 文件 | swp_extract.py |
| 需要循环测试 payload | Python + requests 脚本 |

---

## 四、工具使用心法

1. **信息收集自动化**：扫描器只花 1 分钟，代替 10 分钟手敲
2. **利用靠知识**：工具找到入口后，判断/构造 payload 靠学过的原理
3. **工具会失效**：WAF/限速/假 200/验证码 → 换思路或手动
4. **遇新题型固化新工具**：每做一类新题，把套路写进工具/模板
5. **命令不背**：本手册 + 速查卡，做题对照抄
