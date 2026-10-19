# 🗄️ 10 · SQL 注入

## 一、题型概述

用户输入拼进 SQL 语句 → 改变原意、读出/篡改数据。Web 最经典题型之一，分支极多（联合/报错/盲注/堆叠/WAF 绕过）。

## 二、常考考点

- **登录绕过**：`' OR 1=1-- -` 闭合认证条件；SQLite 后端注释 `--` 无需尾部空格（`admin'--` 裸写即可）。
- **隐藏调试参数**：登录表单里的 `debug`/`test` 等 hidden 字段改 1 可能回显 SQL，等于开卷。
- **联合查询（UNION）**：`UNION SELECT` 拖库（需先 `ORDER BY` 判列数）。
- **报错注入**：`extractvalue()` / `updatexml()` / `floor()` 把数据挤进报错信息。
- **盲注**：布尔盲注、时间盲注（`sleep`/`benchmark`），靠响应差异逐位拖数据。
- **sqlmap 自动化**：GET 直接 `-u`；POST 必须 `--data` + `-p` + `--batch`。
- **WAF 绕过**：空格被拦→`()` 代替；`OR` 被拦→`||`；`UNION` 被拦→换报错注入；`select (` 贴括号绕"词+空格"类规则。

## 三、解决方法 / 通用套路

1. **先找注入点**：加 `'` 看是否报 SQL 语法错，确认字符型/数字型。
2. **判列数**：`ORDER BY n-- -`（被拦就换盲注/报错）。
3. **能 UNION 就 UNION**；UNION 被拦 → **报错注入**（extractvalue 最稳）。
4. **纯盲注** → 用脚本二分逐位提取（参考已删的 40554 思路）。
5. **上 sqlmap**：`sqlmap -u URL --dbs --batch`，POST 加 `--data`/`-p`。

## 四、已收容题目

| 题目 | 关键手法 | WriteUp |
|---|---|---|
| qsnctf 40517 | 登录绕过 + error/time 盲注 + sqlmap 工作流（GET/POST） | `WP-[qsnctf]SQL注入登录绕过与sqlmap工作流.md` |
| picoCTF 2019 Irish-Name-Repo 1 | SQLite 登录绕过 + `debug=1` 回显 SQL + 库内无 flag 转人工 | `WP-[picoCTF-2019-Irish-Name-Repo1]SQLite登录绕过与debug回显.md` |

> 注：qsnctf 40554（报错注入绕过空格过滤）因学生反馈"看不懂"已**跳过删除**，其 WP 与脚本一并清理；若日后想补同类题，参考 `Web笔记15` 的 sqlmap 流程 + 报错注入思路。

## 五、相关笔记与工具

- 笔记：`Web笔记15-sqlmap的GET与POST请求.md`
- 工具：sqlmap（外部，非本仓库）、`python+requests` 自写盲注脚本
- 关联：WAF 绕过与报错注入可单开专题笔记（待补 `Web笔记17`）

> 返回总入口：`../../README.md`
