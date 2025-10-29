import os
import json
from scripts.global_set.app_set import PATH_CONFIG

_CONFIG_INSTANCE: dict | None = None
_DEFAULT_CONFIG = {
    "DATABASE_HISTORY": {"max_record": 10, "history_paths": []},
    "LUA_DEFAULT": "--{} {}\\nlocal cm, m = GetID()\\nfunction cm.initial_effect(c)\\n\\nend\\n",
    "HIDE_ILLEGAL": 1,
}


class ConfigSet:
    _data: dict[str, any]

    def __init__(self, data: dict[str, any]):
        self._data = data

    # ---------------- 保存 ----------------
    def save(self):
        """將當前配置儲存到配置檔"""
        try:
            os.makedirs(os.path.dirname(PATH_CONFIG), exist_ok=True)
            with open(PATH_CONFIG, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    # ---------------- 歷史 ----------------
    def clear_database_hist(self):
        """清空歷史路徑列表"""
        self._data["DATABASE_HISTORY"]["history_paths"] = []
        self.save()

    def add_database_hist(self, path: str):
        """更新歷史路徑列表"""
        hist_set = self._data.get("DATABASE_HISTORY", {})
        hist_lst: list = hist_set.get("history_paths", [])
        max_record = hist_set.get("max_record", 10)

        if path in hist_lst:
            hist_lst.remove(path)

        hist_lst.insert(0, path)
        hist_lst = hist_lst[:max_record]

        hist_set["history_paths"] = hist_lst
        self._data["DATABASE_HISTORY"] = hist_set

        self.save()

    def get_hist_list(self) -> list[str]:
        """獲取歷史路徑列表"""
        return self._data["DATABASE_HISTORY"]["history_paths"]

    # ---------------- 默認 lua ----------------
    def get_default_lua(self) -> str:
        """獲取默認 lua"""
        return self._data["LUA_DEFAULT"]

    # ---------------- 自动隐藏不合法组件 ----------------
    def get_hide_illegal(self) -> bool:
        """是否 自动隐藏不合法组件"""
        return self._data["HIDE_ILLEGAL"] == 1

    def set_hide_illegal(self, b: bool):
        """設定 自动隐藏不合法组件"""
        val = 1 if b else 0
        self._data["HIDE_ILLEGAL"] = val
        self.save()


# 獲取 cardinfo.txt
def get_config() -> ConfigSet:
    """載入配置檔, 如果不存在或載入失敗則建立預設配置"""
    global _CONFIG_INSTANCE
    if _CONFIG_INSTANCE is not None:
        return _CONFIG_INSTANCE
    if not os.path.exists(PATH_CONFIG):
        _CONFIG_INSTANCE = ConfigSet(_DEFAULT_CONFIG)
        return _CONFIG_INSTANCE
    try:
        with open(PATH_CONFIG, "r", encoding="utf-8") as f:
            config = json.load(f)
            _CONFIG_INSTANCE = ConfigSet(config)
            return _CONFIG_INSTANCE
    except Exception:
        _CONFIG_INSTANCE = ConfigSet(_DEFAULT_CONFIG)
        return _CONFIG_INSTANCE
