from PyQt6.QtWidgets import QSizePolicy, QWidget, QVBoxLayout, QLayout, QPlainTextEdit
from PyQt6.QtGui import QTextCursor, QColor, QPainter
from PyQt6.QtCore import Qt, QRect
from scripts.basic_item.ui_item import new_frame, new_title
from scripts.global_set.card_db import Card
from scripts.global_set.app_set import TEXT_HINTS_COUNT, DEFAULT_HINT


class HintSetLineArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)

    def paintEvent(self, event):
        painter = QPainter(self)
        top, offset = 4, 15
        for i in range(16):
            painter.drawText(
                0,
                top,
                self.width() - 1,
                15,
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                str(i),
            )
            top += offset

        # 分隔線
        painter.setPen(QColor(180, 180, 180))
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())


class HintSetTextArea(QPlainTextEdit):
    def __init__(self, frame: QVBoxLayout):
        super().__init__()
        # 延展
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # 禁止自動換行
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        # 禁用滾動條
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # 設定字體
        font = self.font()
        font.setFamily("Consolas")
        font.setPointSize(10)
        self.setFont(font)
        # 開始打字的位置
        self.setViewportMargins(17, 0, 0, 0)
        # 繪製行號欄
        cr = self.contentsRect()
        HintSetLineArea(self).setGeometry(QRect(cr.left(), cr.top(), 17, cr.height()))
        # 預設內容
        self.setPlainText(DEFAULT_HINT)
        frame.addWidget(self)


# 格式化 hint 內容並轉化為 list
def _fix_hint_text(text: str) -> list[str]:
    lines = text.splitlines()
    if len(lines) < TEXT_HINTS_COUNT:
        lines += [""] * (TEXT_HINTS_COUNT - len(lines))
    elif len(lines) > TEXT_HINTS_COUNT:
        lines = lines[:TEXT_HINTS_COUNT]
    return lines


# 脚本提示組件
class HintItem(QWidget):
    text: HintSetTextArea

    def __init__(self, frame: QLayout):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_frame: QVBoxLayout = new_frame("V", self)
        new_title("脚本提示文字", main_frame)
        # 脚本提示
        self.text = HintSetTextArea(main_frame)
        # 監聽文字變動
        self.text.textChanged.connect(self._on_text_changed)

        frame.addWidget(self)

    # ---------- 內部事件 ----------
    def _on_text_changed(self):
        cursor = self.text.textCursor()
        block_num = cursor.blockNumber()  # 行號
        col = cursor.positionInBlock()  # 列號

        txt = self.text.toPlainText()
        fix_txt = "\n".join(_fix_hint_text(txt))

        if fix_txt != txt:
            self.text.blockSignals(True)
            self.text.setPlainText(fix_txt)
            # 恢復光標到原行列
            new_cursor = self.text.textCursor()
            new_cursor.movePosition(QTextCursor.MoveOperation.Start)
            new_cursor.movePosition(
                QTextCursor.MoveOperation.Down,
                QTextCursor.MoveMode.MoveAnchor,
                block_num,
            )
            new_cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.MoveAnchor,
                col,
            )
            self.text.setTextCursor(new_cursor)
            self.text.blockSignals(False)

    # ---------- 調用事件 ----------
    def get_hints(self) -> list[str]:
        txt = self.text.toPlainText()
        return _fix_hint_text(txt)

    def clear(self):
        self.text.setPlainText(DEFAULT_HINT)

    def load_card(self, card: Card):
        self.text.setPlainText("\n".join(card.hints))
