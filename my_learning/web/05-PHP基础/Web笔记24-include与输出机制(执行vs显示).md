# Web笔记24 · include 与输出机制（执行 vs 显示）

> 主题：为什么 `include("flag.php")` 不会把 flag.php 的内容打印到页面？
> 关联实战：qsnctf 40661（eval 双过滤题，flag 用 include 藏起来）

## 一句话心法
**`include` 是"执行这个文件"，不是"把文件内容显示到页面"。**

## 为什么 include 不打印内容
flag.php 的真实内容（开卷后看到）：
```php
<?php
$flag="flag{d607e5968bd04134b5039a1957f9538f}";   // 这是【赋值语句】
?>
```
- 赋值语句 `$flag="...";` 只把值存进变量 `$flag`，**不产生任何输出**。
- 所以 `include("flag.php")` 跑完，只是悄悄在内存里多了一个 `$flag` 变量，页面上什么都不会多出来。

## 会显示 vs 不显示 对照表

| flag.php 里写的是什么 | include 后页面看到什么 |
|---|---|
| `$flag="flag{...}";`（赋值） | 啥都没有（只存了变量） |
| `echo $flag;`（输出） | 打印出 flag |
| 裸文本 `flag{...}`（在 `<?php ?>` 外面） | 当作 HTML 直接打印 |
| `<?php ?>` 之外的 HTML | 原样输出 |

> 出题人故意写成"纯赋值、不 echo"，让 flag 藏在变量里不露面——逼你要么读源码、要么把 `$flag` 吐出来。

## 三个容易混的函数

| 函数 | 干什么 | 会显示什么 |
|---|---|---|
| `include` / `require` | 把被引入文件**当作 PHP 执行** | 只输出文件里 `echo/print`/`<?php?>` 外的裸文本部分 |
| `echo` / `print` | 把内容**发送到页面**（输出） | 指定的内容 |
| `highlight_file(__FILE__)` | 把"**当前文件**源代码"染色当文本显示 | 源码文本（不执行、不显示被 include 的文件） |

## 实战实例（qsnctf 40661）
- 主文件逻辑：`include("flag.php");` 然后 `highlight_file(__FILE__);` 显示自身源码。
- 你在浏览器看到的彩色代码，是 `highlight_file` 的功劳，**不是** `include` 的输出。
- `highlight_file` 只显示主文件本身，不会把 include 进来的 flag.php 一起显示，更不会执行它输出 flag。
- 所以 flag 既没被运行时输出、也没被高亮显示 → 必须 `file_get_contents` 读源码，或想办法输出 `$flag` 变量。

## 记忆口诀
include = 运行；echo/print = 显示；highlight_file = 把源码当文本看。三者完全不同。
