import os
from PyQt6.QtWidgets import QSizePolicy, QLabel, QLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import pyqtSignal, Qt
from scripts.global_set.app_set import PATH_COVER, SCALED_WIDTH, SCALED_HEIGHT


# 檢查路徑是否為存在的 .jpg 檔案
def _is_jpg_file(path: str) -> bool:
    return path.lower().endswith(".jpg") and os.path.exists(path)


# 根據路徑加載 QPixmap
def _new_pix_map(path: str) -> QPixmap | None:
    pixmap = QPixmap(path)
    if pixmap.isNull():
        return None
    return pixmap.scaled(
        SCALED_WIDTH,
        SCALED_HEIGHT,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


# 卡圖容器
class PicItem(QLabel):
    set_pic = pyqtSignal()

    def __init__(self, frame: QLayout):
        super().__init__()
        self.setFixedSize(SCALED_WIDTH, SCALED_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_path(PATH_COVER)

        frame.addWidget(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.set_pic.emit()
        super().mousePressEvent(event)

    # ---------- 調用事件 ----------
    def clear(self):
        self.set_path(PATH_COVER)

    def set_path(self, path: str):
        if not _is_jpg_file(path):
            path = PATH_COVER

        if (pixmap := _new_pix_map(path)) is not None:
            self.setPixmap(pixmap)
