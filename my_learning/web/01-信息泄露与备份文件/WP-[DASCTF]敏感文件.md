【DASCTF 敏感文件】平台：dasctf｜难度：☆☆☆｜日期：2026-08-01

## 考点
敏感信息泄露（专栏：敏感信息泄露）—— flag 拆分藏在多个敏感文件中

## 我的思路
1. 页面提示"信息搜集之所以重要" → 敏感文件探测题
2. 批量探测常见敏感路径 → 命中 5 个：robots.txt / .DS_Store / index.php~ / .index.php.swp / .htaccess(403)
3. robots.txt → 发现隐藏文件 /flag1_is_her3_fun.txt → flag1
4. index.php~（vim 备份）→ 源码里有 flag2（无闭合括号的片段，易漏）
5. .index.php.swp（vim 交换文件）→ 提取源码 → flag3
6. 拼接三个片段 = 完整 flag

## 解题过程
```bash
# 1. 扫描（或用工具 sensitive_scan.py 一键）
curl -s <靶机>/robots.txt            # 发现 /flag1_is_her3_fun.txt
curl -s <靶机>/flag1_is_her3_fun.txt # flag1:n1book{info_1
curl -s <靶机>/index.php~            # 备份文件 → flag2:s_v3ry_im
curl -s <靶机>/.index.php.swp -o x.swp  # 下载交换文件
# 2. 提取 swp 源码 → 找到 flag3:p0rtant_hack}
```

flag：`n1book{info_1s_v3ry_imp0rtant_hack}`（三段拼合）

## 收获
### 1. flag 拆分套路
- 出题人把 flag 拆成多段，分别藏在不同的敏感文件里 → **必须全部找到才能拼全**
- 分段命名规律：flag1/flag2/flag3 + 提示性名字（flag1_is_her3_fun.txt）
- 片段可能是**不闭合**的（没有 `}`）→ 搜"flag2:"这种模式，别只搜闭合格式

### 2. 敏感文件探测优先级（实战顺序）
```
robots.txt → 备份文件(~ .bak .old .save) → 交换文件(.swp) → 版本控制(.git .svn .hg) → .DS_Store → flag变体(f1ag)
```

### 3. 关键认知
- **"隐藏"是给人看的**：点开头文件（.DS_Store/.swp）服务器照样返回，除非 nginx 配置了 deny
- **二进制乱码 ≠ 访问失败**：.swp/.DS_Store 浏览器显示乱码 = 成功下载，用 curl -o 保存后本地解析
- vim 交换文件：文件名是 `.原文件名.swp`，存着编辑中的源码（含被删内容/旧版本）
- 备份文件 `xxx~`：vim 保存时留下的前一版本，常含被删掉的敏感代码

### 4. 自动化
- 工具：sensitive_scan.py（爆破 100+ 路径 + 解析 robots + 搜 flag 片段）→ 一条命令扫完
- 人工只负责最后一步：把片段拼起来

## 常见坑
- 中文编码问题导致文本搜索漏掉 flag（PowerShell 下用 python/文件方式搜更稳）
- robots.txt 格式不规范时（Disallow 空值+路径在下一行），手动看或让工具兼容
