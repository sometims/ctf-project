# 💥 04 · RCE 与命令注入

## 一、题型概述

**用户输入被当成「命令」或「代码」执行**——Web 漏洞里最危险、也最常考的一类。分两支：
- **命令注入（Command Injection）**：拼进系统 shell，如 `system("ping ".$ip)`。
- **代码注入（Code Injection / eval）**：拼进语言解释器，如 `eval($_GET['x'])`。

## 二、常考考点

- **拼接符**：命令注入用 `;`、`&&`、`||`、`|`、`\n`（换行）、反引号 `` ` ``、`<`(读文件当命令输入) 串接额外命令。
- **无空格绕过**：`${IFS}`、`$IFS$9`、`<`、`{cat,/flag}`、Tab、`$'\x20'`。
- **黑名单绕过**：过滤 `cat`→用 `tac`/`more`/`less`/`nl`/`sort`；过滤 `/`→用变量拼接；过滤关键字→拼接/`*` 通配。
- **PHP eval 链**：`$$` 变量-variable、`extract()`、`$_GET` 超全局变量层层传递，构造"把输入喂进 eval"的链。
- **危险函数**：`system/exec/shell_exec/passthru`、PHP `eval`、Python `eval/exec`、模板 `{{ }}`。

## 三、解决方法 / 通用套路

1. **先判类型**：输入进了系统命令（试 `;id`）还是进了语言（试 `;phpinfo()` / `{{7*7}}`）。
2. **试拼接符 + 基础命令**（`;id`、`| whoami`）验证执行。
3. **遇过滤**：空格→`${IFS}`；命令名→换同义命令或拼接；关键字→拆词/通配。
4. **eval 链题**：理清变量传递路径，脚本自动化爆破链深度（`php_eval_chain.py`）。

## 四、已收容题目

| 题目 | 关键手法 | WriteUp |
|---|---|---|
| NSSCTF Ping-Ping | 经典命令注入 `;`、`|` 拼接 | `WP-[NSSCTF]Ping-Ping-命令注入.md` |
| CTF-Show 嵌套 eval | 超全局变量链 + cookie 中文名 + 嵌套数组喂入 eval | `WP-[CTF-Show]嵌套eval的RCE.md` |
| CTF-Show 变量的变量 | `extract()` + 36 层 `$$` 变量-variable 链 | `WP-[CTF-Show]变量的变量eval.md` |
| qsnctf 目录浏览器(40567) | 字符+词级黑名单：`&`分隔 / Tab代空格 / `/[f]lag`字符类避关键词 / `grep`读文件 | `WP-[qsnctf]目录浏览器命令注入黑名单绕过.md` |

## 五、相关笔记与工具

- 笔记：`Web笔记04-RCE常用命令速查.md`、`Web笔记05-发请求的几种方式与命令注入重点.md`、`Web笔记06-shell基础与命令注入绕过速查.md`（shell 基础 + 分隔符/空格替代/关键词绕过/控制字符表示法 一览）
- 工具：`php_eval_chain.py`（见 `../00-资料与工具/`）

> 返回总入口：`../../README.md`
