# 📄 07 · 文件包含（LFI）

## 一、题型概述

`include $file` 且 `$file` 可控 → 既能**读任意文件**，配合伪协议又能**执行代码**。是 PHP 栈的核心题型，和"伪协议"强绑定。

## 二、常考考点

- **基础 LFI / 路径穿越**：`?file=../../../../etc/passwd`。
- **php://filter 读源码**：`php://filter/convert.base64-encode/resource=index` 把源码 base64 读出（不执行）。
- **data:// 执行代码**：`data://text/plain,<?php ...?>` 被 `include` 当 PHP 执行。
- **php://input**：从 HTTP body 读代码执行（环境不支持时失效）。
- **黑名单绕过**：过滤 `flag` / `php://` / `data://` 等字面串 → 用**等价写法**溜过（如 `data:` 无双斜杠、`'fl'.'ag'` 拆词、`/f*` 通配）。
- **伪协议全家福**：`data://` / `php://input` / `php://filter` / `phar://` / `zip://` 的分工。

## 三、解决方法 / 通用套路

1. **先验证**：`?file=/etc/passwd` 看是否回显系统文件。
2. **想读源码** → `php://filter/convert.base64-encode/resource=目标`。
3. **想执行代码** → `data://text/plain,<?php ...?>`（或 `php://input`）。
4. **遇黑名单** → 让"参数外壳"不含触发词；数据体里拆词/通配（`笔记13 §2.5/§2.7`）。
5. **判断执行与否**：看"哪个函数消费"——`include` 执行，`file_get_contents` 不执行（`笔记13 §2.4`）。

## 四、已收容题目

| 题目 | 关键手法 | WriteUp |
|---|---|---|
| DASCTF p参数文件包含 | LFI + `php://filter` 读源码 + die 绕过 | `WP-[DASCTF]p参数文件包含.md` |
| qsnctf 40514 | `data://` 直接执行 + `cat /f*` 读 flag | `WP-[qsnctf]文件包含data协议绕过黑名单.md` |
| qsnctf 40559 | 黑名单只写 `data://` → 用 `data:` 无双斜杠绕过 + `cat /f*` | `WP-[qsnctf]文件包含黑名单绕过data协议无双斜杠.md` |

## 五、相关笔记与工具

- 笔记：`Web笔记10-文件包含LFI解题手册.md`、`Web笔记13-PHP文件包含与伪协议全家福.md`（含正则 `\`/`i` 速成、data 拆解图）
- 图示：`img/data_uri_breakdown.svg`、`img/data_consumer_functions.svg`

> 返回总入口：`../../README.md`
