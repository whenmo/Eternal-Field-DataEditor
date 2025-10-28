from PyQt6.QtWidgets import (
    QLabel,
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QApplication,
)
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtCore import Qt, pyqtSignal
from scripts.global_set.card_db import CDB
from scripts.basic_item.ui_item import new_frame, new_btn


class CardTable(QTableWidget):
    def __init__(self, frame: QVBoxLayout):
        super().__init__()
        self._press_on_empty = False
        self._press_index = None

        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["ID", "Name"])
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setDefaultAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.setColumnWidth(0, 80)
        self.horizontalHeader().setStretchLastSection(True)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # 禁編輯
        self.setSelectionMode(QTableWidget.SelectionMode.NoSelection)  # 禁選中
        self.setDragDropMode(QTableWidget.DragDropMode.NoDragDrop)  # 禁拖放
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setDragEnabled(False)
        self.setAcceptDrops(False)
        self.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: transparent;
                color: black;
            }
        """)
        frame.addWidget(self)

    def mousePressEvent(self, event):
        idx = self.indexAt(
            event.position().toPoint() if hasattr(event, "position") else event.pos()
        )
        if not idx.isValid():
            # 點在空白處：記錄並吞掉事件（不傳給父類以避免啟動選取/拖曳）
            self._press_on_empty = True
            self._press_index = None
            # 立即清除任何存在的選取（避免殘留高亮）
            self.clearSelection()
            return
        # 點在項目上：記錄索引，保留不啟動拖曳的行為，但允許產生 click
        self._press_on_empty = False
        self._press_index = idx
        # 仍然呼叫父類以確保 click 相關的內部狀態（但我們會在 move 時忽略拖曳）
        super().mousePressEvent(event)

    # 如果按住的是空白處或是從項目開始，忽略移動事件以避免高亮/選取改變
    def mouseMoveEvent(self, event):
        if self._press_on_empty or self._press_index is not None:
            return
        super().mouseMoveEvent(event)

    # 如果是從空白處開始按住，釋放時重置狀態並吞掉事件
    def mouseReleaseEvent(self, event):
        if self._press_on_empty:
            self._press_on_empty = False
            self._press_index = None
            return
        # 如果是從項目上按下（即使期間有移動），在放開時強制發出 itemClicked 以模擬 click
        if self._press_index is not None:
            row = self._press_index.row()
            col = self._press_index.column()
            item = self.item(row, col)
            if item is not None:
                # 手動發出信號（保持行為一致）
                try:
                    self.itemClicked.emit(item)
                except Exception:
                    pass
            # 重置狀態，並且不要呼叫父類以避免造成選取/高亮
            self._press_index = None
            return
        super().mouseReleaseEvent(event)


# 卡片列表組件
class CardListItem(QWidget):
    card_lst: CardTable
    page_text: QLineEdit
    page_label: QLabel
    refresh_edit = pyqtSignal()
    # 卡片列表屬性
    cdb: CDB | None = None
    id_to_row: dict[int, int]
    # 前後頁屬性
    rows_per_page: int = 10
    now_page: int = 1
    total_page: int = 1

    def __init__(self, frame: QHBoxLayout):
        super().__init__()
        self.id_to_row = {}
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        main_frame = new_frame("V", self)
        # 卡片列表
        self.card_lst = CardTable(main_frame)
        self.card_lst.itemClicked.connect(self.on_item_clicked)
        # 按鈕控制區
        page_frame: QHBoxLayout = new_frame("H", main_frame)
        page_frame.addStretch()
        new_btn("上一頁", page_frame, self.prev_page)
        self.page_text = QLineEdit("1")
        self.page_text.setStyleSheet("font-size: 12px;")
        self.page_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_text.returnPressed.connect(self.goto_page)
        page_frame.addWidget(self.page_text)
        self.page_label = QLabel("/ 1")
        self.page_label.setStyleSheet("font-size: 12px;")
        page_frame.addWidget(self.page_label)
        new_btn("下一頁", page_frame, self.next_page)
        page_frame.addStretch()

        frame.addWidget(self)

    # ---------------- UI 事件處理 ----------------
    def showEvent(self, event):
        super().showEvent(event)
        self.calc_rows_per_page()
        self.refresh_view()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.refresh_view()

    # 處理上下鍵移動 now_ind 到前一個/下一個
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Up:
            self._move_index(-1)
            return
        elif key == Qt.Key.Key_Down:
            self._move_index(1)
            return
        super().keyPressEvent(event)

    # ---------------- 分頁邏輯 ----------------
    # 上一頁
    def prev_page(self):
        if self.now_page > 1:
            self.now_page -= 1
            self.refresh_view()

    # 下一頁
    def next_page(self):
        if self.now_page < self.total_page:
            self.now_page += 1
            self.refresh_view()

    # 跳轉到指定頁
    def goto_page(self):
        try:
            page = int(self.page_text.text())
        except ValueError:
            page = self.now_page
        if 1 <= page <= self.total_page:
            self.now_page = page
            self.refresh_view()
        else:
            self.page_text.setText(str(self.now_page))

    def calc_rows_per_page(self):
        # 顯示欄數 = 卡片列表 widget 高度 / 單行高度
        show_row = self.card_lst.viewport().height() // 30
        self.rows_per_page = max(1, show_row)

    # ---------------- 顯示 ----------------
    def refresh_view(self):
        """根據當前的 cdb 和過濾列表刷新 QTableWidget 的內容"""
        self.card_lst.setRowCount(0)
        keys = self.cdb.show_id_lst if self.cdb else []
        self.calc_rows_per_page()
        self.total_page = max(
            1, (len(keys) + self.rows_per_page - 1) // self.rows_per_page
        )
        # 頁碼校正
        if self.now_page > self.total_page:
            self.now_page = self.total_page
        # 更新 page_text 與 page_label
        self.page_text.setText(str(self.now_page))
        self.page_label.setText(f"/ {self.total_page}")
        # 計算當前頁的索引範圍
        st_ind = (self.now_page - 1) * self.rows_per_page
        ed_ind = min(st_ind + self.rows_per_page, len(keys))
        self.card_lst.setRowCount(ed_ind - st_ind)
        self.id_to_row.clear()
        # 填充表格
        for row, key_idx in enumerate(range(st_ind, ed_ind)):
            card_id = keys[key_idx]
            card = self.cdb.card_dict[card_id]
            self.id_to_row[int(card.id)] = row
            is_selected = card_id in self.cdb.select_id_lst
            for col, txt in enumerate([str(card.id), card.name]):
                item = QTableWidgetItem(txt)
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                )
                if is_selected:  # 使用淺藍色作為選中高亮
                    item.setBackground(QColor(180, 200, 255))
                    item.setForeground(QColor(0, 0, 0))
                else:  # 重置為預設背景
                    item.setBackground(QBrush())
                    item.setForeground(QBrush())
                self.card_lst.setItem(row, col, item)

    # 點擊時事件
    def on_item_clicked(self, item: QTableWidgetItem):
        row = item.row()
        id_item = self.card_lst.item(row, 0)
        clicked_id = int(id_item.text())
        modifiers = QApplication.keyboardModifiers()
        # ------------------ 處理 Shift 範圍選擇 ------------------
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            pre_id = self.cdb.now_id
            keys = self.cdb.show_id_lst
            if keys and pre_id != 0:
                try:
                    ind_st = keys.index(pre_id)
                    ind_ed = keys.index(clicked_id)
                except ValueError:  # 如果 ID 不在當前列表
                    ind_st, ind_ed = -1, -1
                if ind_st != -1:
                    range_st = min(ind_st, ind_ed)
                    range_ed = max(ind_st, ind_ed)
                    self.cdb.select_id_lst.clear()
                    for i in range(range_st, range_ed + 1):
                        self.cdb.select_id_lst.add(keys[i])
        # ------------------ 處理 Ctrl 選擇 ------------------
        elif modifiers & Qt.KeyboardModifier.ControlModifier:
            if clicked_id in self.cdb.select_id_lst:
                if len(self.cdb.select_id_lst) > 1:
                    self.cdb.select_id_lst.remove(clicked_id)
            else:
                self.cdb.select_id_lst.add(clicked_id)
        # ------------------ 單擊 ------------------
        else:
            self.cdb.select_id_lst.clear()
            self.cdb.select_id_lst.add(clicked_id)

        self.cdb.now_id = clicked_id
        self.refresh_view()
        self.refresh_edit.emit()

    def _move_index(self, delta: int):
        """根據目前 self.cdb.show_id_lst 的順序移動 now_ind 並觸發 on_item_clicked"""
        if not (keys := self.cdb.show_id_lst):
            return
        try:
            cur_idx = keys.index(self.cdb.now_id)
        except ValueError:  # 若沒有選擇，從 -1 開始
            cur_idx = -1
        new_idx = cur_idx + delta
        if new_idx < 0 or new_idx >= len(keys):
            return  # 超出範圍則不動作
        new_page = (new_idx // self.rows_per_page) + 1
        # 目標行在當前頁，直接觸發 on_item_clicked
        if new_page == self.now_page:
            cur_row = new_idx % self.rows_per_page
        else:
            self.now_page = new_page
            self.refresh_view()
            if delta == 1:
                cur_row = 0
            else:
                cur_row = self.card_lst.rowCount() - 1

        self.on_item_clicked(self.card_lst.item(cur_row, 0))
        self.setFocus()

    # ---------------- 數據操作 ----------------
    # 清除所有過濾條件
    def clear_filter(self):
        all_ids = sorted(self.cdb.card_dict.keys(), key=lambda k: int(k))
        self.cdb.show_id_lst = all_ids
        if self.cdb.now_id not in self.cdb.show_id_lst and self.cdb.show_id_lst:
            self.cdb.now_id = self.cdb.show_id_lst[0]
        try:
            now_idx = self.cdb.show_id_lst.index(self.cdb.now_id)
            self.current_page = (now_idx // self.rows_per_page) + 1
        except ValueError:
            self.current_page = 1
        self.refresh_view()

    # 搜索 id
    def search_id(self, id: str):
        self.cdb.search_id(id)
        self.now_page = 1
        self.refresh_view()

    # 搜索 name
    def search_name(self, name: str):
        self.cdb.search_name(name)
        self.now_page = 1
        self.refresh_view()

    def set_data_source(self, cdb: CDB):
        """設定卡片資料庫 (CDB) 並初始化卡片索引和過濾列表"""
        self.cdb = cdb
        try:
            now_idx = self.cdb.show_id_lst.index(self.cdb.now_id)
            self.now_page = (now_idx // self.rows_per_page) + 1
        except (ValueError, AttributeError):
            self.now_page = 1
        self.refresh_view()

    # cdb 更新時校正
    def on_cdb_change(self):
        try:
            now_idx = self.cdb.show_id_lst.index(self.cdb.now_id)
            self.current_page = (now_idx // self.rows_per_page) + 1
        except ValueError:
            self.current_page = 1

        self.refresh_view()
        self.refresh_edit.emit()
