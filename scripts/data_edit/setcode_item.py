import re
from typing import Final
from contextlib import contextmanager
from PyQt6.QtWidgets import (
    QSizePolicy,
    QWidget,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QLayout,
    QPushButton,
    QApplication,
)
from PyQt6.QtCore import Qt
from scripts.global_set.card_db import Card
from scripts.global_set.card_data_set import get_card_data
from scripts.basic_item.ui_item import new_frame, new_title
from scripts.basic_item.icon_line_item import IconLineItem

VALID_SETCODE: Final[str] = r"^[0-9A-F]{1,4}$"
INFO_CODE: list[str] = ["0", "FFFF"]


# 將單個字串 格式化 為標準的 1-4 位大寫 16 進制字串, 無 0X, 用於顯示於 IconLineItem
def _fix_code_to_show(code: str) -> str:
    res = code.upper()
    if res.startswith("0X"):
        res = res[2:]
    if not re.fullmatch(VALID_SETCODE, res):
        res = "0"
    return res


# 檢查當前字串的狀態
def _get_code_type(code: str) -> bool:
    if not code:
        return "info"
    code = code.upper()
    if code.startswith("0X"):
        code = code[2:]
    if code in INFO_CODE:
        return "info"
    if bool(re.fullmatch(VALID_SETCODE, code)):
        return "ok"
    return "err"


# 將combobox data 格式化 為標準的 1-4 位大寫 16 進制字串, 無 0X
def _fix_combobox_data(code: str | None) -> str:
    if code is None or code == "-1":
        return "FFFF"
    return code[2:].upper()


# 字段組件
class SetcodeItem(QWidget):
    comb_list: list[QComboBox]
    line_list: list[IconLineItem]
    _show_default: str = False
    _updating: bool = False
    _data_ind_dic: dict[str, int]

    def __init__(self, frame: QLayout):
        super().__init__()
        self.comb_list = []
        self.line_list = []
        self._data_ind_dic = {}

        default, setcode_list = get_card_data().get_setcode_data()
        self._show_default = _fix_code_to_show(default)

        main_fram: QVBoxLayout = new_frame("V", self)
        new_title("卡片字段", main_fram)
        for _ in range(4):
            self._create_setcode_row(main_fram, setcode_list)

        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        frame.addWidget(self)

    # ---------------- 內部事件 ----------------
    def _create_setcode_row(self, frame: QLayout, setcode_list: list[tuple[str, str]]):
        map_is_empty = not self._data_ind_dic
        row_frame: QHBoxLayout = new_frame("H", frame)
        # 左側 combobox 初始化
        set_cb = QComboBox()
        row_frame.addWidget(set_cb)
        for i, (name, value) in enumerate(setcode_list):
            set_cb.addItem(name, value)
            if map_is_empty:
                self._data_ind_dic[value] = i
        # 中央 LineEdit
        set_le = IconLineItem(self._show_default, "", row_frame)
        set_le.txt.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        set_le.txt.setFixedWidth(80)  # 固定寬度
        set_le.set_icon_tip(
            "应为 code or 0xcode or 0Xcode\ncode为不检查大小写的最多 4 位的 16 进制数字",
            "格式正确\n点击左侧按钮即可复制全大写的 0Xcode",
            "格式错误\n应为 code or 0xcode or 0Xcode\ncode为不检查大小写的最多 4 位的 16 进制数字",
        )
        # 右側 copy buttom
        copy_btn = QPushButton("复制")
        copy_btn.setFixedWidth(50)
        row_frame.addWidget(copy_btn)
        # 綁定事件
        set_cb.currentIndexChanged.connect(
            lambda idx, le=set_le, cb=set_cb: self._comb_change(cb, le)
        )
        set_le.txt.textChanged.connect(
            lambda text, le=set_le, cb=set_cb: self._line_change(le, cb)
        )
        copy_btn.clicked.connect(lambda chk, le=set_le: self._copy_value(le))
        self.comb_list.append(set_cb)
        self.line_list.append(set_le)

    # 獲取字段值對應的 combobox 索引與標準化十六進制字串 (無 0X
    def _trans_code(self, code: str) -> tuple[int, str]:
        fix_code = _fix_code_to_show(code)
        # 沒有則為 -1 (自定義
        target_data_hex = "0X" + fix_code
        ind = self._data_ind_dic.get(target_data_hex, -1)
        if ind == -1:
            ind = self._data_ind_dic.get("-1", -1)
        return (ind, fix_code)

    @contextmanager
    def _updating_block(self):
        self._updating = True
        try:
            yield
        finally:
            self._updating = False

    def _comb_change(self, combobox: QComboBox, icle: IconLineItem):
        if self._updating:
            return
        with self._updating_block():
            txt: str = _fix_combobox_data(combobox.currentData())
            icle.set_text(txt)
            icle.set_icon(_get_code_type(txt))

    def _line_change(self, icle: IconLineItem, combobox: QComboBox):
        if self._updating:
            return
        with self._updating_block():
            txt = icle.get_text()
            icle.set_icon(_get_code_type(txt))
            ind, _ = self._trans_code(txt)
            combobox.setCurrentIndex(ind)

    def _copy_value(self, icle: IconLineItem):
        res = "0X" + _fix_code_to_show(icle.get_text())
        QApplication.clipboard().setText(res)

    # ---------------- 設定數據 ----------------
    def clear(self):
        with self._updating_block():
            for i in range(4):
                ind, txt = self._trans_code(self._show_default)
                self.comb_list[i].setCurrentIndex(ind)
                self.line_list[i].set_text(txt)
                self.line_list[i].set_icon(_get_code_type(txt))

    # 根據 card 設定卡片字段
    def load_card(self, card: Card):
        setcode = card.setcode
        with self._updating_block():
            for i in range(4):
                code = f"{setcode & 0xFFFF:X}"
                ind, txt = self._trans_code(code)
                self.comb_list[i].setCurrentIndex(ind)
                self.line_list[i].set_text(txt)
                self.line_list[i].set_icon(_get_code_type(txt))

    # ---------------- 獲取數據 ----------------
    def get_setcode(self) -> int:
        res = 0
        for i, icle in enumerate(self.line_list):
            fix_code = _fix_code_to_show(icle.get_text())
            res += int(fix_code, 16) << (i * 16)
        return res
