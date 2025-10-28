from scripts.global_set.card_db import Card
from PyQt6.QtWidgets import (
    QSizePolicy,
    QLabel,
    QWidget,
    QHBoxLayout,
    QCheckBox,
    QLayout,
)
from PyQt6.QtCore import Qt
from scripts.basic_item.ui_item import new_panel, new_frame


# 移動標組件
class MoveItem(QWidget):
    checkboxes: list[QCheckBox]

    def __init__(self, frame: QLayout):
        super().__init__()
        main_frame: QHBoxLayout = new_frame("H", self)
        # 左側 Label
        lab = QLabel("移动方向")
        lab.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        main_frame.addWidget(lab)
        # 右側 GridLayout
        grid_panel, grid_frame = new_panel("G", 2)

        self.checkboxes = []
        positions = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)]
        for _, pos in enumerate(positions):
            cb = QCheckBox()
            self.checkboxes.append(cb)
            grid_frame.addWidget(cb, pos[0], pos[1])

        main_frame.addWidget(grid_panel)
        grid_panel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        frame.addWidget(self)

    def get_move(self) -> int:
        value = 0
        for i, cb in enumerate(self.checkboxes):
            if cb.isChecked():
                value |= 1 << i
        return value

    def clear(self):
        for _, cb in enumerate(self.checkboxes):
            cb.setChecked(False)

    # 讀取卡片並更新卡片資料
    def load_card(self, card: Card):
        move = card.move
        for i, cb in enumerate(self.checkboxes):
            cb.setChecked((move & (1 << i)) != 0)
