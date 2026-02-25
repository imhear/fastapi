以下是一份完整的 Git 分支管理文档，基于你的需求（三个分支：`master`、`develop`、`stable`）设计。它涵盖了首次创建分支的场景以及日常操作的标准化流程。

---

## 分支角色定义

- **`master`**：仅用于跟踪上游官方仓库（`tiangolo/fastapi`）的 `master` 分支。始终保持纯净，不包含任何个人修改。用于获取上游更新并作为开发分支的基础。
- **`develop`**：个人开发主分支。所有新功能、实验、修改都在此分支上进行。可定期从 `master` 变基或合并以保持与上游同步。
- **`stable`**：个人稳定发布分支。当 `develop` 上的代码达到稳定可发布状态时，将其合并到 `stable`，并可以打标签。该分支用于部署或分发给用户。

---

## 首次设置（从现有仓库创建三分支结构）

假设你已经克隆了你的 fork 仓库（`origin`），并添加了上游（`upstream`）。以下步骤将重新整理分支，使它们符合上述角色。

### 1. 确保本地仓库干净
```bash
git status                 # 确认没有未提交的修改
```

### 2. 添加 upstream 远程（如果尚未添加）
```bash
git remote add upstream https://github.com/tiangolo/fastapi.git
git fetch upstream         # 获取上游所有分支
```

### 3. 重建 `master` 分支（使其与 upstream/master 一致）
```bash
# 如果本地已有 master 分支，先删除（谨慎，确保重要提交已备份）
git branch -D master       # 强制删除本地 master（如有必要）

# 从 upstream/master 创建新的本地 master
git checkout -b master upstream/master
git push -f origin master  # 强制更新远程 master（覆盖历史）
```

### 4. 创建/调整 `develop` 分支（保留你的开发历史）
假设你已经在 `develop` 分支上有一些提交。我们将其变基到新的 `master` 上，确保它基于最新上游。
```bash
git checkout develop       # 切换到 develop
git rebase master          # 将 develop 的提交放在 master 的最新提交之后
# 如果有冲突，解决后 git add . 然后 git rebase --continue
git push --force-with-lease origin develop   # 强制推送更新远程 develop
```
*如果本地还没有 `develop` 分支，可从 `master` 创建：*
```bash
git checkout -b develop master
```

### 5. 创建 `stable` 分支（从当前 develop 创建）
```bash
git checkout -b stable develop   # 基于 develop 创建 stable
git push -u origin stable        # 推送到远程，并建立跟踪
```

现在本地和远程都有了三个分支，结构如下：
- `master` 跟踪 `upstream/master`
- `develop` 包含你的开发历史，基于最新上游
- `stable` 包含当前的稳定快照

---

## 日常操作命令

### 1. 同步上游更新到 `master`
定期从官方仓库拉取最新代码，保持 `master` 更新。
```bash
git checkout master
git pull upstream master        # 拉取上游最新提交
git push origin master           # 推送到你的 fork（可选，但推荐）
```

### 2. 将上游更新合并到 `develop`
开发分支需要及时合并上游变更，避免落后太多。
```bash
git checkout develop
git rebase master                # 将 develop 的提交变基到最新 master 之上
# 或 git merge master（两者选一，rebase 可保持线性历史）
git push --force-with-lease origin develop   # 如果使用 rebase 则需要强制推送
```

### 3. 在 `develop` 上开发
日常开发流程：
```bash
git checkout develop
# 编写代码...
git add .
git commit -m "描述修改内容"
git push origin develop          # 推送到远程备份
```

### 4. 发布稳定版本到 `stable`
当 `develop` 上的功能足够稳定，准备发布时，将其合并到 `stable`。
```bash
git checkout stable
git merge --ff-only develop      # 如果 stable 是 develop 的直接祖先，快进合并
# 如果 stable 已有其他提交，使用 git merge develop 生成合并提交
git push origin stable
```

