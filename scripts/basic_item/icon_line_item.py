from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QSizePolicy,
    QApplication,
    QStyle,
    QLayout,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap
from scripts.basic_item.ui_item import new_frame

DEFAULT_ICON_TYPE: str = "info"
ICON_TIP_INDEX: dict[str, int] = {"info": 0, "ok": 1, "err": 2}
ICON_DICT: dict[str, QStyle.StandardPixmap] = {
    "info": QStyle.StandardPixmap.SP_MessageBoxInformation,
    "ok": QStyle.StandardPixmap.SP_DialogApplyButton,
    "err": QStyle.StandardPixmap.SP_MessageBoxCritical,
}


# icon 組件
def _new_icon(frame: QWidget, fix_typ: str) -> QPixmap:
    style = QApplication.style()
    pixmap = style.standardPixmap(ICON_DICT[fix_typ], option=None, widget=frame).scaled(
        QSize(16, 16),
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    return pixmap


# 檢查並格式化 typ
def _fix_typ(typ: str) -> str:
    if typ not in ICON_DICT:
        typ = DEFAULT_ICON_TYPE
    return typ


class LineIcon(QLabel):
    typ: str
    tips: list[str]

    def __init__(self, frame: QHBoxLayout):
        super().__init__()
        # 當前 icon
        self.typ = DEFAULT_ICON_TYPE
        # 默認 tooltip
        self.tips = ["", "", ""]
        self.setToolTip("")
        # 樣式
        style = QApplication.style()
        icon_pixmap = style.standardPixmap(
            ICON_DICT[DEFAULT_ICON_TYPE], None, self
        ).scaled(
            QSize(16, 16),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.setPixmap(icon_pixmap)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        frame.addWidget(self)

    def _get_tip(self) -> int:
        return self.tips[ICON_TIP_INDEX[self.typ]]

    def set_tips(self, info_tip: str, ok_tip: str, err_tip: str):
        self.tips = [info_tip, ok_tip, err_tip]
        self.setToolTip(self._get_tip())

    def set_typ(self, typ: str):
        fix_typ = _fix_typ(typ)
        if self.typ != fix_typ:
            self.typ = fix_typ
            icon = _new_icon(self, fix_typ)
            self.setPixmap(icon)
            self.setToolTip(self._get_tip())


class LineEdit(QLineEdit):
    def __init__(self, default: str, hint: str, frame: QHBoxLayout):
        super().__init__(default)
        self.setPlaceholderText(hint)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        frame.addWidget(self)


class IconLineItem(QWidget):
    icon: LineIcon
    line: LineEdit

    def __init__(self, default: str, hint: str, frame: QLayout):
        super().__init__()
        main_fram: QHBoxLayout = new_frame("H", self)
        self.icon = LineIcon(main_fram)
        self.line = LineEdit(default, hint, main_fram)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        frame.addWidget(self)

    def set_icon_tips(self, info_tip: str, ok_tip: str, err_tip: str):
        self.icon.set_tips(info_tip, ok_tip, err_tip)

    def set_icon_typ(self, typ: str):
        self.icon.set_typ(typ)

    def set_text(self, txt: str):
        self.line.setText(txt)

    def get_text(self) -> str:
        return self.line.text()


"""
class IconLineItem(QWidget):
    icon: QLabel
    icon_tip: list[str]
    txt: QLineEdit

    _now_icon_typ: str

    def __init__(self, default: str, hint: str, frame: QLayout):
        super().__init__()
        main_frame: QHBoxLayout = new_frame("H", self)

        # 創建一個帶有 info 圖標的 label
        self.icon = QLabel()
        style = QApplication.style()
        icon_pixmap = style.standardPixmap(
            ICON_DICT[DEFAULT_ICON_TYPE], None, self
        ).scaled(
            QSize(16, 16),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.icon.setPixmap(icon_pixmap)
        self.icon.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # 默認 tooltip
        self.icon_tip = ["", "", ""]
        self.icon.setToolTip("")

        # 當前 icon
        self._now_icon_typ = DEFAULT_ICON_TYPE

        # 創建 QLineEdit
        self.txt = QLineEdit(default)
        self.txt.setPlaceholderText(hint)

        main_frame.addWidget(self.icon)
        main_frame.addWidget(self.txt)

        self.setSizePolicy(
            self.txt.sizePolicy().horizontalPolicy(),
            self.txt.sizePolicy().verticalPolicy(),
        )

        frame.addWidget(self)

    def _get_tip(self) -> int:
        typ = self._now_icon_typ
        ind = ICON_TIP_INDEX[typ]
        return self.icon_tip[ind]

    def set_icon_tips(self, info_tip: str, ok_tip: str, err_tip: str):
        self.icon_tip = [info_tip, ok_tip, err_tip]
        self.icon.setToolTip(self._get_tip())

    def set_icon_typ(self, typ: str):
        fix_typ = _fix_typ(typ)
        if fix_typ != self._now_icon_typ:
            self._now_icon_typ = fix_typ
            icon = _new_icon(self, fix_typ)
            self.icon.setPixmap(icon)
            self.icon.setToolTip(self._get_tip())

    def set_text(self, txt: str):
        self.txt.setText(txt)

    def get_text(self) -> str:
        return self.txt.text()
"""
