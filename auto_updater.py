"""
自动热更新模块

支持在不重新下载整个exe/容器的情况下，自动更新少量修改的文件。

更新机制：
1. 从远程服务器获取更新清单（包含文件列表、版本、MD5哈希）
2. 比较本地文件与远程文件的哈希值
3. 只下载有变化的文件
4. 备份旧文件，下载新文件
5. 需要时重启应用

支持更新的文件类型：
- Python 源文件 (.py)
- 前端文件 (.js, .css, .html)
- 配置文件 (.yml, .json)
- 静态资源
"""

import os
import sys
import json
import hashlib
import shutil
import tempfile
import asyncio
import aiohttp
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from loguru import logger
from dataclasses import dataclass, asdict
from enum import Enum


class UpdateStatus(Enum):
    """更新状态"""
    IDLE = "idle"                      # 空闲
    CHECKING = "checking"              # 检查中
    DOWNLOADING = "downloading"        # 下载中
    INSTALLING = "installing"          # 安装中
    COMPLETED = "completed"            # 完成
    FAILED = "failed"                  # 失败
    RESTART_REQUIRED = "restart_required"  # 需要重启


@dataclass
class FileUpdate:
    """文件更新信息"""
    path: str                 # 相对路径
    md5: str                  # MD5哈希
    size: int                 # 文件大小
    download_url: str         # 下载URL
    version: str              # 文件版本
    requires_restart: bool    # 是否需要重启
    description: str = ""     # 更新说明


@dataclass
class UpdateManifest:
    """更新清单"""
    version: str                      # 版本号
    release_date: str                 # 发布日期
    description: str                  # 版本说明
    files: List[FileUpdate]           # 文件列表
    min_version: str = ""             # 最低兼容版本
    changelog: List[str] = None       # 更新日志


@dataclass
class UpdateProgress:
    """更新进度"""
    status: UpdateStatus
    current_file: str = ""
    current_index: int = 0
    total_files: int = 0
    downloaded_bytes: int = 0
    total_bytes: int = 0
    message: str = ""
    error: str = ""


