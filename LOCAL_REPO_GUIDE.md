# 本地插件仓库使用指南

## 📍 仓库位置

```
~/MoviePilot-Plugins/
├── plugins/
│   └── downloadguard/          # 插件目录
│       ├── __init__.py         # 插件主文件
│       ├── web/                # Web UI (如果有)
│       └── ...
├── README.md                   # 说明文档
├── plugins.json               # 插件信息配置
├── .gitignore                 # Git 忽略规则
├── LICENSE                    # 许可证
└── GITHUB_UPLOAD.md          # GitHub 上传指南
```

## 🚀 当前配置

已在 MoviePilot 的 `.moviepilot.env` 中配置：

```bash
PLUGIN_LOCAL_REPO_PATHS=~/MoviePilot-Plugins/plugins,/Users/arukoii/MoviePilot-Plugins/plugins
```

这意味着：
- MoviePilot 会自动监视 `~/MoviePilot-Plugins/plugins` 目录
- 该目录中的插件会被自动加载
- 插件文件更改时会自动热加载（如已启用热加载）

## 📦 添加新插件

### 步骤 1：创建插件目录

```bash
mkdir ~/MoviePilot-Plugins/plugins/myplugin
cd ~/MoviePilot-Plugins/plugins/myplugin
```

### 步骤 2：创建插件文件

创建 `__init__.py`：

```python
from app.plugins import _PluginBase
from app.log import logger

class MyPlugin(_PluginBase):
    plugin_name = "我的插件"
    plugin_desc = "插件描述"
    plugin_version = "1.0.0"
    plugin_author = "你的名字"
    plugin_order = 50

    def init_plugin(self, config: dict = None):
        """初始化插件"""
        pass

    def get_state(self) -> bool:
        """获取插件状态"""
        return True
```

### 步骤 3：更新配置

编辑 `~/MoviePilot-Plugins/plugins.json`：

```json
{
  "repo_name": "MoviePilot 个人插件仓库",
  "plugins": [
    {
      "id": "MyPlugin",
      "name": "我的插件",
      "version": "1.0.0",
      "description": "插件描述",
      "plugin_path": "plugins/myplugin"
    }
  ]
}
```

### 步骤 4：重启 MoviePilot

```bash
moviepilot restart
# 或使用热加载（如已启用）
```

## 🔄 热加载功能

### 启用热加载

在 MoviePilot `.moviepilot.env` 中添加：

```bash
PLUGIN_AUTO_RELOAD=true
```

### 热加载工作原理

- 监视 `PLUGIN_LOCAL_REPO_PATHS` 中的所有目录
- 检测到文件变化时自动重新加载插件
- **不需要重启 MoviePilot**
- 最小化服务中断时间

### 热加载限制

- 不能检测新增的插件目录（需要重启）
- 某些类型的更改可能需要重启
- 数据库更改通常需要重启

## 📝 文件结构规范

```
plugins/pluginname/
├── __init__.py                 # 必需：主插件类
├── web/
│   ├── index.html             # 可选：前端页面
│   └── ...
├── static/
│   ├── css/                   # 可选：样式表
│   ├── js/                    # 可选：脚本
│   └── images/                # 可选：图片
├── README.md                  # 可选：插件说明
└── requirements.txt           # 可选：依赖列表
```

## 🔧 测试插件

### 本地测试

1. 在 `~/MoviePilot-Plugins/plugins/` 中创建插件
2. 重启或热加载 MoviePilot
3. 在 MoviePilot UI 中检查是否加载

### 调试日志

查看插件特定日志：

```bash
tail -f ~/workspace/MoviePilot2/moviepilot-local-config/logs/plugins/pluginname.log
```

### 完整日志

查看主日志：

```bash
tail -f ~/workspace/MoviePilot2/moviepilot-local-config/logs/moviepilot.log
```

## 🗂️ 管理多个插件

支持在同一仓库中管理多个插件：

```
~/MoviePilot-Plugins/plugins/
├── downloadguard/
├── myplugin1/
├── myplugin2/
└── ...
```

每个插件是独立的目录，MoviePilot 会自动扫描并加载。

## 🔐 权限管理

确保插件目录具有正确的权限：

```bash
chmod -R 755 ~/MoviePilot-Plugins/
```

## 📤 推送到 GitHub

当准备好上传时，参考 [GITHUB_UPLOAD.md](GITHUB_UPLOAD.md)

## ⚡ 性能建议

1. **避免频繁修改**：修改前禁用热加载，修改后重启
2. **大文件**：将大文件放在 `static/` 目录
3. **依赖管理**：使用 `requirements.txt` 声明依赖
4. **日志**：使用 `logger.info()` 而不是 `print()`

## 🆘 故障排除

### 插件未加载

1. 检查插件目录名是否与类名对应
2. 查看 `moviepilot.log` 中的错误信息
3. 确认 `PLUGIN_LOCAL_REPO_PATHS` 配置正确

```bash
grep -E "error|ERROR|Failed" ~/workspace/MoviePilot2/moviepilot-local-config/logs/moviepilot.log
```

### 热加载失效

1. 确认已启用 `PLUGIN_AUTO_RELOAD=true`
2. 重启监控线程：重启 MoviePilot
3. 检查文件权限

### 导入错误

1. 检查依赖是否已安装
2. 确认导入路径正确
3. 查看 `plugins/pluginname.log`

## 📚 参考资源

- [MoviePilot 官方插件开发](https://github.com/jxxghp/MoviePilot)
- [Python 包导入](https://docs.python.org/3/reference/import_system.html)
- [JSON 格式](https://www.json.org)
