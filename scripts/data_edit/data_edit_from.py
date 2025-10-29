import os
import subprocess
import platform
import shutil
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
from scripts.global_set.app_set import TYPE_MONS, TYPE_AREA
from scripts.global_set.card_db import CDB, Card
from scripts.global_set.config_set import get_config
from scripts.basic_item.ui_item import new_frame, new_btn
import scripts.basic_item.msg_item as show
from scripts.data_edit.card_list_item import CardListItem
from scripts.data_edit.card_data_item import CardDataItem
from scripts.data_edit.card_text_item import CardTextItem


class DataEditFrom(QWidget):
    card_list: CardListItem
    card_data: CardDataItem
    card_text: CardTextItem
    copy_card: dict[int, Card]
    update_past_txt = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setVisible(False)  # 初始隱藏
        self.copy_card = {}
        main_frame: QHBoxLayout = new_frame("H", self, None, False)
        # 卡片列表
        self.card_list = CardListItem(main_frame)
        # ---------------- 中央容器 ----------------
        mid_frame: QVBoxLayout = new_frame("V", main_frame)
        # 卡片文本編輯區
        self.card_text = CardTextItem(mid_frame)
        # 搜索 & 重置 & 脚本 按鈕
        btn_frame: QHBoxLayout = new_frame("H", mid_frame)
        btn_frame.addStretch()
        new_btn("重置列表", btn_frame, self.card_list.clear_filter)
        new_btn("脚本", btn_frame, self.open_script)
        new_btn("重置资料", btn_frame, self.clear_edit)
        btn_frame.addStretch()
        # ---------------- 右側容器 ----------------
        right_frame: QVBoxLayout = new_frame("V", main_frame)
        right_frame.setAlignment(Qt.AlignmentFlag.AlignTop)  # 所有子組件靠上對齊
        # 卡片數據編輯區
        self.card_data = CardDataItem(right_frame)
        right_frame.addStretch()
        # 添加 & 修改 & 删除 按鈕
        btn_frame: QHBoxLayout = new_frame("H", right_frame)
        btn_frame.addStretch()
        new_btn("添加", btn_frame, self.add_card)
        new_btn("保存 (Ctrl + S)", btn_frame, self.save_card)
        new_btn(
            "删除",
            btn_frame,
            self.delete_card,
            "background-color: #d9534f; color: black;",
        )
        shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        shortcut.activated.connect(self.save_card)
        btn_frame.addStretch()
        # ---------------- 信號接收 ----------------
        self.card_list.refresh_edit.connect(self.refresh_edit)
        self.card_data.code.find_id.connect(self.find_id)
        self.card_data.typ.typ_change.connect(self.hide_illegal)
        self.card_text.find_name.connect(self.find_name)
        self.card_text.pic.set_pic.connect(self.set_pic)

    # ---------------- 信號事件 ----------------
    # 搜索 ID 開頭的卡
    def find_id(self, id: str):
        self.card_list.search_id(id)
        self.refresh_edit()

    # 搜索 name 開頭的卡
    def find_name(self, name: str):
        self.card_list.search_name(name)
        self.refresh_edit()

    # 隱藏不合法項
    def hide_illegal(self, typ: int):
        show_illegal = not get_config().get_hide_illegal()
        is_area = bool(typ & TYPE_AREA)
        self.card_data.life.setVisible(is_area or show_illegal)
        self.card_data.cost.setVisible(not is_area or show_illegal)
        show_mons = bool(typ & TYPE_MONS) or show_illegal
        self.card_text.gene_desc.setVisible(show_mons)
        self.card_data.atk.setVisible(show_mons)
        self.card_data.race.setVisible(show_mons)
        self.card_data.from_.setVisible(show_mons)
        self.card_data.moveset.setVisible(show_mons)

    # 點擊 pic 時導入卡圖
    def set_pic(self):
        cdb, card = self._get_cdb_and_card()
        if not (cdb and card):
            return
        file_path, _ = QFileDialog.getOpenFileName(
            None, "选择卡图", "", "Images (*.jpg);;All Files (*)"
        )
        if not file_path:
            return
        pic_dir = cdb.get_pic_dir()
        try:
            os.makedirs(pic_dir, exist_ok=True)
        except Exception as e:
            show.error(f"無法建立資料夾 : {pic_dir}\n{e}")
            return

        pic_path = os.path.join(pic_dir, f"c{int(card.id)}.jpg")
        shutil.copyfile(file_path, pic_path)
        self.card_text.pic.set_path(pic_path)

    # ---------------- 按鈕事件 ----------------
    # 腳本
    def open_script(self):
        cdb, card = self._get_cdb_and_card()
        if not (cdb and card):
            return
        script_dir = cdb.get_script_dir()
        try:
            os.makedirs(script_dir, exist_ok=True)
        except Exception as e:
            show.error(f"無法建立資料夾 : {script_dir}\n{e}")
            return

        script_path = os.path.join(script_dir, f"c{card.id}.lua")
        if not os.path.exists(script_path):
            try:
                with open(script_path, "w", encoding="utf-8") as f:
                    lua = get_config().get_default_lua().format(card.name, card.id)
                    f.write(lua)
            except Exception as e:
                show.error(f"無法建立檔案 : {script_path}\n{e}")
                return
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(script_path)
            elif system == "Darwin":  # macOS
                subprocess.Popen(["open", script_path])
            else:  # Linux, XDG standard
                subprocess.Popen(["xdg-open", script_path])
        except Exception as e:
            show.error(f"無法打開檔案 : {script_path}\n{e}")

    # 編輯區 資料清除
    def clear_edit(self):
        self.card_data.clear()
        self.card_text.clear()

    # 編輯區 資料指向當前卡
    def refresh_edit(self):
        cdb, card = self._get_cdb_and_card()
        if not (cdb and card):
            return
        self.card_data.load_card(card)
        self.card_text.load_card(card)
        pic_path = os.path.join(cdb.get_pic_dir(), f"c{card.id}.jpg")
        self.card_text.pic.set_path(pic_path)

    # 添加卡片
    def add_card(self):
        id, alias = self.card_data.get_code()
        if id == 0:
            show.error("ID 格式錯誤")
            return
        cdb, _ = self._get_cdb_and_card()
        if cdb and cdb.add_card(self._pack_edit_to_card(id, alias)):
            self.card_list.on_cdb_change()

    # 保存卡片
    def save_card(self):
        cdb, card = self._get_cdb_and_card()
        if not card:
            show.error("当前没有可编辑的卡片, 请使用 添加")
            return
        id, alias = self.card_data.get_code()
        if id == 0:
            show.error("ID 格式錯誤")
            return
        c = self._pack_edit_to_card(id, alias)
        if card.id == id:
            cdb.save_card(c)
        else:
            cdb.del_id(card.id)
            if not cdb.add_card(c):
                return
        self.card_list.on_cdb_change()
        show.msg("修改成功")

    # 刪除卡片
    def delete_card(self):
        if (cdb := self.card_list.cdb) is None:
            return
        if cdb.del_select_card():
            self.card_list.set_data_source(cdb)
            self.refresh_edit()

    # ---------------- 內部函數 ----------------
    # 將當前編輯器內容打包成 Card 並返回
    def _pack_edit_to_card(self, id: int, alias: int) -> Card:
        c = Card(id)
        data_list = self.card_data.get_data_list()
        c.load_edit_data(alias, data_list)

        is_mons = bool(data_list[1] & TYPE_MONS)
        c.load_edit_text(self.card_text.get_text_list(is_mons))
        return c

    # 將指定 ID 的卡片複製到內部剪貼簿
    def _copy_id_list(self, cdb: CDB, id_list: list[int]):
        if not id_list:
            show.msg("没有卡片可复制")
            return
        self.copy_card = {}
        copy_ct = 0
        for id in id_list:
            if id in cdb.card_dict:
                card = cdb.card_dict[id]
                self.copy_card[id] = card
                copy_ct += 1
        show.msg(f"已复制 {copy_ct} 张卡片")
        self.update_past_txt.emit(copy_ct)

    # 獲取 cdb 與 now card
    def _get_cdb_and_card(self) -> tuple[CDB | None, Card | None]:
        cdb = self.card_list.cdb
        card = cdb.get_now_card() if cdb else None
        return (cdb, card)

    # ---------------- 調用事件 ----------------
    # 設定 cdb
    def set_cdb(self, cdb: CDB):
        self.card_list.set_data_source(cdb)
        self.refresh_edit()

    # 复制选中卡片
    def copy_select_card(self):
        if (cdb := self.card_list.cdb) is None:
            return
        self._copy_id_list(cdb, list(cdb.select_id_lst))

    # 复制所有卡片
    def copy_all_card(self):
        if (cdb := self.card_list.cdb) is None:
            return
        id_list = sorted(cdb.card_dict.keys(), key=lambda k: int(k))
        self._copy_id_list(cdb, id_list)

    # 粘贴卡片
    def paste_cards(self):
        if not self.copy_card:
            return
        if (cdb := self.card_list.cdb) is None:
            return
        paste_ct = 0
        last_id = None
        for card in self.copy_card.values():
            id = card.id
            try:
                if cdb.has_id(id):
                    if not show.quest(f"ID {id} 已存在, 是否覆蓋"):
                        continue
                cdb.add_card(card)
                last_id = id
                paste_ct += 1
            except Exception:
                continue
        if paste_ct > 0:
            if last_id:
                cdb.now_id = last_id
            self.card_list.set_data_source(cdb)
            self.refresh_edit()
            show.msg(f"已贴上 {paste_ct} 张卡片")
