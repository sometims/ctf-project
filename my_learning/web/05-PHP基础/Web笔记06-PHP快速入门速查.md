# PHP 快速入门速查（CTF 读题用）

> 目标：不是学会写 PHP，而是**读懂题目里的 PHP 代码**。认识这些，能读 90% 入门题。

## 一、程序骨架

```php
<?php          // 开头必须有
$x = 1;        // 变量 $ 开头，不声明类型
echo $x;       // 输出
?>
```

## 二、基础语法表

| 语法 | 写法 | 说明 |
|---|---|---|
| 变量 | `$a = "hello";` | 值随意，字符串/数字/数组 |
| 拼接 | `"a" . "b"` | `.` = 字符串拼接（PHP 的 + 只做加法） |
| 输出 | `echo $x;` / `print` | 打印到页面 |
| 判断 | `if($x==1){...}else{...}` | 常规 |
| 数组 | `$arr[0]` / `$arr['key']` | 方括号取元素，数字或字符串 key |
| 嵌套数组 | `$_POST['a']['b'][0]` | 表单 `a[b][0]=x` 自动生成 |
| 注释 | `//` `#` `/* */` | 不执行 |
| 停止 | `die()` / `exit` | 立刻结束 |
| 检查 | `isset($x)` | 变量是否存在 |

## 三、超全局变量（输入源，做题必看）

| 变量 | 装什么 | 怎么喂 |
|---|---|---|
| `$_GET['k']` | URL 参数 | `/?k=1` |
| `$_POST['k']` | 请求体 | POST 表单 |
| `$_COOKIE['k']` | cookie | Cookie 头 |
| `$_REQUEST['k']` | GET+POST 合并 | 两个都算 |
| `$_FILES['k']` | 上传文件 | multipart |
| `$_SERVER` | 服务器信息 | 自动 |

## 四、危险函数（看到就警觉 → 找输入源和过滤）

| 函数 | 作用 | 漏洞类型 |
|---|---|---|
| `eval($str)` | 字符串当 PHP 代码执行 | RCE |
| `system($cmd)` | 执行系统命令+回显 | RCE |
| `shell_exec($cmd)` | 执行命令返回结果 | RCE |
| `exec()` `passthru()` | 同上变体 | RCE |
| `include`/`require` | 包含文件 | 文件包含 |
| `file_get_contents` | 读文件 | 任意文件读取 |
| `unserialize($str)` | 反序列化 | 反序列化 |
| `preg_replace('/x/e',...)` | 旧版可执行 | RCE |
| `extract($_POST)` | 参数解包成变量 | 变量覆盖/配合eval |
| `$$a` | 变量的变量 | 配合 eval 链 |

## 五、常见辅助函数

| 函数 | 作用 | 常见坑 |
|---|---|---|
| `highlight_file(__FILE__)` | 打印源码 | = 源码送脸上，直接审计 |
| `error_reporting(0)` | 关报错 | 失败静默，用标记payload验证 |
| `die()` | 结束 | 无参数时页面空白 |
| `header()` | 发响应头 | 重定向等 |
| `str_replace` / `preg_match` | 过滤/检查 | 有就可能要绕过 |
| `addslashes` | 转义引号 | SQL注入的常见防线 |

## 六、读题三步法

```
① 找危险函数（eval/system/include/unserialize...）
② 找输入源（$_GET/$_POST/$_COOKIE...）用户能不能控制？
③ 找过滤（preg_match/str_replace/黑名单...）能不能绕过？
→ 漏洞类型确定
```

## 七、复习：这几天见过的代码

```php
// Ping-Ping: 命令注入
$command = 'ping -c 6 ' . $_POST['command'];   // 拼接无过滤
shell_exec($command);

// Flask题: PHP侧 $_COOKIE 概念（语言不同，概念同）
$_COOKIE['CTFshow-QQ群:'];

// 嵌套eval题
eval($_REQUEST[$_GET[$_POST[$_COOKIE['CTFshow-QQ群:']]]][6][0][7][5][8][0][9][4][4]);

// 变量的变量题
extract($_POST);
eval($$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$_);
```

## 八、学习方法建议

- 不需要背函数库：遇到不懂的查 https://www.php.net/manual/zh/ 或问老师
- 优先认识"危险函数"+"超全局变量"，这两类覆盖 90% 题目
- 每做一题，把新见的函数补进本表
