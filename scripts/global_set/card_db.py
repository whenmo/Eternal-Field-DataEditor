import sqlite3
import os
from scripts.global_set.app_set import (
    get_sql_code_data,
    get_sql_code_text,
    TEXT_HINTS_COUNT,
)
import scripts.basic_item.msg_item as show

sql_set_datas, sql_insert_datas = get_sql_code_data()
sql_set_texts, sql_insert_texts = get_sql_code_text()


# 建立新的 CDB 資料庫檔案, 包含 datas 與 texts 兩個表
def create_database_file(file_path: str):
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()
    cursor.execute(sql_set_datas)
    cursor.execute(sql_set_texts)
    conn.commit()
    conn.close()


class Card:
    id: int
    alias: int = 0
    setcode: int = 0
    type: int = 0
    value: int = 0
    atk: int = 0
    move: int = 0
    race: int = 0
    from_: int = 0
    name: str = ""
    desc: str = ""
    hints: list[str]

    def __init__(self, id: int):
        self.id = id
        self.hints = []

    # ---------------- sql 相關 ----------------
    def get_data_row(self) -> tuple:
        return (
            self.id,
            self.alias,
            self.setcode,
            self.type,
            self.value,
            self.atk,
            self.move,
            self.race,
            self.from_,
        )

    def get_text_row(self) -> tuple:
        hints = self.hints
        if len(hints) < TEXT_HINTS_COUNT:
            hints += [""] * (TEXT_HINTS_COUNT - len(hints))
        else:
            hints = hints[:TEXT_HINTS_COUNT]
        return (self.id, self.name, self.desc, *hints)

    def load_sql_data(self, data_row: list[int]):
        self.alias = data_row[1]
        self.setcode = data_row[2]
        self.type = data_row[3]
        self.value = data_row[4]
        self.atk = data_row[5]
        self.move = data_row[6]
        self.race = data_row[7]
        self.from_ = data_row[8]

    def load_edit_data(self, alias: int, data_lst: list[int]):
        self.alias = alias
        self.setcode = data_lst[0]
        self.type = data_lst[1]
        self.value = data_lst[2]
        self.atk = data_lst[3]
        self.move = data_lst[4]
        self.race = data_lst[5]
        self.from_ = data_lst[6]

    def load_sql_text(self, text_row: list[str]):
        self.name = text_row[1]
        self.desc = text_row[2]
        self.hints = text_row[3:]

    def load_edit_text(self, text_lst: list[str]):
        self.name = text_lst[0]
        self.desc = text_lst[1]
        self.hints = text_lst[2:]

    # ---------------- 類型檢查 ----------------
    def is_type(self, typ: int) -> bool:
        return bool(self.type & typ)


