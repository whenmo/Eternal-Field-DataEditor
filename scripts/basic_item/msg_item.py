import logging
from PyQt6.QtWidgets import QMessageBox, QWidget


# 詢問組件
def quest(msg: str, frame: QWidget | None = None) -> bool:
    yes = QMessageBox.StandardButton.Yes
    no = QMessageBox.StandardButton.No
    return yes == QMessageBox.question(frame, "询问", msg, yes | no)


# 錯誤組件
def error(msg: str, frame: QWidget | None = None):
    logging.warning(msg)
    QMessageBox.warning(frame, "错误", msg)


# 提示組件
def msg(msg: str, frame: QWidget | None = None):
    QMessageBox.information(frame, "提示", msg)
