# 🔍 01 · 信息泄露与备份文件

## 一、题型概述

**最低成本、最常考的第一类题**。不利用任何"漏洞利用链"，而是直接从页面、源码、注释、JS、备份文件中把 flag 或关键线索"捡"出来。新人最容易拿到第一血的地方。

## 二、常考考点

- **查看源代码**：右键 / `Ctrl+U` 看 HTML 注释、隐藏元素、内联 JS。
- **JS 硬编码**：密钥、flag 片段、接口地址直接写在前端 JS 里（常配合 JSFuck、混淆）。
- **注释泄露**：HTML/SVG/图片 `<!-- -->`、源码注释。
- **备份 / 临时文件**：`.swp`（Vim）、`.bak`、`.swo`、`.DS_Store`、`~`、`.git`、`.svn`、`robots.txt`、`flag.txt`。
- **目录可列**：服务器开了 autoindex，直接浏览文件列表。
- **报错信息**：把路径、框架、版本暴露出来。

## 三、解决方法 / 通用套路

1. **第一步永远看源码**：`Ctrl+U` → 搜 `flag`、`password`、`key`、`token`、`hidden`、`<!--`。
2. **扫备份文件**：手动试 `index.php.bak`、`/robots.txt`、`/.git/`、`.swp`；或上自动化工具（见下）。
3. **JS 解密**：遇到 JSFuck / 混淆，复制到控制台或在线解码器跑一遍。
4. **组合意识**：信息泄露常是别的题的"第一步"（先拿到源码/密钥，再打后续）。

## 四、已收容题目

| 题目 | 关键手法 | WriteUp |
|---|---|---|
| LitCTF 1zjs | 注释 + JSFuck 解码 | `WP-[LitCTF2023]1zjs.md` |
| LitCTF Vim-yyds | `.swp` 泄露 + 恢复源码 + RCE | `WP-[LitCTF2023]Vim-yyds.md` |
| DASCTF 敏感文件 | flag 拆分到 robots/.DS_Store/.bak/.swp 多文件 | `WP-[DASCTF]敏感文件.md` |

## 五、相关笔记与工具

- 笔记：`Web笔记01-敏感信息泄露与JS分析.md`、`Web笔记07-敏感信息泄露速查表.md`（12 种泄露点速查）
- 工具：`sensitive_scan.py`、`swp_extract.py`（见 `../00-资料与工具/`）
- 图示：`1zjs_logo.png`

> 返回总入口：`../../README.md`
