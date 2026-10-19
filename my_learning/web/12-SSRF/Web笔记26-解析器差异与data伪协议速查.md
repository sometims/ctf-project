# Web笔记26 · 解析器差异与 data:// 伪协议速查

> 主题：同一 URL 被多套解析器各读各的 → SSRF 绕过；data:// 伪协议伪造 host
> 关联实战：qsnctf 40745（host 结尾检查 + 内容检查）、SSRF 内网 IP（0x7f000001）

## 一、URL 解剖（先认零件）
```
scheme://user:pass@host:port/path?query#fragment
 协议    用户:密码@ 主机:端口 路径  查询  锚点
```
`parse_url($url)` 返回关联数组：`['scheme'] ['user'] ['pass'] ['host'] ['port'] ['path'] ['query'] ['fragment']`。`$r['host']` 就是主机名。

## 二、核心心法：多套解析器 = 找差异 ★
一个 URL 在代码里可能被**三套不同的解析器**处理：
| 角色 | 干什么 | 特点 |
|---|---|---|
| 校验器（FILTER_VALIDATE_URL）| 只查格式合不合法 | 宽松，认任意 scheme:// |
| 静态解析器（parse_url）| 把 URL 拆零件 | 纯字符串拆解，信你写的 |
| 实际执行者（file_get_contents/curl）| 真正发起读取/请求 | 按协议规则干活 |

**三者对同一个 URL 的理解可以不一致 → 检查者看到"合法身份"，执行者干"别的事"。**

## 三、data:// 伪协议（不联网的假数据源）
- 为什么叫"伪协议"：长着协议脸（`scheme://`）、能被 file_get_contents/include 接受，但**不发起网络请求**，内容由 PHP 按 URL 字符串当场生成
- 格式：`data://<mediatype>,<内容>` 或 `data://<mediatype>;base64,<base64内容>`
- 读函数返回"第一个逗号后的内容"

## 四、data:// 伪造 host 套路（40745 解法）★
```
data://getflag.com/text/plain,pentest
        └─┬─┘   └──┬──┘ └──┬──┘
    parse_url 当 host   路径  真实内容
```
- parse_url 拆出 host = `getflag.com` → 骗过"host 以 getflag.com 结尾"检查
- data 包装器忽略 host，只返回 `pentest` → 骗过"内容必须 = pentest"
- 三关全过：`?url=data://getflag.com/text/plain,pentest`

## 五、data:// 三个招牌用法
| 场景 | 用法 | 效果 |
|---|---|---|
| SSRF 造内容 | `data://<假host>/text/plain,<要的内容>` | 过 host/内容检查 |
| LFI 代码执行 | `include("data://text/plain,<?php system('ls');?>")` | include 当 PHP 执行 → RCE |
| 躲过滤 | `data://text/plain;base64,<base64>` | 特殊字符/关键字编码后过 |

## 六、失败路径参考（黑盒测绘）
- `data://text/plain,pentest` → 没有 host → host 检查挂
- `http://127.0.0.1@getflag.com/` → host 检查过，但真实连了外部 getflag.com（403）→ @ 用户信息技巧骗不过执行者
- 套路：**报错/回显就是探针**（服务器 print_r 白送 parse_url 结果，务必利用）

## 七、同类家族（解析器差异这一课）
| 手法 | 差异点 |
|---|---|
| 0x7f000001 十六进制 IP | 检查器只认点分十进制，curl 认十六进制 |
| data:// 假 host | parse_url 认假 host，data 包装器只认逗号后内容 |
| 回环变体 | 127.1 / [::1] / nip.io 等表达同一地址 |

## 八、正则检查的读法（结尾 vs 等于）
- `/getflag\.com$/` → 结尾匹配（$ 锚点）→ `xxxgetflag.com` 都过
- `/^getflag\.com$/` → 完全等于 → 只有 getflag.com 过
- 正则里 `.` 是任意字符，`\.` 才是字面点号（出题人忘转义 = 可绕过点）
