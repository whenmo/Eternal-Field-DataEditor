from PyQt6.QtWidgets import QWidget, QLineEdit, QLayout, QPlainTextEdit
from PyQt6.QtCore import Qt, pyqtSignal
from scripts.global_set.card_db import Card
from scripts.global_set.app_set import TYPE_MONS
from scripts.basic_item.ui_item import new_frame
from scripts.data_edit.pic_item import PicItem
from scripts.data_edit.hint_item import HintItem


# 卡片文本組件
class CardTextItem(QWidget):
    name: QLineEdit
    pic: PicItem
    hint: HintItem
    desc: QPlainTextEdit
    gene_desc: QPlainTextEdit
    find_name = pyqtSignal(str)

    def __init__(self, frame: QLayout):
        super().__init__()
        # 卡名
        self.name = QLineEdit()
        self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name.returnPressed.connect(self._send_find_request)
        frame.addWidget(self.name)
        # 卡圖 & 脚本提示文字
        mid_frame = new_frame("H", frame)
        self.pic = PicItem(mid_frame)
        self.hint = HintItem(mid_frame)
        # 卡片描述
        self.desc = QPlainTextEdit()
        self.desc.setPlaceholderText("卡片描述")
        frame.addWidget(self.desc)
        # 進化元效果
        self.gene_desc = QPlainTextEdit()
        self.gene_desc.setPlaceholderText("进化元效果")
        font_metrics = self.gene_desc.fontMetrics()
        line_height = font_metrics.lineSpacing()  # 每行行高（含間距）
        self.gene_desc.setFixedHeight(line_height * 5 + 8)  # 顯示約5行，+8留邊距
        frame.addWidget(self.gene_desc)

    # ---------------- 內部事件 ----------------
    # 搜索 name 開頭的卡
    def _send_find_request(self):
        name = self.name.text()
        self.find_name.emit(name)

    # ---------------- 設定數據 ----------------
    # 讀取卡片並更新卡片文本
    def load_card(self, card: Card):
        self.name.setText(card.name)
        self.hint.load_card(card)

        desc = card.desc
        is_mons = card.is_type(TYPE_MONS)
        if is_mons:
            gene_desc = ""
            desc_lst = desc.splitlines()
            for i, line in enumerate(desc_lst):
                if line.startswith("【进化元效果】"):
                    desc = "\n".join(desc_lst[:i])
                    gene_desc = "\n".join(desc_lst[i + 1 :])
                    break
            self.gene_desc.setPlainText(gene_desc)

        self.desc.setPlainText(desc)
        self.gene_desc.setVisible(is_mons)

    # 清空當前內容
    def clear(self):
        self.name.setText("")
        self.pic.clear()
        self.hint.clear()
        self.desc.setPlainText("")
        self.gene_desc.setPlainText("")

    # ---------------- 獲取數據 ----------------
    # text list : [name, desc, str1 ~16]
    def get_text_list(self, is_mons: bool) -> list[str]:
        res_lst = [self.name.text()]
        desc = self.desc.toPlainText()
        if is_mons and (gene := self.gene_desc.toPlainText()):
            desc += "\n【进化元效果】\n" + gene
        res_lst.append(desc)
        res_lst += self.hint.get_hints()

        return res_lst