### 5. 为稳定版本打标签
推荐为每次发布打一个版本标签（例如 `v1.0-myfork`）。
```bash
git checkout stable
git tag -a v1.0.0-myfork -m "我的第一个稳定版本"
git push origin v1.0.0-myfork    # 推送标签到远程
```

---

## 其他常见场景

### 需要从 `develop` 中挑选特定提交到 `stable`
如果只想合并部分功能（而非整个 `develop`），可以使用 `cherry-pick`：
```bash
git checkout stable
git cherry-pick <commit-hash>    # 多次 cherry-pick 挑选多个提交
git push origin stable
```

### 修正历史（仅限个人分支）
在 `develop` 上，如果你需要修改最近一次提交：
```bash
git commit --amend               # 修改提交信息或内容
git push --force-with-lease origin develop
```

### 删除远程分支（如果不再需要）
```bash
git push origin --delete <branch-name>
```

---

## 注意事项

- **强制推送（`--force`）** 仅在个人分支（`develop`、`stable`）上使用，且最好用 `--force-with-lease` 更安全。`master` 应尽量避免强制推送，除非你确认没有其他人依赖它。
- 在切换分支前，务必提交或暂存当前工作区的修改（`git stash`），避免丢失。
- 定期执行 `git fetch --all --prune` 清理远程已删除分支的本地引用。
- 如果多人协作，请提前沟通分支策略，避免历史重写导致混乱。

---

## 示例工作流（从上游更新到发布）

1. 同步上游：`git checkout master && git pull upstream master && git push origin master`
2. 更新开发分支：`git checkout develop && git rebase master && git push --force-with-lease origin develop`
3. 日常开发并推送。
4. 准备发布：`git checkout stable && git merge develop && git push origin stable`
5. 打标签：`git tag v1.1.0 && git push origin v1.1.0`

这套流程将帮助你清晰管理三个分支，既保持与上游同步，又能独立发布自己的稳定版本。

---

## 工作流的改善方案（优化后完整流程）
# ========== 阶段1：同步上游（优化点：增加本地分支检查） ==========
git checkout master
git fetch upstream  # 先拉取上游最新，不直接合并
git pull upstream master  # 合并上游master到本地master
git push origin master    # 推送到自己的远程master

# ========== 阶段2：更新开发分支（核心优化：多人用merge，单人可选rebase） ==========
git checkout develop
git pull origin develop   # 先拉取远程develop最新（避免覆盖他人提交）
# 【关键】若develop是多人协作：用merge替代rebase，避免重写历史
git merge master          # 而非 rebase master
# 若仅单人开发，非要用rebase：先确认没有未推送的本地提交，再执行
# git rebase master
git push origin develop   # 多人协作时，去掉 --force-with-lease！

# ========== 阶段3：日常开发（新增：提交前验证） ==========
# 开发完成后，先本地验证（比如运行测试、编译）
pytest  # 假设是Python项目，运行单元测试
# 提交并推送
git add .
git commit -m "feat: 新增xxx功能"
git push origin develop

# ========== 阶段4：准备发布（核心优化：合并前拉取+合并后验证） ==========
git checkout stable
git pull origin stable    # 先拉取远程stable最新，避免本地过时
git merge develop         # 合并develop到stable
# 合并后必须本地验证（关键！）
pytest  # 运行测试，确保合并后代码无bug
# 验证通过后再提交+推送
git commit  # 完成合并提交（解决编辑器问题）
git push origin stable

# ========== 阶段5：打标签（优化点：标签备注+验证推送） ==========
# 打带备注的标签（更易追溯），而非轻量标签
git tag -a v1.1.0 -m "版本v1.1.0：新增xxx功能，修复xxx问题"
git push origin v1.1.0    # 推送标签到远程
# 验证标签是否推送成功
git fetch origin --tags
git tag -l | grep v1.1.0  # 确认标签存在
