from PyQt6.QtWidgets import QWidget, QComboBox, QVBoxLayout, QHBoxLayout, QLayout
from PyQt6.QtCore import pyqtSignal
from scripts.global_set.card_db import Card
from scripts.global_set.card_data_set import get_card_data
from scripts.global_set.app_set import TYPE_MAIN, DICT_VAL_TO_TYP
from scripts.basic_item.ui_item import new_frame, new_title


def _new_combobox(frame: QHBoxLayout) -> QComboBox:
    combobox = QComboBox()
    frame.addWidget(combobox)
    return combobox


def _set_combobox(
    combobox: QComboBox, default_data: str, data_show_dict: dict[str, str]
):
    for data, show in data_show_dict.items():
        combobox.addItem(show, data)

    index = combobox.findData(default_data)
    if index != -1:
        combobox.setCurrentIndex(index)


# 卡片类型組件
class TypeItem(QWidget):
    main: QComboBox
    sub: QComboBox
    _main_data_default: str
    _main_data_now: str
    _sub_data: dict[str, tuple[str, dict[str, str]]]
    typ_change = pyqtSignal(int)

    def __init__(self, frame: QLayout):
        super().__init__()
        # 數據處理
        self._main_data_default, mapping = get_card_data().get_typ_data()
        self._main_data_now = self._main_data_default
        self._sub_data = {}
        main_data_show_dict = {}
        for typ_str, typ_dict in mapping.items():
            display = typ_dict.get("display", typ_str)
            sub_default_data = typ_dict.get("default", "")
            sub_data_show_dict = typ_dict.get("options", {})

            main_data_show_dict[typ_str] = display
            self._sub_data[typ_str] = (sub_default_data, sub_data_show_dict)

        # GUI
        main_frame: QVBoxLayout = new_frame("V", self)
        new_title("卡片类型", main_frame)
        typ_frame: QHBoxLayout = new_frame("H", main_frame)
        # 左側 (子) 类型 QComboBox
        self.sub = _new_combobox(typ_frame)
        sub_default_data, sub_data_show_dict = self._sub_data[self._main_data_now]
        _set_combobox(self.sub, sub_default_data, sub_data_show_dict)
        # 右側 (主) 类型 QComboBox
        self.main = _new_combobox(typ_frame)
        _set_combobox(self.main, self._main_data_now, main_data_show_dict)
        self.main.currentIndexChanged.connect(self._main_combobox_change)

        frame.addWidget(self)

    # ---------- 內部事件 ----------
    def _reset_sub_combobox(self, main_data: str):
        sub_default, sub_options = self._sub_data[main_data]
        self.sub.clear()
        _set_combobox(self.sub, sub_default, sub_options)
        self.typ_change.emit(int(sub_default, 16))

    def _main_combobox_change(self):
        main_data = self.main.currentData()
        if main_data == self._main_data_now:
            return
        self._main_data_now = main_data
        self._reset_sub_combobox(main_data)

    # ---------- 調用事件 ----------
    def clear(self):
        self.main.setCurrentIndex(self.main.findData(self._main_data_default))
        self._reset_sub_combobox(self._main_data_default)

    # 根據 card 設定卡片ID
    def load_card(self, card: Card):
        typ = card.type
        main_data = DICT_VAL_TO_TYP[typ & TYPE_MAIN]
        self.main.setCurrentIndex(self.main.findData(main_data))
        typ_str = f"0x{typ:X}"
        self.sub.setCurrentIndex(self.sub.findData(typ_str))

    def get_type(self) -> int:
        return int(self.sub.currentData(), 16)
