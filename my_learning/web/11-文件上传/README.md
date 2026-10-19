# 📤 11 · 文件上传

## 一、题型概述

上传功能若校验不严 → 传 Webshell（`.php`）拿到服务器执行权限（getshell）。是"从外部打进服务器"的高价值题型。

## 二、常考考点

- **前端校验绕过**：JS 只拦浏览器 → `curl` 直接传 `.php`。
- **后缀黑名单**：`.php` 被拦 → 换 `.php5`/`.phtml`/`.htaccess` 让 `.jpg` 当 PHP 解析。
- **`.htaccess` 禁解析**：上传目录被 `php_flag engine off` 禁解析（访问看到源码）→ **看源码泄露判断**（`curl /dir/.htaccess` 拿 403=存在）。
- **路径穿越**：保存名取自 `filename` 且未 `basename()` 过滤 → `filename="../cmd.php"` 把文件写到**网站根**（会解析 PHP）。
- **MIME / 内容校验**：伪造 `Content-Type`、图片马。

## 三、解决方法 / 通用套路

1. **先传正常 `.php` 看反应**：报错（被拦）/ 执行（直接 getshell）/ 下载 / **显示源码**（被禁解析）。
2. **显示源码 = 目录禁解析** → 怀疑 `.htaccess`；`curl /该目录/.htaccess` 看 403(存在) 还是 404(不存在)。
3. **覆盖 `.htaccess` 常被"同名已存在"堵死** → 换招：**路径穿越 `../` 写到网站根**。
4. **写 Webshell 到根目录** → 访问 `cmd.php?c=cat /f*` 读 flag。

## 四、已收容题目

| 题目 | 关键手法 | WriteUp |
|---|---|---|
| qsnctf 40536 | 上传成功但不解析 → 判 `.htaccess` 禁解析 → `filename="../cmd.php"` 路径穿越写网站根 getshell | `WP-[qsnctf]文件上传路径穿越绕过解析限制getshell.md` |

## 五、相关笔记与工具

- 笔记：`Web笔记16-文件上传与htaccess禁解析套路.md`（含"源码泄露→目录禁解析→.htaccess"判定套路与指令速查）
- 关联：与 01-信息泄露（看源码）、07-文件包含 思路相通

> 返回总入口：`../../README.md`
