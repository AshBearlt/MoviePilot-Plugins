from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.chain.download import DownloadChain
from app.chain.storage import StorageChain
from app.chain.transfer import TransferChain
from app.helper.downloader import DownloaderHelper
from app.log import logger
from app.plugins import _PluginBase
from app.schemas import FileItem, NotificationType
from app.schemas.types import DownloaderType
from app.utils.system import SystemUtils


class DownloadGuard(_PluginBase):
    """
    下载空间守护插件
    功能：当qBittorrent下载文件时，检测剩余空间，若剩余空间不足时调用一次手动整理指定目录
    """
    
    # 插件信息
    plugin_name = "下载空间守护"
    plugin_desc = "监控qBittorrent下载，空间不足时自动发起整理"
    plugin_icon = "https://raw.githubusercontent.com/AshBearlt/MoviePilot-Plugins/main/icons/scan.png"
    plugin_version = "1.0.1"
    plugin_author = "AshBearlt"
    author_url = "https://github.com/AshBearlt"
    plugin_config_prefix = "downloadguard_"
    plugin_order = 50
    auth_level = 1

    # 私有属性
    _enabled = False
    _message = "插件未启用"
    _min_free_space = 10  # 最小空间，单位：GB
    _interval_seconds = 300  # 定时检测间隔，单位：秒
    _cleanup_dirs = ""  # 要整理的目录，多个用英文逗号分隔
    _notify = True  # 是否发送通知
    _auto_cleanup = True  # 是否自动整理

    def init_plugin(self, config: dict = None):
        """初始化插件配置"""
        logger.warning(f"[DownloadGuard] init_plugin() 被调用，config={config}")
        # 停止现有任务
        self.stop_service()
        
        if config:
            self._enabled = config.get("enabled", False)
            self._min_free_space = float(config.get("min_free_space", 10) or 10)
            self._interval_seconds = int(config.get("interval_seconds", 300) or 300)
            self._cleanup_dirs = config.get("cleanup_dirs", "").strip()
            self._notify = config.get("notify", True)
            self._auto_cleanup = config.get("auto_cleanup", True)

        if self._interval_seconds < 30:
            self._interval_seconds = 30
        
        if self._enabled:
            self._message = "插件已启用"
            logger.warning(
                f"[DownloadGuard] ✓ 已启用，间隔: {self._interval_seconds}秒，"
                f"保留空间: {self._min_free_space}GB，目录: {self._cleanup_dirs}"
            )
        else:
            self._message = "插件未启用"
            logger.warning(f"[DownloadGuard] ✗ 插件未启用")

    def get_state(self) -> bool:
        """获取插件运行状态"""
        state = self._enabled
        # 每次调用都记录，便于调试
        logger.warning(f"[DownloadGuard] get_state() → {state}")
        return state

    def _scheduled_check(self):
        """定时检测：仅当 qBittorrent 有下载中任务时才检查空间。"""
        if not self._enabled:
            return

        try:
            logger.warning("[DownloadGuard] ⏱️ 定时检测触发")
            
            # 首先打印当前剩余空间
            if self._cleanup_dirs:
                dirs_to_cleanup = [
                    d.strip() for d in self._cleanup_dirs.split(",") 
                    if d.strip()
                ]
                valid_dirs = []
                for dir_path in dirs_to_cleanup:
                    path = Path(dir_path)
                    if path.exists() and path.is_dir():
                        valid_dirs.append(path)
                
                if valid_dirs:
                    try:
                        total_space, free_space = SystemUtils.space_usage(valid_dirs)
                        free_space_gb = free_space / (1024 ** 3)
                        total_space_gb = total_space / (1024 ** 3)
                        logger.warning(
                            f"[DownloadGuard] 💾 空间: 总容量={total_space_gb:.2f}GB, "
                            f"剩余={free_space_gb:.2f}GB, 阈值={self._min_free_space:.2f}GB"
                        )
                    except Exception as e:
                        logger.warning(f"[DownloadGuard] ⚠️ 获取空间出错: {str(e)}")
            
            has_downloading, downloading_count = self._has_qb_downloading_tasks()
            if not has_downloading:
                logger.warning("[DownloadGuard] ⏭️ 当前没有下载任务，跳过")
                return

            logger.warning(f"[DownloadGuard] 📥 检测到 {downloading_count} 个下载任务")

            self._check_and_cleanup_space()
        except Exception as e:
            logger.error(f"[DownloadGuard] ❌ 错误: {str(e)}", exc_info=True)
            self._send_notification(
                title="下载空间守护错误",
                text=f"定时检测出错: {str(e)}",
                mtype=NotificationType.Plugin
            )

    @staticmethod
    def _is_qb_service(service) -> bool:
        return bool(service and service.type == DownloaderType.Qbittorrent.value)

    def _has_qb_downloading_tasks(self) -> Tuple[bool, int]:
        """检查是否存在 qBittorrent 下载中任务。"""
        try:
            # 直接调用 DownloadChain，不传 name 参数则返回所有下载器的任务
            download_chain = DownloadChain()
            
            # 获取所有正在下载的任务
            torrents = download_chain.downloading()
            torrent_count = len(torrents) if torrents else 0
            
            logger.info(f"DownloadGuard: 检测到所有下载器正在下载的任务数: {torrent_count}")
            
            if torrents:
                # 可选：打印具体任务信息用于调试
                for torrent in torrents[:3]:  # 只打印前3个任务
                    logger.debug(f"DownloadGuard: 下载中任务 - {getattr(torrent, 'name', '未知')}")
            
            return torrent_count > 0, torrent_count
        except Exception as e:
            logger.error(f"DownloadGuard: 检测下载任务出错: {str(e)}", exc_info=True)
            return False, 0

    def _check_and_cleanup_space(self):
        """检查空间并清理"""
        if not self._cleanup_dirs:
            logger.warning("DownloadGuard: 未配置整理目录")
            return
        
        # 解析整理目录列表
        dirs_to_cleanup = [
            d.strip() for d in self._cleanup_dirs.split(",") 
            if d.strip()
        ]
        
        if not dirs_to_cleanup:
            logger.warning("DownloadGuard: 整理目录配置为空")
            return
        
        # 验证目录是否存在
        valid_dirs = []
        for dir_path in dirs_to_cleanup:
            path = Path(dir_path)
            if path.exists() and path.is_dir():
                valid_dirs.append(path)
            else:
                logger.warning(f"DownloadGuard: 整理目录不存在或不是目录: {dir_path}")
        
        if not valid_dirs:
            logger.warning("DownloadGuard: 没有有效的整理目录")
            return
        
        # 检查磁盘空间
        total_space, free_space = SystemUtils.space_usage(valid_dirs)
        free_space_gb = free_space / (1024 ** 3)
        total_space_gb = total_space / (1024 ** 3)
        
        logger.info(
            f"DownloadGuard: 检查目录 {valid_dirs} - "
            f"总空间: {total_space_gb:.2f}GB, "
            f"剩余空间: {free_space_gb:.2f}GB, "
            f"最小要求: {self._min_free_space:.2f}GB"
        )
        
        # 如果空间不足，进行整理
        if free_space_gb < self._min_free_space:
            logger.warning(
                f"DownloadGuard: 剩余空间不足 (剩余: {free_space_gb:.2f}GB < 最小要求: {self._min_free_space:.2f}GB)，"
                f"准备整理目录"
            )
            
            # 发送通知
            if self._notify:
                self._send_notification(
                    title="磁盘空间不足",
                    text=f"监控目录：{', '.join(str(d) for d in valid_dirs)}\n"
                         f"剩余空间：{free_space_gb:.2f}GB\n"
                         f"最小要求：{self._min_free_space:.2f}GB\n"
                         f"已触发{'自动整理' if self._auto_cleanup else '手动整理提醒'}",
                    mtype=NotificationType.Plugin
                )
            
            if self._auto_cleanup:
                self._perform_cleanup(valid_dirs)
        else:
            logger.info(f"DownloadGuard: 磁盘空间充足，无需整理")

    def _perform_cleanup(self, dirs: List[Path]):
        """执行整理操作"""
        try:
            transfer_chain = TransferChain()
            
            for cleanup_dir in dirs:
                logger.info(f"DownloadGuard: 开始整理目录 {cleanup_dir}")
                
                # 获取目录中的文件
                storage_chain = StorageChain()
                file_items = storage_chain.list_files(
                    fileitem=FileItem(
                        name=cleanup_dir.name,
                        path=str(cleanup_dir),
                        type="dir"
                    ),
                    recursion=False
                )
                
                if not file_items:
                    logger.info(f"DownloadGuard: 目录 {cleanup_dir} 中没有文件")
                    continue
                
                # 对每个文件项进行整理
                for file_item in file_items:
                    if file_item.type == "file":
                        logger.info(f"DownloadGuard: 整理文件 {file_item.path}")
                        try:
                            # 调用整理接口
                            success, message = transfer_chain.do_transfer(
                                fileitem=file_item,
                                manual=True,
                                background=True,
                                force=True
                            )
                            if success:
                                logger.info(f"DownloadGuard: 文件整理成功 {file_item.path}")
                            else:
                                logger.warning(
                                    f"DownloadGuard: 文件整理失败 {file_item.path}: {message}"
                                )
                        except Exception as e:
                            logger.error(
                                f"DownloadGuard: 整理文件失败 {file_item.path}: {str(e)}",
                                exc_info=True
                            )
                
                logger.info(f"DownloadGuard: 目录 {cleanup_dir} 整理完成")
            
            # 重新检查空间
            total_space, free_space = SystemUtils.space_usage(dirs)
            free_space_gb = free_space / (1024 ** 3)
            
            self._send_notification(
                title="磁盘空间整理完成",
                text=f"整理目录: {', '.join(str(d) for d in dirs)}\n"
                     f"剩余空间: {free_space_gb:.2f}GB",
                mtype=NotificationType.Plugin
            )
            
        except Exception as e:
            logger.error(
                f"DownloadGuard: 整理失败 {str(e)}",
                exc_info=True
            )
            self._send_notification(
                title="磁盘空间整理失败",
                text=f"整理过程中出错: {str(e)}",
                mtype=NotificationType.Plugin
            )

    def _send_notification(self, title: str, text: str, mtype: NotificationType):
        """发送通知"""
        if self._notify:
            try:
                self.post_message(
                    mtype=mtype,
                    title=title,
                    text=text
                )
            except Exception as e:
                logger.error(f"DownloadGuard: 发送通知失败 {str(e)}", exc_info=True)

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        """注册远程命令"""
        return []

    def get_api(self) -> List[Dict[str, Any]]:
        """注册插件API"""
        return []

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """返回插件配置表单"""
        return [
            {
                "component": "VForm",
                "content": [
                    {
                        "component": "VRow",
                        "content": [
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 6},
                                "content": [
                                    {
                                        "component": "VSwitch",
                                        "props": {
                                            "model": "enabled",
                                            "label": "启用插件",
                                        },
                                    }
                                ],
                            },
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 6},
                                "content": [
                                    {
                                        "component": "VSwitch",
                                        "props": {
                                            "model": "notify",
                                            "label": "启用通知",
                                        },
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "component": "VRow",
                        "content": [
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 6},
                                "content": [
                                    {
                                        "component": "VSwitch",
                                        "props": {
                                            "model": "auto_cleanup",
                                            "label": "自动整理（关闭则仅提醒）",
                                        },
                                    }
                                ],
                            },
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 6},
                                "content": [
                                    {
                                        "component": "VTextField",
                                        "props": {
                                            "model": "min_free_space",
                                            "label": "最小保留空间 (GB)",
                                            "type": "number",
                                            "hint": "当剩余空间低于此值时触发整理",
                                        },
                                    }
                                ],
                            },
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 6},
                                "content": [
                                    {
                                        "component": "VTextField",
                                        "props": {
                                            "model": "interval_seconds",
                                            "label": "检测间隔 (秒)",
                                            "type": "number",
                                            "hint": "最小 30 秒，仅在 qB 有下载中任务时检测",
                                        },
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "component": "VRow",
                        "content": [
                            {
                                "component": "VCol",
                                "props": {"cols": 12},
                                "content": [
                                    {
                                        "component": "VTextField",
                                        "props": {
                                            "model": "cleanup_dirs",
                                            "label": "整理目录",
                                            "placeholder": "/path/to/dir1,/path/to/dir2",
                                            "hint": "多个目录用英文逗号分隔，通常为下载目录",
                                            "rows": 3,
                                        },
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "component": "VAlert",
                        "props": {
                            "type": "info",
                            "variant": "tonal",
                            "text": "此插件按设定间隔定时检测磁盘空间，且仅在 qBittorrent 有下载中任务时执行。空间不足时会将文件加入整理队列。",
                        },
                    },
                ],
            }
        ], {
            "enabled": False,
            "notify": True,
            "auto_cleanup": True,
            "min_free_space": 10,
            "interval_seconds": 300,
            "cleanup_dirs": "",
        }

    def get_service(self) -> List[Dict[str, Any]]:
        """注册定时检测服务。"""
        logger.warning(f"[DownloadGuard] get_service() 被调用，enabled={self._enabled}")
        if not self._enabled:
            logger.warning(f"[DownloadGuard] 插件未启用，返回空列表")
            return []
        logger.warning(f"[DownloadGuard] ✓ 返回服务列表：间隔 {self._interval_seconds} 秒")
        return [
            {
                "id": "DownloadGuard.Check",
                "name": "下载空间定时检测",
                "trigger": "interval",
                "func": self._scheduled_check,
                "kwargs": {
                    "seconds": int(self._interval_seconds),
                },
            }
        ]

    def get_page(self) -> List[dict]:
        """返回插件详情页"""
        return [
            {
                "component": "VAlert",
                "props": {
                    "type": "info",
                    "variant": "tonal",
                    "text": self._message,
                },
            }
        ]

    def stop_service(self):
        """停止服务"""
        pass
