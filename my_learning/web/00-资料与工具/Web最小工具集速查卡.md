# Web最小工具集速查卡（做题对照用）

> 目的：做题时照着抄，不用背。每行都是"干什么 + 命令"。

## 1. curl —— 发请求（万能基础）

### 🦴 万能骨架（记这个，不记参数）

```
curl.exe  网址   [怎么发]   [带什么]   [怎么收]
```

| 空位 | 参数 | 什么时候用 |
|---|---|---|
| 怎么发 | `-X POST` | 要提交数据时 |
| | `-d "k=v"` | 发简单表单数据 |
| | `--data-urlencode "k=v"` | 数据带特殊符号（`;` `&` 空格 `/`） |
| 带什么 | `-H "头: 值"` | 自定义请求头 / Cookie |
| | `-b 文件` | 带上之前存的 cookie |
| | `-c 文件` | 保存服务器发的 cookie |
| | `-A "UA"` | 伪装浏览器 |
| 怎么收 | `-o 文件` | 响应存文件 |
| | `-s` | 静默（去进度条） |
| | `-i` | 连响应头显示 |
| | `-w "%{http_code}"` | 只输出状态码 |
| | `-v` | 调试看完整报文 |

> 口诀：`curl 网址 + 怎么发 + 带什么 + 怎么收`，不需要的全不写。

| 要干什么 | 命令 |
|---|---|
| GET 一个页面 | `curl.exe http://地址/` |
| 看响应头（Server/PHP版本） | `curl.exe -i http://地址/` |
| POST 提交表单数据 | `curl.exe -X POST http://地址/ -d "参数=值"` |
| POST 提交带特殊符号的数据 | `curl.exe -X POST http://地址/ --data-urlencode "参数=值;符号"` |
| 保存服务器发的 cookie 到文件 | `curl.exe ... -c cookies.txt` |
| 带上 cookie 文件去请求 | `curl.exe ... -b cookies.txt` |
| 手动指定 cookie | `curl.exe ... -H "Cookie: session=xxx"` |
| 响应存文件 | `curl.exe ... -o 文件名` |
| 伪装浏览器 UA | `curl.exe ... -A "Mozilla/5.0 ..."` |
| 调试看完整报文 | `curl.exe ... -v` |
| 批量探测状态码 | `curl.exe -s -o NUL -w "%{http_code}" 地址` |

> Windows 必须写 `curl.exe`（PowerShell 的 `curl` 是别的命令的别名）。

## 2. flask-unsign —— 处理 Flask session cookie（3 个动词）

| 要干什么 | 命令 |
|---|---|
| 解码看 cookie 内容 | `flask-unsign --decode --cookie "<cookie值>"` |
| 爆破密钥（用字典试） | `flask-unsign --unsign --cookie "<cookie值>" --wordlist 字典.txt --no-literal-eval` |
| 用密钥伪造新 cookie | `flask-unsign --sign --secret "<密钥>" --cookie "{'name':'admin'}"` |

> 记住"解→爆→签"三步即可。

## 3. 爆破用弱密钥字典（怎么造）

```powershell
$wl = "secret,key,admin,litctf,LitCTF,ctf,flag,nssctf,hello,password,123456,test,root" -split ","
$wl | Set-Content wl.txt -Encoding ascii
```

**猜词规律**（把线索填进方框里）：
1. 通用弱密码：`secret` `admin` `password` `123456`
2. 框架名：`flask` `django`
3. 平台名：`nssctf`、`ctf`
4. **题目/赛事名**：`litctf` ← 页面标题写了啥就试啥
5. 常见变形：首字母大小写、加年份（litctf2023）

## 4. 做题通用套路（每题的骨架）

```
1. 信息收集：curl 看页面 + 响应头 → 判断技术栈（PHP? Flask?）
2. 找输入点：表单/参数 → 想它会被后端怎么用
3. 探测：正常提交 → 观察回显/响应头/cookie
4. 分析：哪个环节信任了用户输入 → 选漏洞类型
5. 利用：查本速查卡抄命令 → 拿 flag
6. 复盘：写 WP 进 my_learning/
```

> 命令记不住没关系，抄就行；真正要懂的是**每一步为什么存在**。
