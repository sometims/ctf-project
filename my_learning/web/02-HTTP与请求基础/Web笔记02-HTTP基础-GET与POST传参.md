# 🗂 Web 笔记 02｜HTTP 基础：GET 与 POST 传参全攻略

> 记录自：NSSCTF [LitCTF 2023] Follow me and hack me（3864）｜ 2026-08-01
> 这道题就是教 GET/POST 传参的入门题

---

## 一、本质（先记这个）

**传参 = 让参数出现在发给服务器的请求里。**

- GET 参数 → 放在 **URL 里**（网址 `?变量=值`）
- POST 参数 → 放在 **body 里**（请求体，URL 看不见）

**工具（地址栏/Console/命令行/HackBar）只是"发射器"**，发射的是同一个请求。参数不在工具里，在请求里。

| | GET 参数 | POST 参数 |
|---|---|---|
| 放哪 | 网址 `?CTF=Lit2023` | body `Challenge=...` |
| 肉眼可见 | ✅ 地址栏看得见 | ❌ 看不见 |
| 传多长 | 短（URL 限制） | 长 |
| 用途 | 查询/取数据 | 提交/传数据 |

---

## 二、GET 的传参方式（任选一个）

### ① 浏览器地址栏（最简单）
把网址 + `?变量=值` 粘进地址栏回车：
```
http://node5.anna.nssctf.cn:28716/?CTF=Lit2023
```
多参数用 `&` 连接：`?a=1&b=2`

### ② curl（命令行，CTF 主力）
```bash
curl "http://node5.anna.nssctf.cn:28716/?CTF=Lit2023"
```

### ③ Python requests
```python
import requests
r = requests.get("http://node5.anna.nssctf.cn:28716/", params={"CTF": "Lit2023"})
print(r.text)
```

### ④ 浏览器 F12 Console
```js
fetch("http://node5.anna.nssctf.cn:28716/?CTF=Lit2023")
```

---

## 三、POST 的传参方式（任选一个）

### ① curl（推荐，一条命令搞定 GET+POST）
```bash
curl -X POST "http://node5.anna.nssctf.cn:28716/?CTF=Lit2023" -d "Challenge=i%27m_c0m1ng"
```
拆解：
- `-X POST` = 指定 POST 方法
- `-d "变量=值"` = ★ 指定 body（POST 参数放这）
- 网址里的 `?CTF=...` 是 GET 参数，body 里的是 POST 参数——**可以同时带**

> 💡 小知识：`-d` 本身就默认用 POST，所以 `curl URL -d "a=b"` 不加 `-X POST` 也行。

### ② Python requests（写脚本推荐）
```python
import requests
r = requests.post(
    "http://node5.anna.nssctf.cn:28716/?CTF=Lit2023",
    data={"Challenge": "i'm_c0m1ng"}   # data= 字典，自动帮你 urlencode（单引号不用自己编码！）
)
print(r.text)
```

### ③ 浏览器 F12 Console（fetch 要看结果必须加 .then！）
```js
fetch("http://node5.anna.nssctf.cn:28716/?CTF=Lit2023",
  {method:"POST",
   headers:{"Content-Type":"application/x-www-form-urlencoded"},
   body:"Challenge=i%27m_c0m1ng"})
  .then(r=>r.text()).then(t=>console.log(t))   // ★ 不加 .then 只看到 Promise，看不到结果！
```

### ④ HackBar（浏览器插件，图形界面最友好）
```
装好 HackBar 后：F12 → HackBar 面板
① URL 框填：http://node5.anna.nssctf.cn:28716/?CTF=Lit2023
② Method 下拉框选 POST
③ Post data 框填：Challenge=i%27m_c0m1ng
④ 点 Execute 执行 → 看响应
```

### ⑤ HTML 表单（本质就是 POST！）
网页里 `<form method="POST">` 提交时发的就是 POST——你平时填表单点提交，就是在发 POST。

---

## 四、请求长啥样（底层真相）

```
GET /?CTF=Lit2023 HTTP/1.1        ← 方法 + URL + 版本
Host: node5.anna.nssctf.cn:28716
User-Agent: Mozilla/5.0
                                   ← 空行（GET 没 body）
```
```
POST /?CTF=Lit2023 HTTP/1.1       ← 方法换 POST
Content-Type: application/x-www-form-urlencoded
Content-Length: 22
                                   ← 空行
Challenge=i%27m_c0m1ng            ← ★ body，POST 参数在这
```

---

## 五、常见坑（考试重点）

1. **变量名大小写敏感**：题目写 `CTF`，传小写 `ctf` 不认。**照抄题目给的变量名**。
2. **URL 编码**：值里带特殊字符要编码。`'` → `%27`、空格 → `%20`、`&` → `%26`。
   - curl 里手写编码：`i'm_c0m1ng` → `i%27m_c0m1ng`
   - Python requests 用字典会自动编码，省心
3. **fetch 一定要 `.then`** 才能看到响应，否则只输出 Promise（下单了没取餐）
4. **多参数**用 `&` 连接：`?a=1&b=2`、`-d "a=1&b=2"`
5. GET/POST 参数**可以同一次请求都带**：`curl -X POST "网址?GET参数" -d "POST参数"`

---

## 六、离线/断网能不能传？（比赛关键）

```
① 打到靶机的网 ← POST 是发给【靶机】，不是外网。能开靶机 = 能连靶机 = 能传参 ✅
② 外网 ← 装工具、查 WP 才需要
```

- 线下赛：靶机在局域网，外网断了也能打
- 工具（curl/python/hackbar）都装在**本地**，发请求不需要外网
- ⚠️ 真正受"断网"影响的是**没提前装好的工具**——所以工具要**赛前装好**！

---

## 七、工具对比（选哪个用）

| 工具 | 类型 | GET | POST | 友好度 | 适用 |
|---|---|---|---|---|---|
| 地址栏 | 浏览器 | ✅ | ❌ | ★★★★★ | GET 试水 |
| curl | 命令行 | ✅ | ✅ | ★★★☆ | 刷题主力 |
| Python requests | 脚本 | ✅ | ✅ | ★★★☆ | 处理响应 |
| HackBar | 浏览器插件 | ✅ | ✅ | ★★★★ | 新手友好 |
| F12 Console | 浏览器 | ✅ | ✅ | ★★☆ | 应急 |
| Burp Suite | 抓包 | ✅ | ✅ | ★★ | 进阶改包 |

**推荐路线**：入门用 HackBar / curl → 进阶上 Burp Suite。
