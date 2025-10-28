from PyQt6.QtWidgets import QWidget, QLayout
from scripts.global_set.card_db import Card
from scripts.data_edit.id_item import IDItem
from scripts.data_edit.setcode_item import SetcodeItem
from scripts.data_edit.type_item import TypeItem
from scripts.data_edit.combobox_item import ComboboxItem
from scripts.data_edit.move_item import MoveItem
from scripts.basic_item.ui_item import new_title
from scripts.global_set.card_data_set import get_card_data
from scripts.global_set.app_set import TYPE_AREA


# 卡片資料組件
class CardDataItem(QWidget):
    code: IDItem
    setcode: SetcodeItem
    typ: TypeItem
    life: ComboboxItem
    atk: ComboboxItem
    cost: ComboboxItem
    from_: ComboboxItem
    race: ComboboxItem
    moveset: MoveItem

    def __init__(self, frame: QLayout):
        super().__init__()
        # card data
        card_data = get_card_data()
        # id & alias
        self.code = IDItem(frame)
        # 字段
        self.setcode = SetcodeItem(frame)
        # 卡片类型
        self.typ = TypeItem(frame)
        new_title("卡片细节", frame)
        # 生命
        self.life = ComboboxItem(card_data.get_combobox_data("life"), frame)
        # 費用 & 攻擊力 & 陣營 & 種族
        self.cost = ComboboxItem(card_data.get_combobox_data("cost"), frame)
        self.atk = ComboboxItem(card_data.get_combobox_data("atk"), frame)
        self.from_ = ComboboxItem(card_data.get_combobox_data("from"), frame)
        self.race = ComboboxItem(card_data.get_combobox_data("race"), frame)
        # 移動箭頭
        self.moveset = MoveItem(frame)

    # ---------------- 設定數據 ----------------
    # 讀取卡片並更新卡片資料
    def load_card(self, card: Card):
        self.code.load_card(card)
        self.setcode.load_card(card)
        self.typ.load_card(card)
        life, cost = 0, card.value
        if card.is_type(TYPE_AREA):
            life, cost = cost, life
        self.life.set_value(f"{life}")
        self.cost.set_value(f"{cost}")
        self.atk.set_value(f"{card.atk}")
        self.race.set_value(f"0x{card.race:X}")
        self.from_.set_value(f"0x{card.from_:X}")
        self.moveset.load_card(card)

    # 清空當前內容
    def clear(self):
        self.code.clear()
        self.setcode.clear()
        self.typ.clear()
        self.life.clear()
        self.cost.clear()
        self.atk.clear()
        self.race.clear()
        self.from_.clear()
        self.moveset.clear()

    # ---------------- 獲取數據 ----------------
    # code
    def get_code(self) -> tuple[int, int]:
        id, alias = self.code.get_code()
        return (id, alias)

    # data list [ setcode, type, value, atk, move, race, from ]
    def get_data_list(self) -> list[int]:
        res_lst = [self.setcode.get_setcode()]
        typ = self.typ.get_type()
        res_lst.append(typ)
        if typ & TYPE_AREA:
            value = self.life.get_data()
        else:
            value = self.cost.get_data()
        res_lst.append(value)
        res_lst.append(self.atk.get_data())
        res_lst.append(self.moveset.get_move())
        res_lst.append(self.race.get_data())
        res_lst.append(self.from_.get_data())
        return res_lst