class AutoUpdater:
    """自动更新器"""
    
    # [安全修复] 禁用自动更新，原服务器为不可信的HTTP裸IP，存在远程代码执行风险
    DEFAULT_UPDATE_SERVER = ""
    AUTO_UPDATE_DISABLED = True
    
    # 可热更新的文件类型（不需要重启）
    HOT_UPDATABLE_EXTENSIONS = {'.js', '.css', '.html', '.json', '.yml', '.yaml'}
    
    # 需要重启的文件类型
    RESTART_REQUIRED_EXTENSIONS = {'.py', '.pyd', '.so', '.dll', '.exe'}
    
    # 不允许更新的文件/目录
    EXCLUDED_PATHS = {
        'data/',
        'logs/',
        'browser_data/',
        'uploads/',
        '__pycache__/',
        '.git/',
        'global_config.yml',  # 用户配置文件不更新
    }
    
    def __init__(self, 
                 app_dir: Optional[str] = None,
                 update_server: Optional[str] = None,
                 current_version: str = "1.0.0"):
        """
        初始化更新器
        
        Args:
            app_dir: 应用目录，默认为当前工作目录
            update_server: 更新服务器地址
            current_version: 当前版本号
        """
        self.app_dir = Path(app_dir) if app_dir else Path.cwd()
        self.update_server = update_server or self.DEFAULT_UPDATE_SERVER
        self.current_version = current_version
        self.backup_dir = self.app_dir / "update_backup"
        
        # 更新状态
        self.progress = UpdateProgress(status=UpdateStatus.IDLE)
        self._update_callbacks: List[callable] = []
        
        # 确保备份目录存在
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"自动更新器初始化: app_dir={self.app_dir}, server={self.update_server}, version={self.current_version}")
    
    def add_progress_callback(self, callback: callable):
        """添加进度回调"""
        self._update_callbacks.append(callback)
    
    def _notify_progress(self):
        """通知进度更新"""
        for callback in self._update_callbacks:
            try:
                callback(self.progress)
            except Exception as e:
                logger.error(f"进度回调执行失败: {e}")
    
    def _update_progress(self, **kwargs):
        """更新进度"""
        for key, value in kwargs.items():
            if hasattr(self.progress, key):
                setattr(self.progress, key, value)
        self._notify_progress()
    
    def _calculate_file_md5(self, file_path: Path) -> str:
        """计算文件MD5"""
        if not file_path.exists():
            return ""
        
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    
    def _is_excluded(self, path: str) -> bool:
        """检查路径是否被排除"""
        path_lower = path.lower().replace('\\', '/')
        for excluded in self.EXCLUDED_PATHS:
            if path_lower.startswith(excluded.lower()) or excluded.lower() in path_lower:
                return True
        return False
    
    def _needs_restart(self, file_path: str) -> bool:
        """检查文件更新是否需要重启"""
        ext = Path(file_path).suffix.lower()
        return ext in self.RESTART_REQUIRED_EXTENSIONS
    
    async def check_for_updates(self) -> Optional[UpdateManifest]:
        """
        检查是否有可用更新
        
        Returns:
            UpdateManifest: 更新清单，如果没有更新则返回None
        """
        self._update_progress(status=UpdateStatus.CHECKING, message="正在检查更新...")
        
        if self.AUTO_UPDATE_DISABLED:
            logger.warning("自动更新已禁用(安全原因: 原更新服务器为不可信HTTP源，存在远程代码执行风险)")
            self._update_progress(status=UpdateStatus.IDLE, message="自动更新已禁用(安全原因)")
            return None
        
        try:
            manifest_url = f"{self.update_server}/xianyu/update_manifest.php?version={self.current_version}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(manifest_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        logger.warning(f"获取更新清单失败: HTTP {response.status}")
                        self._update_progress(status=UpdateStatus.IDLE, message="检查更新失败")
                        return None
                    
                    data = await response.json()
                    
                    if not data.get('success'):
                        logger.info(f"没有可用更新: {data.get('message', '未知')}")
                        self._update_progress(status=UpdateStatus.IDLE, message="已是最新版本")
                        return None
                    
                    manifest_data = data.get('data', {})
                    
                    # 解析文件列表
                    files = []
                    for file_info in manifest_data.get('files', []):
                        files.append(FileUpdate(
                            path=file_info['path'],
                            md5=file_info['md5'],
                            size=file_info.get('size', 0),
                            download_url=file_info['download_url'],
                            version=file_info.get('version', manifest_data.get('version', '')),
                            requires_restart=file_info.get('requires_restart', self._needs_restart(file_info['path'])),
                            description=file_info.get('description', '')
                        ))
                    
                    manifest = UpdateManifest(
                        version=manifest_data.get('version', ''),
                        release_date=manifest_data.get('release_date', ''),
                        description=manifest_data.get('description', ''),
                        files=files,
                        min_version=manifest_data.get('min_version', ''),
                        changelog=manifest_data.get('changelog', [])
                    )
                    
                    logger.info(f"发现新版本: {manifest.version}, 共 {len(files)} 个文件需要更新")
                    self._update_progress(status=UpdateStatus.IDLE, message=f"发现新版本 {manifest.version}")
                    
                    return manifest
                    
        except asyncio.TimeoutError:
            logger.error("检查更新超时")
            self._update_progress(status=UpdateStatus.FAILED, error="检查更新超时")
            return None
        except Exception as e:
            logger.error(f"检查更新失败: {e}")
            self._update_progress(status=UpdateStatus.FAILED, error=str(e))
            return None
    
    async def get_files_to_update(self, manifest: UpdateManifest) -> List[FileUpdate]:
        """
        获取需要更新的文件列表（排除已是最新的文件）
        
        Args:
            manifest: 更新清单
            
        Returns:
            需要更新的文件列表
        """
        files_to_update = []
        
        for file_update in manifest.files:
            # 跳过被排除的文件
            if self._is_excluded(file_update.path):
                logger.debug(f"跳过排除的文件: {file_update.path}")
                continue
            
            local_path = self.app_dir / file_update.path
            
            # 如果服务端没有提供MD5，则始终更新该文件
            if not file_update.md5 or not file_update.md5.strip():
                files_to_update.append(file_update)
                logger.debug(f"需要更新（无MD5校验）: {file_update.path}")
                continue
            
            local_md5 = self._calculate_file_md5(local_path)
            
            # 如果本地文件不存在或MD5不匹配，则需要更新
            if local_md5 != file_update.md5:
                files_to_update.append(file_update)
                logger.debug(f"需要更新: {file_update.path} (本地MD5: {local_md5}, 远程MD5: {file_update.md5})")
            else:
                logger.debug(f"文件已是最新: {file_update.path}")
        
        return files_to_update
    
    # 非关键文件，MD5校验失败时可以继续更新（仅警告不报错）
    NON_CRITICAL_FILES = {'version.txt', 'update_log.txt', 'changelog.txt'}
    
    async def download_file(self, file_update: FileUpdate, session: aiohttp.ClientSession) -> Optional[bytes]:
        """
        下载单个文件
        
        Args:
            file_update: 文件更新信息
            session: aiohttp会话
            
        Returns:
            文件内容，失败返回None
        """
        try:
            async with session.get(file_update.download_url, timeout=aiohttp.ClientTimeout(total=60)) as response:
                if response.status != 200:
                    logger.error(f"下载文件失败: {file_update.path}, HTTP {response.status}")
                    return None
                
                content = await response.read()
                
                # 验证MD5（如果服务端提供了MD5值）
                if file_update.md5 and file_update.md5.strip():
                    downloaded_md5 = hashlib.md5(content).hexdigest()
                    if downloaded_md5 != file_update.md5:
                        # 检查是否为非关键文件
                        file_name = Path(file_update.path).name
                        if file_name in self.NON_CRITICAL_FILES:
                            logger.warning(f"非关键文件MD5不匹配（忽略）: {file_update.path}, 期望: {file_update.md5}, 实际: {downloaded_md5}")
                            # 非关键文件，继续更新
                        else:
                            logger.error(f"文件MD5校验失败: {file_update.path}, 期望: {file_update.md5}, 实际: {downloaded_md5}")
                            return None
                    else:
                        logger.debug(f"文件MD5校验通过: {file_update.path}")
                else:
                    logger.debug(f"跳过MD5校验（服务端未提供）: {file_update.path}")
                
                return content
                
        except Exception as e:
            logger.error(f"下载文件异常: {file_update.path}, {e}")
            return None
    
    def _backup_file(self, file_path: Path) -> bool:
        """
        备份文件
        
        Args:
            file_path: 要备份的文件路径
            
        Returns:
            是否成功
        """
        if not file_path.exists():
            return True
        
        try:
            relative_path = file_path.relative_to(self.app_dir)
            backup_path = self.backup_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}" / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            logger.debug(f"备份文件: {file_path} -> {backup_path}")
            return True
        except Exception as e:
            logger.error(f"备份文件失败: {file_path}, {e}")
            return False
    
    async def apply_updates(self, files_to_update: List[FileUpdate]) -> Tuple[bool, List[str], bool]:
        """
        应用更新
        
        Args:
            files_to_update: 需要更新的文件列表
            
        Returns:
            (是否成功, 更新的文件列表, 是否需要重启)
        """
        if not files_to_update:
            return True, [], False
        
        updated_files = []
        needs_restart = False
        total_size = sum(f.size for f in files_to_update)
        downloaded_size = 0
        
        self._update_progress(
            status=UpdateStatus.DOWNLOADING,
            total_files=len(files_to_update),
            total_bytes=total_size,
            message=f"正在下载 {len(files_to_update)} 个文件..."
        )
        
        async with aiohttp.ClientSession() as session:
            for index, file_update in enumerate(files_to_update):
                self._update_progress(
                    current_file=file_update.path,
                    current_index=index + 1,
                    message=f"正在下载: {file_update.path}"
                )
                
                # 下载文件
                content = await self.download_file(file_update, session)
                if content is None:
                    self._update_progress(
                        status=UpdateStatus.FAILED,
                        error=f"下载文件失败: {file_update.path}"
                    )
                    return False, updated_files, needs_restart
                
                downloaded_size += len(content)
                self._update_progress(downloaded_bytes=downloaded_size)
                
                # 备份并安装
                local_path = self.app_dir / file_update.path
                
                # 备份旧文件
                if not self._backup_file(local_path):
                    logger.warning(f"备份失败，继续更新: {file_update.path}")
                
                # 确保目录存在
                local_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 写入新文件
                try:
                    self._update_progress(
                        status=UpdateStatus.INSTALLING,
                        message=f"正在安装: {file_update.path}"
                    )
                    
                    with open(local_path, 'wb') as f:
                        f.write(content)
                    
                    updated_files.append(file_update.path)
                    
                    if file_update.requires_restart:
                        needs_restart = True
                    
                    logger.info(f"更新文件成功: {file_update.path}")
                    
                except Exception as e:
                    logger.error(f"写入文件失败: {file_update.path}, {e}")
                    self._update_progress(
                        status=UpdateStatus.FAILED,
                        error=f"安装文件失败: {file_update.path}"
                    )
                    return False, updated_files, needs_restart
        
        # 更新完成
        if needs_restart:
            self._update_progress(
                status=UpdateStatus.RESTART_REQUIRED,
                message=f"更新完成，共更新 {len(updated_files)} 个文件，需要重启应用"
            )
        else:
            self._update_progress(
                status=UpdateStatus.COMPLETED,
                message=f"更新完成，共更新 {len(updated_files)} 个文件"
            )
        
        return True, updated_files, needs_restart
    
    async def perform_update(self, manifest: Optional[UpdateManifest] = None) -> Dict[str, Any]:
        """
        执行完整的更新流程
        
        Args:
            manifest: 更新清单，如果为None则自动检查
            
        Returns:
            更新结果
        """
        result = {
            "success": False,
            "message": "",
            "updated_files": [],
            "needs_restart": False,
            "new_version": ""
        }
        
        try:
            # 检查更新
            if manifest is None:
                manifest = await self.check_for_updates()
            
            if manifest is None:
                result["message"] = "没有可用更新"
                result["success"] = True
                return result
            
            result["new_version"] = manifest.version
            
            # 获取需要更新的文件
            files_to_update = await self.get_files_to_update(manifest)
            
            if not files_to_update:
                result["message"] = "所有文件已是最新"
                result["success"] = True
                return result
            
            logger.info(f"开始更新 {len(files_to_update)} 个文件到版本 {manifest.version}")
            
            # 应用更新
            success, updated_files, needs_restart = await self.apply_updates(files_to_update)
            
            result["success"] = success
            result["updated_files"] = updated_files
            result["needs_restart"] = needs_restart
            
            if success:
                result["message"] = f"成功更新 {len(updated_files)} 个文件到版本 {manifest.version}"
                if needs_restart:
                    result["message"] += "，需要重启应用生效"
                
                # 更新成功后，保存文件哈希清单（用于以后对比）
                self.save_file_hashes(manifest.version, updated_files)
            else:
                result["message"] = "更新过程中出现错误"
            
            return result
            
        except Exception as e:
            logger.error(f"更新失败: {e}")
            result["message"] = f"更新失败: {str(e)}"
            self._update_progress(status=UpdateStatus.FAILED, error=str(e))
            return result
    
    def get_local_file_hashes(self, file_patterns: List[str] = None) -> Dict[str, str]:
        """
        获取本地文件的MD5哈希值
        
        Args:
            file_patterns: 文件模式列表，默认为常见的可更新文件
            
        Returns:
            {文件路径: MD5哈希}
        """
        if file_patterns is None:
            file_patterns = ['*.py', '*.js', '*.css', '*.html', '*.yml', '*.yaml', '*.json']
        
        file_hashes = {}
        
        for pattern in file_patterns:
            for file_path in self.app_dir.rglob(pattern):
                try:
                    relative_path = str(file_path.relative_to(self.app_dir)).replace('\\', '/')
                    
                    # 跳过排除的路径
                    if self._is_excluded(relative_path):
                        continue
                    
                    file_hashes[relative_path] = self._calculate_file_md5(file_path)
                except Exception as e:
                    logger.debug(f"计算文件哈希失败: {file_path}, {e}")
        
        return file_hashes
    
    def cleanup_old_backups(self, keep_days: int = 7):
        """
        清理旧的备份文件
        
        Args:
            keep_days: 保留天数
        """
        try:
            cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
            
            for backup_dir in self.backup_dir.iterdir():
                if backup_dir.is_dir():
                    if backup_dir.stat().st_mtime < cutoff_time:
                        shutil.rmtree(backup_dir)
                        logger.info(f"清理旧备份: {backup_dir}")
                        
        except Exception as e:
            logger.error(f"清理备份失败: {e}")
    
    def save_file_hashes(self, version: str, updated_files: List[str] = None):
        """
        保存文件哈希清单到本地
        
        更新完成后调用此方法，记录所有文件的MD5哈希值，
        方便以后对比哪些文件发生了变化。
        
        Args:
            version: 当前版本号
            updated_files: 本次更新的文件列表（可选）
        """
        try:
            hash_file = self.app_dir / "data" / "file_hashes.json"
            hash_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 获取所有可更新文件的哈希
            all_hashes = self.get_local_file_hashes()
            
            # 构建哈希清单
            manifest = {
                "version": version,
                "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "total_files": len(all_hashes),
                "files": all_hashes
            }
            
            # 如果有本次更新的文件列表，单独记录
            if updated_files:
                manifest["last_updated_files"] = updated_files
                manifest["last_updated_count"] = len(updated_files)
            
            # 保存到文件
            with open(hash_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)
            
            logger.info(f"已保存文件哈希清单: {hash_file}, 共 {len(all_hashes)} 个文件")
            
        except Exception as e:
            logger.error(f"保存文件哈希清单失败: {e}")
    
    def load_file_hashes(self) -> Optional[Dict[str, Any]]:
        """
        加载本地保存的文件哈希清单
        
        Returns:
            哈希清单字典，如果不存在则返回None
        """
        try:
            hash_file = self.app_dir / "data" / "file_hashes.json"
            
            if not hash_file.exists():
                return None
            
            with open(hash_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"加载文件哈希清单失败: {e}")
            return None
    
    def compare_file_hashes(self) -> Dict[str, Any]:
        """
        比较当前文件与保存的哈希清单
        
        Returns:
            比较结果，包含变化的文件列表
        """
        result = {
            "has_changes": False,
            "saved_version": None,
            "changed_files": [],
            "new_files": [],
            "deleted_files": [],
            "unchanged_files": []
        }
        
        try:
            saved_manifest = self.load_file_hashes()
            
            if saved_manifest is None:
                result["message"] = "没有保存的哈希清单，无法比较"
                return result
            
            result["saved_version"] = saved_manifest.get("version")
            saved_hashes = saved_manifest.get("files", {})
            
            # 获取当前文件哈希
            current_hashes = self.get_local_file_hashes()
            
            # 比较文件
            all_files = set(saved_hashes.keys()) | set(current_hashes.keys())
            
            for file_path in all_files:
                saved_md5 = saved_hashes.get(file_path)
                current_md5 = current_hashes.get(file_path)
                
                if saved_md5 is None:
                    # 新增的文件
                    result["new_files"].append(file_path)
                elif current_md5 is None:
                    # 删除的文件
                    result["deleted_files"].append(file_path)
                elif saved_md5 != current_md5:
                    # 修改的文件
                    result["changed_files"].append({
                        "path": file_path,
                        "old_md5": saved_md5,
                        "new_md5": current_md5
                    })
                else:
                    # 未变化的文件
                    result["unchanged_files"].append(file_path)
            
            result["has_changes"] = bool(result["changed_files"] or result["new_files"] or result["deleted_files"])
            result["message"] = f"比较完成: {len(result['changed_files'])} 个文件修改, {len(result['new_files'])} 个新增, {len(result['deleted_files'])} 个删除"
            
        except Exception as e:
            logger.error(f"比较文件哈希失败: {e}")
            result["message"] = f"比较失败: {str(e)}"
        
        return result


# 全局更新器实例
_updater: Optional[AutoUpdater] = None


def get_updater() -> AutoUpdater:
    """获取全局更新器实例"""
    global _updater
    if _updater is None:
        # 尝试从版本文件读取当前版本
        version = "1.0.0"
        try:
            version_file = Path(__file__).parent / "static" / "version.txt"
            if version_file.exists():
                version = version_file.read_text().strip()
        except:
            pass
        
        _updater = AutoUpdater(current_version=version)
    
    return _updater


def init_updater(app_dir: str = None, update_server: str = None, current_version: str = None) -> AutoUpdater:
    """
    初始化全局更新器
    
    Args:
        app_dir: 应用目录
        update_server: 更新服务器地址
        current_version: 当前版本号
    """
    global _updater
    
    if current_version is None:
        try:
            version_file = Path(app_dir or ".") / "static" / "version.txt"
            if version_file.exists():
                current_version = version_file.read_text().strip()
            else:
                current_version = "1.0.0"
        except:
            current_version = "1.0.0"
    
    _updater = AutoUpdater(
        app_dir=app_dir,
        update_server=update_server,
        current_version=current_version
    )
    
    return _updater

