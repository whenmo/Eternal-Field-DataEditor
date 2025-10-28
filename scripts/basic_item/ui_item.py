from PyQt6.QtWidgets import (
    QSizePolicy,
    QLabel,
    QWidget,
    QHBoxLayout,
    QGridLayout,
    QVBoxLayout,
    QLayout,
    QPushButton,
)


# frame 組件
def new_frame(
    path: str, parent: QWidget | QLayout, space: int | None = None, cut: bool = True
) -> QLayout:
    if path == "V":
        frame: QLayout = QVBoxLayout()
    elif path == "H":
        frame: QLayout = QHBoxLayout()
    elif path == "G":
        frame: QLayout = QGridLayout()

    if cut:
        frame.setContentsMargins(0, 0, 0, 0)  # 去掉多餘邊距

    if space is not None:
        frame.setSpacing(space)

    if isinstance(parent, QLayout):
        parent.addLayout(frame)
    else:  # QWidget
        parent.setLayout(frame)

    return frame


# 新版面容器
def new_panel(path: str = "V", space: int | None = None) -> tuple[QWidget, QLayout]:
    panel: QWidget = QWidget()
    frame = new_frame(path, panel, space)
    return [panel, frame]


# 标题組件
def new_title(title: str, frame: QLayout):
    lab = QLabel(title)
    lab.setStyleSheet("""
        background-color: lightgray;
        color: black;
        padding: 2px;
    """)
    size_policy = lab.sizePolicy()
    size_policy.setVerticalPolicy(QSizePolicy.Policy.Fixed)  # 禁止垂直拉伸
    lab.setSizePolicy(size_policy)
    frame.addWidget(lab)


# 按鈕組件
def new_btn(
    title: str, frame: QLayout, clicked_func=None, style: str = ""
) -> QPushButton:
    btn = QPushButton(title)
    style = f"""
        QPushButton {{
            min-width: 100px;
            font-size: 12px;
            {style}
        }}
    """
    btn.setStyleSheet(style)
    btn.setFixedHeight(30)
    frame.addWidget(btn)
    if clicked_func:
        btn.clicked.connect(clicked_func)
    return btn
