import os
from typing import Callable
from PyQt6.QtWidgets import QToolBar, QWidget, QPushButton, QMenu, QToolButton
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from scripts.global_set.card_db import CDB


def new_toolbtn(
    title: str,
    toolbar: QToolBar,
    # style: Qt.ToolButtonStyle = Qt.ToolButtonStyle.ToolButtonTextOnly,
) -> QMenu:
    menu = QMenu()
    btn = QToolButton()
    btn.setText(title)
    # btn.setToolButtonStyle(style)
    btn.setMenu(menu)
    btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
    toolbar.addWidget(btn)
    return menu


def new_action(title: str, frame, menu: QMenu, func: Callable = None) -> QAction:
    act = QAction(title, frame)
    menu.addAction(act)
    if func:
        act.triggered.connect(func)
    return act


# 檔案分頁按鈕
class FileBtn(QWidget):
    style_select: str = "text-align: left; padding-left: 5px; background-color: rgb(180,200,255); color: black;"
    style_unselect: str = "text-align: left; padding-left: 5px;"
    fileBtn: QPushButton
    closeBtn: QPushButton
    closing = pyqtSignal(QWidget)

    def __init__(self, txt: str):
        super().__init__()
        # 檔案按鈕
        self.fileBtn = QPushButton(txt, self)
        self.fileBtn.setGeometry(0, 0, 100, 30)
        # X 按鈕
        self.closeBtn = QPushButton("X", self)
        self.closeBtn.setGeometry(75, 5, 20, 20)
        self.closeBtn.clicked.connect(self.close_self)

        self.setFixedSize(100, 30)

    # 點擊 x
    def close_self(self):
        self.closing.emit(self)

    # 將自己標為選中狀態（淺藍底、黑字）
    def select(self):
        self.fileBtn.setStyleSheet(self.style_select)
        self.closeBtn.setStyleSheet(self.style_select)

    # 恢復預設樣式。
    def deselect(self):
        self.fileBtn.setStyleSheet(self.style_unselect)
        self.closeBtn.setStyleSheet(self.style_unselect)


# 檔案分頁列表
class FileBtnToolBar(QToolBar):
    index: int = -1
    file_list: list[FileBtn]
    show_dataeditor = pyqtSignal(bool)
    load_cdb = pyqtSignal(CDB)

    def __init__(self):
        super().__init__("file_list")
        self.setFixedHeight(30)
        self.file_list = []

    # ---------------- 檔案讀取 ----------------
    def add_cdbfile(self, filepath: str):
        """根據傳入路徑新增一個 cdb 檔案分頁（若已存在則不新增）"""
        # 已存在相同路徑的分頁則指向該分頁
        for f in self.file_list:
            if isinstance(f, CdbFileBtn) and f.cdb.path == filepath:
                f.on_clicked()
                return

        if (cdb := CDB.create(filepath)) is None:
            return
        cdb_file = CdbFileBtn(cdb, self)
        cdb_file.click_cdbfile.connect(self.load_cdbfile)
        cdb_file.closing.connect(self.remove_file)
        # 更新狀態
        self.file_list.append(cdb_file)
        ind = len(self.file_list) - 1
        self.set_ind(ind)

    def load_cdbfile(self, cdbfilebtn: "CdbFileBtn"):
        ind = self.file_list.index(cdbfilebtn)
        self.set_ind(ind)
        self.load_cdb.emit(cdbfilebtn.cdb)

    # ---------------- 數據操作 ----------------
    def set_ind(self, ind: int):
        """設定 toolbar 的選中項（會處理樣式與 index 更新）"""
        if ind == self.index:
            return
        # 取消先前選中樣式
        if self.index != -1:
            self.file_list[self.index].deselect()
        # 設定新選中
        self.index = ind
        if self.index != -1:
            self.file_list[self.index].select()

    @pyqtSlot(QWidget)
    def remove_file(self, filebtn: FileBtn):
        """移除檔案分頁"""
        remove_ind = self.file_list.index(filebtn)
        old_ind = self.index

        del self.file_list[remove_ind]
        filebtn.deleteLater()
        if remove_ind == old_ind:
            if (flen := len(self.file_list)) > 0:
                new_ind = min(remove_ind, flen - 1)
                self.file_list[new_ind].on_clicked()
            else:
                self.index = -1
                self.show_dataeditor.emit(False)
        elif remove_ind < old_ind:
            self.index = old_ind - 1

    # ---------------- 獲取數據 ----------------
    def get_file_btn(self) -> "CdbFileBtn | None":
        """獲取當前指向的檔案按鈕"""
        if self.index == -1:
            return None
        return self.file_list[self.index]


# cdb 分頁按鈕
class CdbFileBtn(FileBtn):
    cdb: CDB
    click_cdbfile = pyqtSignal(FileBtn)

    def __init__(self, cdb: CDB, frame: QToolBar):
        super().__init__(os.path.basename(cdb.path))
        self.cdb = cdb
        self.fileBtn.clicked.connect(self.on_clicked)
        frame.addWidget(self)

    # ---------------- 按鈕事件 ----------------
    def on_clicked(self):
        self.click_cdbfile.emit(self)
