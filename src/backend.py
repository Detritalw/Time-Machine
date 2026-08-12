"""Time Machine Backend — QObject bridge for QML"""
import os, json, time, threading, datetime
from PySide6.QtCore import QObject, Signal, Slot, Property

from modules.backup import (
    backup_folder_raw, calc_folder_size, calc_folder_num,
    get_last_backup_time, get_backup_times, backup_files, del_backup_files,
)
from modules.log import log
from modules.systems import setup_startup_with_self_starting


class Backend(QObject):
    """Exposes all Time Machine backend logic as Qt properties/slots for QML."""

    # Signals
    backupStarted = Signal()
    backupFinished = Signal()
    backupError = Signal(str)
    lastBackupTimeChanged = Signal()
    backupSizeChanged = Signal()
    backupNumChanged = Signal()
    restoreFilesChanged = Signal()
    configChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
        self._config = {}
        self._load_config()

    # ─── config ───────────────────────────────────────────────
    def _config_abspath(self, p):
        if p and p != "/blank":
            return os.path.abspath(os.path.expandvars(os.path.expanduser(p)))
        return "/blank"

    def _load_config(self):
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                self._config = json.load(f)
        except Exception:
            self._config = {"ver": "1.1", "backup-folder": {"from": "/blank", "to": "/blank"},
                            "backup_at_run": False, "auto_backup_time": 600, "self-starting": False}
        log(f"配置已加载")

    def _save_config(self):
        try:
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            log(f"保存配置失败: {e}", 40)

    # ─── properties ───────────────────────────────────────────

    @Property(str, notify=lastBackupTimeChanged)
    def lastBackupTime(self):
        to_folder = self._config.get("backup-folder", {}).get("to", "/blank")
        ts = get_last_backup_time(to_folder)
        if ts == "无备份记录":
            return "无备份记录"
        try:
            dt = datetime.datetime.fromtimestamp(float(ts))
            return dt.strftime("%Y年%m月%d日 %H:%M:%S")
        except Exception:
            return ts

    @Property(str, notify=backupSizeChanged)
    def backupSize(self):
        to_folder = self._config.get("backup-folder", {}).get("to", "/blank")
        size_bytes = calc_folder_size(to_folder)
        for unit in [" B", " KB", " MB", " GB", " TB"]:
            if size_bytes < 1024:
                break
            size_bytes /= 1024
        return f"{size_bytes:.2f} {unit}"

    @Property(str, notify=backupNumChanged)
    def backupNum(self):
        to_folder = self._config.get("backup-folder", {}).get("to", "/blank")
        return f"{calc_folder_num(to_folder)} 次"

    @Property(str, notify=configChanged)
    def fromFolder(self):
        return self._config.get("backup-folder", {}).get("from", "/blank")

    @Property(str, notify=configChanged)
    def toFolder(self):
        return self._config.get("backup-folder", {}).get("to", "/blank")

    @Property(int, notify=configChanged)
    def autoBackupTime(self):
        return self._config.get("auto_backup_time", 600)

    @Property(bool, notify=configChanged)
    def backupAtRun(self):
        return self._config.get("backup_at_run", False)

    @Property(bool, notify=configChanged)
    def selfStarting(self):
        return self._config.get("self-starting", False)

    @Property(str, notify=configChanged)
    def version(self):
        return self._config.get("ver", "1.1")

    # ─── backup time list ─────────────────────────────────────

    @Property("QVariantList", notify=restoreFilesChanged)
    def backupTimeList(self):
        to_folder = self._config.get("backup-folder", {}).get("to", "/blank")
        timestamps = get_backup_times(to_folder)
        result = []
        for ts in timestamps:
            try:
                dt = datetime.datetime.fromtimestamp(float(ts))
                label = dt.strftime("%Y年%m月%d日 %H:%M:%S")
            except Exception:
                label = ts
            result.append({"timestamp": ts, "label": label})
        return result

    # ─── restore file list for a given timestamp ──────────────

    @Slot(str, result="QVariantList")
    def getRestoreFiles(self, timestamp_str):
        to_folder = self._config.get("backup-folder", {}).get("to", "/blank")
        config_path = os.path.join(to_folder, "config.json")
        result = []
        if not os.path.exists(config_path):
            return result
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                time_config = json.load(f)
        except Exception:
            return result

        times_data = time_config.get("times", {})
        selected = times_data.get(timestamp_str, {})
        files_data = selected.get("times", {})

        def flatten_tree(tree, prefix=""):
            items = []
            for name, info in tree.items():
                full = (prefix + "/" + name) if prefix else name
                ts_val = str(info.get("time", ""))
                ftype = info.get("type", "file")
                child_items = []
                if ftype == "folder" and info.get("child"):
                    child_items = flatten_tree(info["child"], full)
                items.append({
                    "name": name,
                    "fullPath": full,
                    "timestamp": ts_val,
                    "type": ftype,
                    "child": child_items,
                })
            return items

        result = flatten_tree(files_data)
        return result

    # ─── slots ────────────────────────────────────────────────

    @Slot()
    def startBackup(self):
        self.backupStarted.emit()
        to_folder = self._config.get("backup-folder", {}).get("to", "/blank")
        from_folder = self._config.get("backup-folder", {}).get("from", "/blank")
        if from_folder == "/blank" or to_folder == "/blank":
            self.backupError.emit("请先设置备份源文件夹和目标文件夹")
            return

        try:
            backup_folder_raw(self._config)
            self.backupFinished.emit()
            self.lastBackupTimeChanged.emit()
            self.backupSizeChanged.emit()
            self.backupNumChanged.emit()
            self.restoreFilesChanged.emit()
        except Exception as e:
            log(f"备份失败: {e}", 40)
            self.backupError.emit(f"备份失败: {e}")

    @Slot(str, str)
    def restoreFile(self, file_path, timestamp_str):
        try:
            backup_files(file_path, timestamp_str)
            log(f"已恢复文件: {file_path}")
        except Exception as e:
            log(f"恢复文件失败: {e}", 40)
            raise

    @Slot(str, str)
    def deleteBackupFile(self, file_path, timestamp_str):
        try:
            del_backup_files(file_path, timestamp_str)
            log(f"已删除备份文件: {file_path}")
        except Exception as e:
            log(f"删除备份文件失败: {e}", 40)
            raise

    @Slot(str)
    def setFromFolder(self, folder):
        self._config.setdefault("backup-folder", {})["from"] = folder
        self._save_config()
        self.configChanged.emit()

    @Slot(str)
    def setToFolder(self, folder):
        self._config.setdefault("backup-folder", {})["to"] = folder
        self._save_config()
        self.configChanged.emit()

    @Slot(int)
    def setAutoBackupTime(self, value):
        self._config["auto_backup_time"] = value
        self._save_config()
        self.configChanged.emit()

    @Slot(bool)
    def setBackupAtRun(self, value):
        self._config["backup_at_run"] = value
        self._save_config()
        self.configChanged.emit()

    @Slot(bool)
    def setSelfStarting(self, value):
        self._config["self-starting"] = value
        self._save_config()
        try:
            setup_startup_with_self_starting(value)
        except Exception as e:
            log(f"设置开机自启失败: {e}", 40)
        self.configChanged.emit()

    # ─── refresh all UI state ─────────────────────────────────

    @Slot()
    def refreshAll(self):
        self._load_config()
        self.lastBackupTimeChanged.emit()
        self.backupSizeChanged.emit()
        self.backupNumChanged.emit()
        self.restoreFilesChanged.emit()
        self.configChanged.emit()
