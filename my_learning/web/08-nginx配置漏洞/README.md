# ⚙️ 08 · nginx 配置漏洞

## 一、题型概述

不是代码漏洞，而是 **nginx 配置错误**导致的越权访问/穿越。常见于 `root` 与 `alias` 用混、开启了目录列表。

## 二、常考考点

- **root vs alias 区别**：
  - `location /img/ { alias /var/www/; }` → 访问 `/img../etc/passwd` 会解析成 `/var/www/../etc/passwd` → **穿越**！
  - `root` 则是拼接路径，不易出该问题。
- **alias 穿越公式**：`/映射前缀../目标文件`（利用 alias 把前缀"替换"掉后留下的 `../`）。
- **autoindex 目录可列**：直接浏览文件列表找 flag/源码。
- **配置误暴露**：`/nginx.conf`、`/.git`、默认页。

## 三、解决方法 / 通用套路

1. 看到静态资源路径（`/img/`、`/static/`）就试 `../` 穿越。
2. 用 `alias` 穿越公式：`/前缀../etc/passwd`。
3. 验证时配合文件读取家族（读 `/etc/passwd`、读主配置、读源码）。

## 四、已收容题目

| 题目 | 关键手法 | WriteUp |
|---|---|---|
| DASCTF u1s1 | nginx `alias` 穿越 `/img../etc/passwd` | `WP-[DASCTF]u1s1-nginx-alias穿越.md` |

## 五、相关笔记与工具

- 笔记：`Web笔记11-nginx基础与alias穿越.md`
- 关联：与 07-文件包含、01-信息泄露 常组合出现

> 返回总入口：`../../README.md`
