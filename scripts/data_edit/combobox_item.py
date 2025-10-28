from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout, QComboBox, QLayout
from PyQt6.QtCore import Qt
from scripts.basic_item.ui_item import new_frame


# 下拉框組件
class ComboboxItem(QWidget):
    default: str
    combobox: QComboBox

    def __init__(self, info: tuple[str, dict[str, str], str], frame: QLayout):
        super().__init__()
        title, data_show_dict, self.default = info

        main_frame: QHBoxLayout = new_frame("H", self)

        # 左側 Label
        lab: QLabel = QLabel(title)
        lab.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        main_frame.addWidget(lab)

        # 右側 combobox
        self.combobox = QComboBox()
        main_frame.addWidget(self.combobox)
        for data, show in data_show_dict.items():
            self.combobox.addItem(show, data)
        index = self.combobox.findData(self.default)
        if index != -1:
            self.combobox.setCurrentIndex(index)

        # 讓 LineEdit 拉伸填滿剩餘空間
        main_frame.setStretch(0, 0)  # label 不拉伸
        main_frame.setStretch(1, 1)  # lineedit 拉伸

        frame.addWidget(self)

    def get_data(self) -> int:
        data = self.combobox.currentData()
        return int(data, 0)

    def set_value(self, value: str):
        index = self.combobox.findData(value)
        if index != -1:
            self.combobox.setCurrentIndex(index)

    def clear(self):
        self.set_value(self.default)
