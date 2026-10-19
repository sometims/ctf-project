# WP｜qsnctf ez_http（HTTP 协议六连关）

> 靶机：http://challenge.qsnctf.com:40073/ ｜ 2026-08-11 实测
> 类型：HTTP 协议基础（方法 / 参数 / Referer / UA / XFF / Cookie 全要素）
> flag(实测)：`flag{f58a173f47d847478d1182f1360e6274}`

---

## 一、解题链（每步一个提示，逐步解锁）

| # | 提示（页面文字） | 含义 | 解法 |
|---|---|---|---|
| 1 | `Please use POST Method` | 请求方法不对 | 改用 **POST** |
| 2 | `请使用POST方法`（中文版） | 仍在要求 POST，实际暗示「POST 里要带 tyctf 参数」 | POST body 加 **`tyctf=x`**（值任意，是开关） |
| 3 | `POST to hhh = abc` | 还差一个参数 | 加 **`hhh=abc`** |
| 4 | `This page must be source https://sqnu-tysec.com` | 检查来源页 | 加请求头 **`Referer: https://sqnu-tysec.com`** |
| 5 | `你用的什么浏览器??? 是TYsecBrowser吗?` | 检查浏览器标识 | 改 **`User-Agent: TYsecBrowser`** |
| 6 | `你不是本地人!!! 何人胆敢来犯` | 检查来源 IP | 加 **`X-Forwarded-For: 127.0.0.1`** |
| 7 | `没带曲奇饼, 或者是user曲奇饼不是admin牌的` | 检查 Cookie 身份 | 加 **`Cookie: user=admin`** → **flag** |

## 二、一条命令通关

```bash
curl -X POST -d "tyctf=x&hhh=abc" \
  -H "Referer: https://sqnu-tysec.com" \
  -H "User-Agent: TYsecBrowser" \
  -H "X-Forwarded-For: 127.0.0.1" \
  -H "Cookie: user=admin" \
  http://challenge.qsnctf.com:40073/
```

## 三、关键认知

1. **tyctf 参数是「开关」**：不传它时提示是中文版「请使用POST方法」，传了就进入下一关——做题时看到「重复的提示但语言/细节不同」，就要怀疑是**隐藏参数门**。
2. **X-Forwarded-For 是伪造重灾区**：这个头本是代理服务器加的（记录真实客户端 IP），但很多后端**直接信任它**当来源 IP → 填 `127.0.0.1` 就"本地人"了。这类题常配合 admin 逻辑。
3. **HTTP 请求 7 个可伪造要素**：方法 / URL参数 / POST参数 / Referer / User-Agent / X-Forwarded-For / Cookie——后端只要拿其中任何一个当「身份/权限依据」就是漏洞。

## 四、复盘一条新套路

```
HTTP 题六连关套路（ez_http 类）：
  方法不对 → 改 POST
  参数开关 → fuzz/看按钮名（tyctf）→ 带上
  再要参数 → hhh=abc（照提示写）
  Referer → 伪造来源域名
  User-Agent → 按提示写浏览器名
  X-Forwarded-For → 127.0.0.1（本地人）
  Cookie → user=admin（身份伪造）
```
> 记忆点：**服务器拿请求头当身份依据 = 全可伪造**，一条 curl 全部搞定。
