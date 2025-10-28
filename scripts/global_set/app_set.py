import os
import sys

# ---------------- 基礎設置 ----------------
APP_ID: str = "Eternal_Field_DataEditor"
VER: str = "1.1"
WRITEER: str = "whenmo"
GIT_URL: str = "https://github.com/whenmo/Eternal-Field-DataEditor"
APP_SIZE: tuple[int, int] = (850, 650)


# ---------------- 路徑常數 ----------------
def _get_base_dir() -> str:
    """計算應用程式的基礎目錄，適用於打包 (frozen) 或原始執行"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    # 位於 global_set
    global_dir = os.path.dirname(os.path.abspath(__file__))
    script_dir = os.path.dirname(global_dir)
    return os.path.dirname(script_dir)


BASE_DIR: str = _get_base_dir()
PATH_CARD_DATA: str = os.path.join(BASE_DIR, "data", "card_data.json")
PATH_CONFIG: str = os.path.join(BASE_DIR, "data", "config.json")
PATH_COVER: str = os.path.join(BASE_DIR, "data", "cover.jpg")
PATH_ICON: str = os.path.join(BASE_DIR, "data", "app_icon.png")

# ---------------- 資料庫 ----------------
SQL_DATA_COLUMNS: str = "alias,setcode,type,value,atk,move,race,[from]"
SQL_TEXT_COLUMNS: str = "name,desc,str1,str2,str3,str4,str5,str6,str7,str8,str9,str10,str11,str12,str13,str14,str15,str16"
TEXT_HINTS_COUNT: int = 16
DEFAULT_HINT = "\n" * (TEXT_HINTS_COUNT - 1)


def get_sql_code_data() -> tuple[str, str]:
    """生成 'datas' 表格的 CREATE 和 INSERT 語句"""
    keys_list = SQL_DATA_COLUMNS.split(",")
    key_type_list = [f"{key} INTEGER" for key in keys_list]
    column_str = ",\n        ".join(key_type_list)
    set_code = f"""
        CREATE TABLE IF NOT EXISTS datas (
            id INTEGER PRIMARY KEY,
            {column_str}
        )
        """
    key_ct = len(keys_list) + 1
    insert_str = ",".join(["?"] * key_ct)
    insert_code = f"INSERT INTO datas VALUES ({insert_str})"
    return (set_code, insert_code)


def get_sql_code_text() -> tuple[str, str]:
    """生成 'texts' 表格的 CREATE 和 INSERT 語句"""
    keys_list = SQL_TEXT_COLUMNS.split(",")
    key_type_list = [f"{key} TEXT" for key in keys_list]
    column_str = ",\n        ".join(key_type_list)
    set_code = f"""
        CREATE TABLE IF NOT EXISTS texts (
            id INTEGER PRIMARY KEY,
            {column_str}
        )
        """
    key_ct = len(keys_list) + 1
    insert_str = ",".join(["?"] * key_ct)
    insert_code = f"INSERT INTO texts VALUES ({insert_str})"
    return (set_code, insert_code)


# ---------------- 類型常數 ----------------
TYPE_MONS: int = 0x1
TYPE_AREA: int = 0x8
TYPE_MAIN: int = 0xF
TYPE_SUB: int = 0xFFF0
DICT_VAL_TO_TYP: dict[int, str] = {
    0x1: "monstyp",
    0x2: "calltyp",
    0x4: "banetyp",
    0x8: "areatyp",
}
# ---------------- 圖片常數 ----------------
SCALED_WIDTH = 200
SCALED_HEIGHT = 285

# ---------------- 腳本提示常數 ----------------
DEFAULT_HINT = "\n" * (TEXT_HINTS_COUNT - 1)
