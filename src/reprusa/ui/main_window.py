from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .design_panel import DesignPanel
from .plot_view import Plotter2DView


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("RePrusa")

        self._tabs = QTabWidget(self)
        self._tabs.setDocumentMode(True)

        self._tab_design = QWidget()
        self._tab_toolpath = QWidget()

        self._build_design_tab()
        self._build_toolpath_tab()

        self._tabs.addTab(self._tab_design, "1. Design")
        self._tabs.addTab(self._tab_toolpath, "2. Toolpath")
        self._tabs.setTabEnabled(1, False)

        root = QWidget()
        lay = QVBoxLayout(root)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._tabs)
        self.setCentralWidget(root)

    def _build_design_tab(self) -> None:
        splitter = QSplitter(Qt.Horizontal, self._tab_design)

        self.design_panel = DesignPanel(splitter)
        self.preview = Plotter2DView(splitter)

        self.design_panel.design_changed.connect(self.preview.set_shapes)
        self.preview.set_shapes(self.design_panel.shapes())

        splitter.addWidget(self.design_panel)

        right = QWidget(splitter)
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(8)

        right_lay.addWidget(self.preview, 1)

        btn_row = QWidget(right)
        btn_row_l = QHBoxLayout(btn_row)
        btn_row_l.setContentsMargins(0, 0, 0, 0)

        btn_row_l.addStretch(1)
        self.btn_next = QPushButton("Next")
        self.btn_next.clicked.connect(self._go_to_toolpath)
        btn_row_l.addWidget(self.btn_next)

        right_lay.addWidget(btn_row, 0)
        splitter.addWidget(right)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        lay = QVBoxLayout(self._tab_design)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(splitter)

    def _build_toolpath_tab(self) -> None:
        lay = QVBoxLayout(self._tab_toolpath)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.addWidget(QLabel("Toolpath stage (coming soon)."))

    def _go_to_toolpath(self) -> None:
        self._tabs.setTabEnabled(1, True)
        self._tabs.setCurrentIndex(1)
