# 上传到 GitHub 指南

## 前置准备

确保已安装 Git：
```bash
which git
```

## 步骤一：初始化 Git 仓库

```bash
cd ~/MoviePilot-Plugins
git init
git config user.name "Your Name"
git config user.email "your@email.com"
```

## 步骤二：添加文件到 Git

```bash
git add .
git commit -m "Initial commit: Add DownloadGuard plugin"
```

## 步骤三：在 GitHub 创建新仓库

1. 访问 https://github.com/new
2. 填写信息：
   - **Repository name**: `MoviePilot-Plugins`
   - **Description**: `Personal MoviePilot plugins repository / MoviePilot 个人插件仓库`
   - **Public/Private**: 选择 **Public**（这样他人可以添加你的仓库）
   - **Initialize this repository**: 不勾选（因为我们已本地初始化）

3. 点击 **Create repository**

## 步骤四：关联远程仓库并推送

```bash
# 替换 YOUR_USERNAME 为你的 GitHub 用户名
git remote add origin https://github.com/YOUR_USERNAME/MoviePilot-Plugins.git
git branch -M main
git push -u origin main
```

如果遇到认证问题，可以使用 Personal Access Token：
```bash
# 1. 在 GitHub 创建 Personal Access Token
#    https://github.com/settings/tokens
#    选择 repo 权限

# 2. 使用 token 推送
git push -u origin main
# 输入 username 和 token（作为密码）
```

## 步骤五：在 MoviePilot 中添加自定义仓库

### 方式一：本地路径（已配置）
已在 `.moviepilot.env` 中配置：
```
PLUGIN_LOCAL_REPO_PATHS=~/MoviePilot-Plugins/plugins
```

### 方式二：GitHub 仓库（推送后）
1. 在 MoviePilot 的插件管理中
2. 找到「添加仓库」或「自定义仓库」
3. 输入你的仓库 URL：`https://github.com/YOUR_USERNAME/MoviePilot-Plugins`
4. 保存后即可安装

## 后续维护

### 更新插件版本

1. 修改 [plugins/downloadguard/__init__.py](plugins/downloadguard/__init__.py) 中的 `plugin_version`
2. 更新 [plugins.json](plugins.json) 中的版本号
3. 提交并推送：

```bash
git add .
git commit -m "chore: Update DownloadGuard to v1.1.0"
git push
```

### 添加新插件

1. 在 `plugins/` 目录下创建新插件目录
2. 更新 `plugins.json`
3. 更新 `README.md`
4. 提交并推送

## 常用 Git 命令

```bash
# 查看状态
git status

# 查看提交历史
git log --oneline

# 撤销本地更改
git checkout -- .

# 删除未跟踪的文件
git clean -fd

# 查看远程仓库
git remote -v

# 更新本地仓库
git pull origin main
```

## 常见问题

### Q: 如何从本地仓库更新到 GitHub？
A: 修改后执行 `git add . && git commit -m "message" && git push`

### Q: 如何让他人使用我的插件？
A: 分享你的 GitHub 仓库 URL，他们可以在 MoviePilot 中添加为自定义仓库

### Q: 本地仓库和 GitHub 仓库可以同时用吗？
A: 可以！在 `.moviepilot.env` 中配置本地路径，MoviePilot 会自动同步两个来源的插件

## 参考链接

- [GitHub 官方文档](https://docs.github.com)
- [Git 官方文档](https://git-scm.com/doc)
- [MoviePilot 插件开发文档](https://github.com/jxxghp/MoviePilot)
