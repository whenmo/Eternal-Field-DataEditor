from PyQt6.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QLayout
from PyQt6.QtCore import Qt, pyqtSignal
from scripts.global_set.card_db import Card
from scripts.basic_item.ui_item import new_frame, new_title


# id 輸入組件
def _new_id_line(placeholder: str, frame: QHBoxLayout) -> QLineEdit:
    le = QLineEdit()
    le.setPlaceholderText(placeholder)
    le.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    frame.addWidget(le)
    return le


# 清除空白，驗證並將數字字串轉換為整數 (無效時返回 0)
def _fix_code(text: str) -> int:
    text = text.strip()
    if not text or not text.isdigit():
        return 0
    return int(text)


# ID組件
class IDItem(QWidget):
    id: QLineEdit
    alias: QLineEdit
    find_id = pyqtSignal(str)

    def __init__(self, frame: QLayout):
        super().__init__()
        main_frame: QVBoxLayout = new_frame("V", self)
        new_title("卡片ID", main_frame)
        id_frame: QHBoxLayout = new_frame("H", main_frame)
        self.id = _new_id_line("ID", id_frame)
        self.id.returnPressed.connect(self._send_search_request)
        self.alias = _new_id_line("规则上当作ID", id_frame)

        frame.addWidget(self)

    # 發出信號搜索 ID 開頭的卡
    def _send_search_request(self):
        id = _fix_code(self.id.text())
        self.find_id.emit(str(id))

    # 根據 card 設定卡片ID
    def load_card(self, card: Card):
        id = card.id
        alias = card.alias if card.alias != 0 else ""
        self.id.setText(str(id))
        self.alias.setText(str(alias))

    # 清空當前內容
    def clear(self):
        self.id.setText("")
        self.alias.setText("")

    # 獲取 id 與 同名卡
    def get_code(self) -> tuple[int, int]:
        id = _fix_code(self.id.text())
        alias = _fix_code(self.alias.text())

        if id == alias and alias != 0:
            alias = 0

        return (id, alias)
