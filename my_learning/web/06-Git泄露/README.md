# 📜 06 · Git 泄露

## 一、题型概述

网站把 `.git` 目录部署到了公网 → 攻击者可**完整恢复源码仓库**，拿到所有历史版本、找 flag 或逻辑漏洞。是信息泄露里的经典独立分支。

## 二、常考考点

- **验证泄露**：访问 `/.git/HEAD`，返回 `ref: refs/heads/master` 即存在。
- **源码恢复**：用 `git-dumper` 把整个 `.git` 拖到本地，再 `git log` / `git checkout` 看历史。
- **仓库内搜 flag**：恢复后直接 `grep -r flag` 或在历史提交里翻。
- **"4 种藏法"**：flag 可能在当前文件、历史提交、某次 diff、被删分支里。

## 三、解决方法 / 通用套路

1. 探 `/.git/HEAD` → 确认泄露。
2. `git-dumper http://x/.git/ ./out` 下载仓库。
3. `git_search.py` 自动搜 flag，或手动 `git log -p` 翻历史。
4. 拿到源码后通常进入"读代码找下一个漏洞"的链路（文件读取/反序列化等）。

## 四、已收容题目

| 题目 | 关键手法 | WriteUp |
|---|---|---|
| DASCTF Git测试 | `.git` 泄露 → git-dumper 恢复 → 仓库搜 flag | `WP-[DASCTF]Git测试.md` |

## 五、相关笔记与工具

- 笔记：`Web笔记09-Git泄露解题手册.md`（5 动作流程 / 4 藏法）
- 工具：`git_search.py`（见 `../00-资料与工具/`）

> 返回总入口：`../../README.md`
