import os
import json
from scripts.global_set.app_set import PATH_CARD_DATA

_CARD_DATA_MAP_INSTANCE: "CardDataSet | None" = None


class CardDataSet:
    _data: dict[str, any]

    def __init__(self, data: dict[str, any]):
        self._data: dict[str, any] = {}

        for key, data_dict in data.items():
            if key == "typ" or key == "setcode":
                self._data[key] = data_dict
                continue
            fix_dict = {
                "display": data_dict.get("display", ""),
                "default": data_dict.get("default", ""),
                "mapping": {},  # 統一的映射字典
            }
            if "mapping" in data_dict:  # 對於 from, race
                fix_dict["mapping"] = data_dict["mapping"]
            elif "range" in data_dict:  # 對於 life, atk, cost
                min, max = 0, 0
                # range_key 為 min, max, 或是 顯示的 str, range_val 為實際值
                for range_key, range_val in data_dict["range"].items():
                    if range_key == "min":
                        min = int(range_val)
                    elif range_key == "max":
                        max = int(range_val)
                    else:
                        fix_dict["mapping"][range_val] = range_key

                for i in range(min, max + 1):
                    i_str = str(i)
                    fix_dict["mapping"][i_str] = i_str

            self._data[key] = fix_dict

    def get_typ_data(self) -> tuple[str, dict[str, dict]]:
        """
        傳回 (default, mapping)\n
        default : typ 的 str "monstyp"\n
        mapping : typ 的 str 為 key, typ_dict 為 val 的 dict\n
        typ_dict : display 顯示的 str\n
        typ_dict : default 實際值的 str\n
        typ_dict : options 實際值的 str 為 key, 顯示的 str 為 val 的 dict
        """
        typ_dic = self._data.get("typ", {})
        return (typ_dic["default"], typ_dic["mapping"])

    def get_setcode_data(self) -> tuple[str, list[tuple[str, str]]]:
        """
        傳回 (default, setcode_list)\n
        default : 實際值的 str\n
        setcode_list : (顯示的 str, 大寫的實際值的 str)
        """
        setcode_dic = self._data.get("setcode", {})
        setcode_list = []
        for value, name in setcode_dic["mapping"].items():
            setcode_list.append((name, value.upper()))
        return (setcode_dic["default"], setcode_list)

    def get_combobox_data(self, key: str) -> tuple[str, dict[str, str], str]:
        """
        獲取用於 combobox 的信息 (life, cost, atk, from, race)\n
        返回: (title, mapping, default)\n
        mapping : 實際值的 str 為 key, 顯示的 str 為 val 的 dict\n
        default : 實際值的 str
        """
        data = self._data.get(key, {})
        title = data.get("display", "")
        mapping = data.get("mapping", {})
        default = data.get("default", "")

        return (title, mapping, default)


# 獲取 cardinfo.txt
def get_card_data() -> CardDataSet | None:
    global _CARD_DATA_MAP_INSTANCE
    if _CARD_DATA_MAP_INSTANCE is not None:
        return _CARD_DATA_MAP_INSTANCE
    if not os.path.exists(PATH_CARD_DATA):
        print(f"錯誤：找不到卡片資訊檔案: {PATH_CARD_DATA}")
        return None
    try:
        with open(PATH_CARD_DATA, "r", encoding="utf-8") as f:
            data = json.load(f)
            _CARD_DATA_MAP_INSTANCE = CardDataSet(data)
            return _CARD_DATA_MAP_INSTANCE
    except json.JSONDecodeError as e:
        print(f"錯誤：解析 JSON 檔案 {PATH_CARD_DATA} 失敗。錯誤訊息: {e}")
        return None
    except Exception as e:
        print(f"讀取檔案時發生意外錯誤: {e}")
        return None
