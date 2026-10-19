# 🌐 02 · HTTP 与请求基础

## 一、题型概述

**不是一种"漏洞"，而是所有 Web 题的地基**。几乎所有 CTF Web 题都要你自己构造 HTTP 请求（GET/POST、自定义头、Cookie、编码）。这一类的"题"更多是知识点，而非独立 WP。

## 二、常考考点

- **GET vs POST**：参数在 URL 还是 body；前端校验是纸老虎（`curl` 随便改）。
- **参数位置**：URL 查询、表单 body、`Cookie`、`Header`、`JSON`、`multipart`。
- **请求构造**：手写 `curl`、改 `Content-Type`、URL 编码 / 双重编码。
- **编码细节**：`encodeURIComponent` 不转义 `'` 等字符（曾直接成为注入入口，见 SSRF/SQLi 题）。

## 三、解决方法 / 通用套路

1. 先用浏览器/抓包看清"正常请求长什么样"。
2. 用 `curl` 复现，再逐步改参数做攻击——**永远用工具发请求，别被前端 JS 限制**。
3. 拿不准就回看速查卡里的 curl 万能骨架。

## 四、已收容题目

- 本分类以知识点为主；对应的 Login/传参类实战散见于各题（如 SQLi 登录绕过、文件上传表单）。
- 独立 WP 暂缺（NSSCTF "Follow me and hack me" GET-POST 题未单独成文，可补）。

## 五、相关笔记与工具

- 笔记：`Web笔记02-HTTP基础-GET与POST传参.md`
- 速查：`../00-资料与工具/Web最小工具集速查卡.md`（curl 万能骨架）

> 返回总入口：`../../README.md`
