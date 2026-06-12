# 🎉 DownloadGuard 插件 - 快速开始指南

欢迎使用 DownloadGuard（下载空间守护）插件！本文档帮助你快速上手。

## 📌 当前状态

✅ **插件已正常运行**
- 位置：`~/MoviePilot-Plugins/plugins/downloadguard/`
- 本地仓库已配置
- 热加载功能可用
- 定时检测每 30 秒执行一次

## 🚀 快速开始

### 1️⃣ 已完成的配置

```bash
# 本地插件仓库已创建
ls -la ~/MoviePilot-Plugins/plugins/

# 输出应该是：
# downloadguard/    <- DownloadGuard 插件
```

### 2️⃣ 验证插件正在运行

```bash
# 查看插件日志
tail -f ~/workspace/MoviePilot2/moviepilot-local-config/logs/plugins/downloadguard.log

# 应该看到类似输出：
# 【INFO】DownloadGuard: 定时检测触发
# 【INFO】DownloadGuard: 监控目录剩余空间 - 总容量: 228.27GB, 剩余: 75.31GB
```

### 3️⃣ 在 MoviePilot UI 中查看

1. 打开 MoviePilot：http://127.0.0.1:65041
2. 进入「设置」→「插件」
3. 搜索「下载空间守护」或「DownloadGuard」
4. 点击进入配置插件

## ⚙️ 插件配置

### 基本配置

| 选项 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| **启用** | 是否启用插件 | `true` | - |
| **发送通知** | 空间不足时是否发送通知 | `true` | - |
| **自动整理** | 是否自动队列转移（false=仅通知） | `true` | - |
| **最小保留空间** | 触发整理的最小保留空间（GB） | `75` | 100 |
| **检测间隔** | 定时检测间隔（秒，最小30） | `30` | 60 |
| **监控目录** | 要监控的目录（逗号分隔） | - | `/path/to/downloads` |

### 配置示例

**场景 1：小磁盘（500GB），保留 100GB**
```
启用：true
最小保留空间：100
检测间隔：60
监控目录：/mnt/downloads
```

**场景 2：大磁盘（10TB），保留 1TB**
```
启用：true
最小保留空间：1000
检测间隔：300
监控目录：/media/downloads,/mnt/downloads
```

## 📊 工作流程

```
每 30 秒（可配置）
    ↓
检测 qBittorrent 是否有下载任务
    ↓
    ├─ 无任务 → 跳过本次检测
    └─ 有任务 ↓
      检查磁盘剩余空间
        ↓
        ├─ 空间充足 → 记录日志，继续等待
        └─ 空间不足 ↓
          发送通知（如已启用）
          ↓
          ├─ auto_cleanup=false → 仅通知，不整理
          └─ auto_cleanup=true → 自动队列转移文件
```

## 🔍 日志查看

### 实时查看日志

```bash
# 查看插件日志
tail -f ~/workspace/MoviePilot2/moviepilot-local-config/logs/plugins/downloadguard.log

# 查看主日志
tail -f ~/workspace/MoviePilot2/moviepilot-local-config/logs/moviepilot.log

# 搜索特定内容
grep "定时检测触发" ~/workspace/MoviePilot2/moviepilot-local-config/logs/plugins/downloadguard.log
```

### 日志级别说明

| 级别 | 符号 | 说明 |
|------|------|------|
| INFO | ℹ️ | 正常信息 |
| WARNING | ⚠️ | 警告信息 |
| ERROR | ❌ | 错误信息 |

## 🛠️ 常见操作

### 重启 MoviePilot

```bash
moviepilot stop --force && sleep 5 && moviepilot start
```

### 启用/禁用热加载

编辑 `~/workspace/MoviePilot2/MoviePilot/.moviepilot.env`：

```bash
# 启用热加载（自动检测文件变化）
PLUGIN_AUTO_RELOAD=true

# 禁用热加载（需要手动重启）
PLUGIN_AUTO_RELOAD=false
```

### 修改检测间隔

