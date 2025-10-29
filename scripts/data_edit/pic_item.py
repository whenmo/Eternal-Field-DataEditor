import os
from PyQt6.QtWidgets import QSizePolicy, QLabel, QLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import pyqtSignal, Qt
from scripts.global_set.app_set import (
    SCALED_WIDTH,
    SCALED_HEIGHT,
    PATH_COVER,
    COVER_CODE,
)


# 根據路徑加載 QPixmap
def _new_pix_map(path: str) -> QPixmap | None:
    # 檢查路徑是否為存在的 .jpg 檔案
    if not (path.lower().endswith(".jpg") and os.path.exists(path)):
        return None
    pixmap = QPixmap(path)
    if pixmap.isNull():
        return None
    return pixmap.scaled(
        SCALED_WIDTH,
        SCALED_HEIGHT,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


# 獲取預設的 cover QPixmap
def _get_default_cover() -> QPixmap | None:
    if (pixmap := _new_pix_map(PATH_COVER)) is not None:
        return pixmap
    pixmap = QPixmap()
    if pixmap.loadFromData(COVER_CODE, "PNG"):
        return pixmap.scaled(
            SCALED_WIDTH,
            SCALED_HEIGHT,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
    return None


# 卡圖容器
class PicItem(QLabel):
    set_pic = pyqtSignal()
    default_cover: QPixmap | None

    def __init__(self, frame: QLayout):
        super().__init__()
        self.setFixedSize(SCALED_WIDTH, SCALED_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.default_cover = _get_default_cover()
        self.setPixmap(self.default_cover)

        frame.addWidget(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.set_pic.emit()
        super().mousePressEvent(event)

    # ---------- 調用事件 ----------
    def clear(self):
        self.set_path("")

    def set_path(self, path: str):
        if (pixmap := _new_pix_map(path)) is not None:
            self.setPixmap(pixmap)
            return
        self.setPixmap(self.default_cover)
