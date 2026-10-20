# MISC 第 6 题「不想上早八」（qsnctf / 青少年CTF训练）

标签：流量分析 / FTP 明文密码 / AES 加密 ZIP / 零宽字符隐写（unicodeSteganographer）

## 题目特征
- 附件 `题目附件.zip` 含三个文件：
  - `数据包.pcapng` —— 流量包
  - `详细说明.txt` —— 剧情：学弟传了加密文件，密码是老师电脑密码，要从流量里找
  - `加密内容.zip` —— AES 加密的 zip（method 99），里面 `我不想上早八了老师.txt`
- flag 藏在 txt 的**零宽字符**里。

## 解题步骤

### 1. 分析流量包，找 FTP 登录密码
用 dpkt 解析 pcapng，发现主体是 **FTP（端口 21）** 会话：

    USER uftp
    PASS xyvtc2024        <-- 这就是老师电脑密码 / zip 密码
    230 Login successful.

> 关键点：FTP 登录的 USER/PASS 是**明文**传输的，直接抓流量就能看到。

### 2. 用密码解 AES 加密 zip
`加密内容.zip` 是 AES 加密（method 99），用 `xyvtc2024` 解开：

    import pyzipper
    z = pyzipper.AESZipFile('加密内容.zip')
    data = z.read(z.namelist()[0], pwd=b'xyvtc2024')

解出 `我不想上早八了老师.txt`，内容是一堆重复的"我真的真的真的不想上早八"——**肉眼看到的文字是障眼法，真信息在零宽字符里**。

### 3. 零宽字符解码（本题核心坑）
文件里实际有 **4 种零宽字符**（之前漏检 U+202C 是失败主因）：
- `U+200C` × 219
- `U+200D` × 55
- `U+202C` × 34
- `U+FEFF` × 36

这正是 `unicodeSteganographer` 库的默认字符集 `setUseChars('u200cu200du202cufeff')`。

### 4. 解码算法（radix=4）
- 每种零宽字符 = 一个数字：200C=0, 200D=1, 202C=2, FEFF=3（顺序按库定义）
- radix=4，每 `ceil(log(256)/log(4)) = 4` 个零宽字符 = 1 个字节
- 344 个零宽字符 / 4 = 86 字节
- **关键坑**：解码出的字节流是 **UTF-16 编码**（每字符 2 字节，高字节为 0x00），且是大端（BE）

还原脚本（Node.js，复现 unicodeSteganographer 逻辑）：

    const C=String.fromCharCode(0x200c), D=String.fromCharCode(0x200d),
          E=String.fromCharCode(0x202c), F=String.fromCharCode(0xfeff);
    const chars=[C,D,E,F];
    let hidden='';
    for(const ch of text){ if(chars.includes(ch)) hidden+=ch; }
    const radix=4, clen=4;
    let bytes=[];
    for(let i=0;i+clen<=hidden.length;i+=clen){
      let g=hidden.substr(i,clen);
      let num=''; for(const ch of g) num+=chars.indexOf(ch);
      bytes.push(parseInt(num,radix));
    }
    // UTF-16BE: bytes[i] 高位(0x00), bytes[i+1] 低位(字符)
    let out='';
    for(let i=0;i+1<bytes.length;i+=2){
      out += String.fromCharCode((bytes[i]<<8) | bytes[i+1]);
    }
    console.log(out);  // xyvtc{9bfd8ebf-e0e0-48f7-85ab-051075e2167c}

### 5. 在线工具捷径
这题用 yuanfux.github.io/zero-width-web 或 mzy0.com/ctftools/zerowidth1 直接粘贴 txt 内容也能解（WP 原文说"在线工具解密得到flag"）。但注意有些在线工具对 4 字符集 + UTF-16 的支持不一致，自己写脚本最稳。

## Flag
    xyvtc{9bfd8ebf-e0e0-48f7-85ab-051075e2167c}

注意前缀是 `xyvtc{`（青少年CTF），不是 qsnctf。

## 知识点
1. **FTP 明文抓密码**：FTP 的 USER/PASS 不加密，流量里直接明文。pcapng 用 dpkt 按 TCP 端口 21 过滤，客户端->21 的方向就是账号密码。
2. **AES 加密 ZIP**：method 99 是 WinZip AES，需用 pyzipper（标准 zipfile 不支持），`z.read(name, pwd=b'xxx')`。
3. **零宽字符检测要"全"**：必须检测所有零宽类字符（200B/200C/200D/200E/200F/202C/2060/FEFF 等），本题漏掉 U+202C 会导致字符集错（radix 算错）全盘失败。
4. **unicodeSteganographer 算法**：4 种字符 = radix 4，每 4 字符 = 1 字节（codelengthBinary=ceil(log256/log4)=4）。
5. **UTF-16 陷阱**：解码出的字节流每字符占 2 字节（0x00 高位），要按 UTF-16 还原，不是直接按 ASCII 字节读——否则看到一堆 "U" 间隔的乱码（U=0x55）。
6. **steghide 不适用**：这是文本零宽隐写，不是图片/音频隐写，用 steghide 会报"格式不支持"。正确工具是零宽解码器（在线或 unicodeSteganographer）。

## 遇到的坑（复盘）
- 最初只检测 200C/200D/FEFF 三种，漏了 U+202C（34个），误判 radix=3，全盘乱码。
- 用 Base-3 / 二进制固定位宽硬切都失败，因为没识别完整 4 字符集 + UTF-16 编码。
- 字节序：零宽解码出 `00 78 00 79` 是 UTF-16BE（高位在前），误用 LE 会得到乱码汉字。