class CDB:
    path: str
    pic_dir: str
    script_dir: str
    card_dict: dict[int, Card]
    now_id: int = 0
    show_id_lst: list[int]
    select_id_lst: set[int]

    def __init__(self, path: str):
        self.path = path
        cdb_dir = os.path.dirname(self.path)
        self.pic_dir = os.path.join(cdb_dir, "pics")
        self.script_dir = os.path.join(cdb_dir, "script")
        self.card_dict = {}
        self.show_id_lst = []
        self.select_id_lst = set()

    # ---------------- 檢查路徑並創建 ----------------
    @classmethod
    def create(cls, path: str) -> "CDB | None":
        """檢查 CDB 路徑並創建, 不合法或載入失敗則返回 None"""
        if not (
            path
            and isinstance(path, str)
            and os.path.exists(path)
            and path.lower().endswith(".cdb")
        ):
            show.error(f"路徑無效\n{path}")
            return None

        try:
            instance = cls(path)
            with sqlite3.connect(instance.path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('datas', 'texts')"
                )
                tables = {row[0] for row in cursor.fetchall()}
                if "datas" not in tables or "texts" not in tables:
                    show.error(f"CDB 文件結構不匹配\n{path}")
                    return None
                cursor.execute("SELECT * FROM datas")
                datas = cursor.fetchall()
                cursor.execute("SELECT * FROM texts")
                texts = cursor.fetchall()
                for data, text in zip(datas, texts):
                    card = Card(data[0])
                    card.load_sql_data(data)
                    card.load_sql_text(text)
                    instance.card_dict[data[0]] = card
        except Exception as e:
            show.error(f"CDB 載入時發生錯誤\n{path}\n{e}")
            return None
        if instance.card_dict:
            instance.show_id_lst = sorted(
                instance.card_dict.keys(), key=lambda k: int(k)
            )
            instance.now_id = instance.show_id_lst[0]
            instance.select_id_lst.add(instance.now_id)
        return instance

    # ---------------- 設定數據 ----------------
    def add_card(self, c: Card) -> bool:
        """增加一張卡"""
        if self.has_id(c.id) and not show.quest(f"{c.id} 已存在, 是否覆盖"):
            return False
        self.save_card(c)
        return True

    def save_card(self, c: Card):
        """保存一張卡"""
        self.card_dict[c.id] = c
        self.save()
        self.show_id_lst = sorted(self.card_dict.keys(), key=lambda k: int(k))
        self.now_id = c.id
        self.select_id_lst.clear()
        self.select_id_lst.add(self.now_id)

    def del_id(self, id: int):
        """刪除 id 的卡並保存"""
        if show.quest(f"是否刪除\n{id}"):
            del self.card_dict[id]
            self.save()

    def save(self):
        """將 cdb 保存到 path"""
        try:
            with sqlite3.connect(self.path) as conn:
                cur = conn.cursor()
                cur.execute(sql_set_datas)
                cur.execute(sql_set_texts)
                cur.execute("DELETE FROM datas")
                cur.execute("DELETE FROM texts")
                sorted_cards = sorted(self.card_dict.values(), key=lambda card: card.id)
                for card in sorted_cards:
                    cur.execute(sql_insert_datas, card.get_data_row())
                    cur.execute(sql_insert_texts, card.get_text_row())
                conn.commit()
        except Exception as e:
            show.error(f"CDB 保存時發生錯誤\n{self.path}\n{e}")

    # ---------------- 獲取數據 ----------------
    def get_first_id(self) -> int:
        """獲取第一張卡的 id"""
        if not self.card_dict:
            return 0
        return next(iter(self.card_dict))

    def get_now_card(self) -> Card | None:
        """回傳當前指向的 id 的 Card, 無卡回傳 None"""
        return self.get_card(self.now_id)

    def get_card(self, id: int) -> Card | None:
        """回傳指定 id 的 Card, 找不到對應 id 回傳 None"""
        return self.card_dict.get(id)

    def has_id(self, id: int) -> bool:
        """檢查是否存在 id"""
        return id in self.card_dict

    def search_id(self, id_prefix: str):
        """
        根據 id 篩選卡片, 如果為空則顯示所有卡片, 同時清空已選中的卡
        不會回傳值, 只會更新內部的 now_id, show_id_lst 和 select_id_lst
        """
        if id_prefix and id_prefix != "0":
            match_id_lst = [
                id for id in self.card_dict.keys() if str(id).startswith(id_prefix)
            ]
            self.show_id_lst = match_id_lst
        else:
            self.show_id_lst = sorted(self.card_dict.keys(), key=lambda k: int(k))

        if self.now_id in self.show_id_lst:
            pass
        elif self.show_id_lst:
            self.now_id = self.show_id_lst[0]
        else:
            self.now_id = 0
        self.select_id_lst.clear()
        self.select_id_lst.add(self.now_id)

    def search_name(self, name: str):
        """
        根據 name 篩選卡片, 如果為空則顯示所有卡片, 同時清空已選中的卡
        不會回傳值, 只會更新內部的 now_id, show_id_lst 和 select_id_lst
        """
        if name:
            name_lower = name.lower()  # 進行不區分大小寫的匹配
            match_id_lst = [
                key
                for key, card in self.card_dict.items()
                if card.name and name_lower in card.name.lower()
            ]
            self.show_id_lst = match_id_lst
        else:
            self.show_id_lst = sorted(self.card_dict.keys(), key=lambda k: int(k))

        if self.now_id in self.show_id_lst:
            pass
        elif self.show_id_lst:
            self.now_id = self.show_id_lst[0]
        else:
            self.now_id = 0
        self.select_id_lst.clear()
        self.select_id_lst.add(self.now_id)

    def del_select_card(self) -> bool:
        """刪除 self.select_id_lst 中選中的所有卡片, 然後更新 now_id, show_id_lst 和 select_id_lst"""
        if not self.select_id_lst:
            return

        msg = "是否刪除\n" + "\n".join([str(id) for id in self.select_id_lst])
        if not show.quest(msg):
            return False

        del_id_lst = self.select_id_lst.copy()
        for id in del_id_lst:
            del self.card_dict[id]

        self.save()

        self.show_id_lst = [id for id in self.show_id_lst if id not in del_id_lst]
        self.select_id_lst.clear()

        if self.show_id_lst:
            new_now_id = self.show_id_lst[0]
            self.select_id_lst.add(new_now_id)
        else:
            new_now_id = 0
        self.now_id = new_now_id
        return True

    def get_pic_dir(self) -> str:
        return self.pic_dir

    def get_script_dir(self) -> str:
        return self.script_dir