在 MoviePilot UI 中修改：
- 进入「设置」→「插件」→「下载空间守护」
- 修改「检测间隔」字段
- 点击保存

最小值：30 秒
推荐值：30-300 秒（根据你的需求）

## 📤 上传到 GitHub（可选）

当你准备分享这个插件时：

```bash
cd ~/MoviePilot-Plugins
git init
git add .
git commit -m "Initial commit"
# 然后按照 GITHUB_UPLOAD.md 的步骤上传
```

详见：[GITHUB_UPLOAD.md](GITHUB_UPLOAD.md)

## 🗂️ 文件结构

```
~/MoviePilot-Plugins/
├── plugins/
│   └── downloadguard/
│       ├── __init__.py              # 插件主程序
│       ├── web/                     # Web UI（如果有）
│       └── static/                  # 静态资源
├── README.md                        # 仓库说明
├── plugins.json                     # 插件元数据
├── LOCAL_REPO_GUIDE.md             # 本地仓库详细指南
├── GITHUB_UPLOAD.md                # GitHub 上传指南
├── LICENSE                         # 许可证
└── .gitignore                      # Git 忽略规则
```

## ⚡ 性能提示

1. **检测间隔**：太频繁（<30秒）会增加 CPU 负载
2. **监控目录**：避免监控系统目录
3. **自动整理**：启用自动整理时会异步队列转移，不会阻塞检测

## 🆘 故障排除

### Q: 插件未出现在 MoviePilot 中

```bash
# 1. 检查配置
grep PLUGIN_LOCAL_REPO_PATHS ~/workspace/MoviePilot2/MoviePilot/.moviepilot.env

# 2. 查看日志
grep -i "error" ~/workspace/MoviePilot2/moviepilot-local-config/logs/moviepilot.log

# 3. 重启 MoviePilot
moviepilot restart
```

### Q: 定时检测没有执行

```bash
# 查看插件日志
tail -100 ~/workspace/MoviePilot2/moviepilot-local-config/logs/plugins/downloadguard.log

# 检查是否启用
grep "已启用" ~/workspace/MoviePilot2/moviepilot-local-config/logs/plugins/downloadguard.log
```

### Q: 空间检测不准确

```bash
# 手动检查磁盘空间
df -h /path/to/directory

# 查看 MoviePilot 的空间计算
grep "总容量" ~/workspace/MoviePilot2/moviepilot-local-config/logs/plugins/downloadguard.log
```

## 📞 获取帮助

1. 查看日志了解错误详情
2. 检查配置是否正确
3. 尝试重启 MoviePilot
4. 在本仓库提交 Issue

## 🎓 进阶使用

### 添加新插件到仓库

```bash
# 1. 创建新插件目录
mkdir ~/MoviePilot-Plugins/plugins/myplugin
cp -r /path/to/plugin/* ~/MoviePilot-Plugins/plugins/myplugin/

# 2. 更新 plugins.json
# 编辑 ~/MoviePilot-Plugins/plugins.json 添加新插件信息

# 3. 重启 MoviePilot（或等待热加载）
moviepilot restart
```

详见：[LOCAL_REPO_GUIDE.md](LOCAL_REPO_GUIDE.md)

### 开发自己的插件

参考 DownloadGuard 的代码结构，从 `~/MoviePilot-Plugins/plugins/downloadguard/__init__.py` 开始。

## 📚 参考资源

- [MoviePilot 官方仓库](https://github.com/jxxghp/MoviePilot)
- [MoviePilot 插件开发](https://github.com/jxxghp/MoviePilot-Plugins)
- [本项目 GitHub](https://github.com/YOUR_USERNAME/MoviePilot-Plugins)

## 📝 更新日志

### v1.0.0 (2026-06-11)
- ✨ 首个版本发布
- ✨ 实现定时空间监控
- ✨ 支持自动/手动整理触发
- ✨ 消息通知功能
- ✨ 完整的日志记录

---

**祝你使用愉快！** 🚀

如有问题，欢迎反馈！

