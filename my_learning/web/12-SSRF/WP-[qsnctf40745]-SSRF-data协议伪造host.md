# WP · qsnctf 40745 — SSRF 解析器差异：data:// 协议伪造 host

> 类型：SSRF / URL 解析器不一致（Parser Differential）  
> 技术栈：nginx/1.18.0 + PHP/7.2.34  
> 难度：入门~中等（开卷源码 + 服务器自曝 parse_url 结果）

## 一、题目信息

- 地址：`http://challenge.qsnctf.com:40745/`
- 入口：POST 参数 `url`。

## 二、信息收集（开卷源码）

host 以 getflag.com 结尾

## 三、漏洞分析

- 目标：让 `parse_url($url)['host']` 以 `getflag.com` 结尾，同时 `file_get_contents($url)` 返回 `pentest`。
- 难点：`parse_url` 和 `file_get_contents` 是**两套不同的解析器**，对同一个 URL 的理解可能不一致 → 这就是突破口（与"检查器 vs 实际请求方"的 SSRF 经典套路同族）。
- 关键点：`parse_url("data://getflag.com/text/plain,pentest")` 会把 `getflag.com` 解析成 host；而 PHP 的 `data://` 流包装器**不管 host 是什么，只把第一个逗号后面的内容当数据返回**。

## 四、利用 payload

```
POST url=data://getflag.com/text/plain,pentest
```

```bash
curl -d "url=data://getflag.com/text/plain,pentest" "http://challenge.qsnctf.com:40745/"
```

返回：

```
flag{1fc345b97290432daad3c6168ca27c36}
```

## 五、验证过的失败路径（黑盒测绘）

| payload                                 | 结果                               |
| --------------------------------------- | -------------------------------- |
| `data://text/plain,pentest`             | ①过 ③挂（host 为空，"host 不正确呢"）       |
| `http://127.0.0.1@getflag.com/`         | ③过 ④挂（真实连到外部 getflag.com 返回 403） |
| `data://getflag.com/text/plain,pentest` | ✅ 全过                             |

## 六、复盘 & 套路沉淀

- **核心心法**：一个 URL 被多套解析器处理时，找它们的**理解差异**。FILTER_VALIDATE_URL 只查格式、parse_url 只做静态解析、file_get_contents 是真正发起请求的——三者对 host 的判定可以不一致。
- **data:// 伪装 host**：`data://<任意host>/<mediatype>,<数据>` 能让 parse_url 看到假 host，而 data 包装器只认逗号后的数据。内容检查要什么字符串就写什么。
- **同类家族**：SSRF 内网 IP 绕过（0x7f000001 十六进制，检查器与 curl 解析不一致）、本 data:// 假 host——都是"解析器差异"这一课。
- **服务器打印 parse_url 结果**是出题人给的调试口，黑盒时务必利用。
