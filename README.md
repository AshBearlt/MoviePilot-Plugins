# MoviePilot 个人插件仓库

本仓库包含自定义的 MoviePilot 插件。

## 插件列表

### 1. DownloadGuard（下载空间守护）

**功能描述：**
- 监控 qBittorrent 下载任务
- 实时检测磁盘空间使用情况
- 空间不足时自动或手动触发文件整理
- 支持自定义检测间隔和空间阈值

**版本：** 1.0.0

**作者：** AshBearlt

**功能特性：**
- ✅ 定时检测（可配置间隔，最小 30 秒）
- ✅ 实时空间监控
- ✅ 自动或手动整理触发
- ✅ 消息通知
- ✅ 自定义监控目录

## 使用方式

### 方式一：本地插件仓库（推荐）

1. 克隆本仓库到本地：
```bash
git clone https://github.com/YOUR_USERNAME/MoviePilot-Plugins.git ~/MoviePilot-Plugins
```

2. 在 MoviePilot 中配置本地插件仓库目录：
   - 进入 MoviePilot 设置
   - 找到「插件」或「开发者」设置
   - 在「本地插件仓库目录」中填入：`~/MoviePilot-Plugins/plugins`
   - 保存并重启（或热加载会自动检测）

3. 在插件市场中即可看到本仓库的插件，点击安装即可

### 方式二：直接从本仓库添加

1. 在 MoviePilot 插件市场中
2. 选择「添加仓库」
3. 输入本仓库地址（如果已发布）

## 插件配置

### DownloadGuard 配置示例

```json
{
  "enabled": true,
  "notify": true,
  "auto_cleanup": true,
  "min_free_space": 75,
  "interval_seconds": 30,
  "cleanup_dirs": "/path/to/download/folder"
}
```

**参数说明：**
- `enabled`: 是否启用插件
- `notify`: 是否发送通知
- `auto_cleanup`: 是否自动整理（true=自动队列 false=仅通知）
- `min_free_space`: 最小保留空间（GB）
- `interval_seconds`: 检测间隔（秒，最小 30）
- `cleanup_dirs`: 要监控的目录（多个用逗号分隔）

## 更新日志

### v1.0.0 (2026-06-11)
- 🎉 首个版本发布
- ✨ 实现定时检测功能
- ✨ 支持多目录监控
- ✨ 集成消息通知系统

## 许可证

MIT License

## 反馈与支持

如有问题或建议，欢迎提交 Issue 或 Pull Request。

