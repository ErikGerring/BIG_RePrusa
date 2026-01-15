from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..core.model import Point
from ..core.primitive import (
    CircleGeometry,
    RectangleGeometry,
    Shape,
    crosshatch_pattern,
    hatch_pattern,
    none_pattern,
)


class DesignPanel(QWidget):
    design_changed = Signal(object)  # emits List[Shape]

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setMinimumWidth(340)
        self.setMaximumWidth(420)

        self._shapes: list[Shape] = []
        self._active_index: int = -1
        self._loading = False

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # Shapes list
        grp_shapes = QGroupBox("Shapes")
        grp_lay = QVBoxLayout(grp_shapes)

        self.lst_shapes = QListWidget(grp_shapes)
        self.lst_shapes.currentRowChanged.connect(self._on_select_shape)
        grp_lay.addWidget(self.lst_shapes)

        btn_row = QWidget(grp_shapes)
        btn_row_l = QHBoxLayout(btn_row)
        btn_row_l.setContentsMargins(0, 0, 0, 0)

        self.cmb_add_shape = QComboBox()
        self.cmb_add_shape.addItems(["Rectangle", "Circle"])
        self.btn_add = QPushButton("Add")
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setEnabled(False)

        self.btn_add.clicked.connect(self._add_selected_kind)
        self.btn_delete.clicked.connect(self._delete_selected)

        btn_row_l.addWidget(self.cmb_add_shape, 1)
        btn_row_l.addWidget(self.btn_add)
        btn_row_l.addWidget(self.btn_delete)
        grp_lay.addWidget(btn_row)

        root.addWidget(grp_shapes)

        # Editor
        grp_edit = QGroupBox("Selected Shape")
        grp_edit_lay = QVBoxLayout(grp_edit)

        self.lbl_none = QLabel("No shape selected.")
        grp_edit_lay.addWidget(self.lbl_none)

        # Type selector (shown only when a shape is selected)
        self._type_row = QWidget(grp_edit)
        type_form = QFormLayout(self._type_row)
        type_form.setContentsMargins(0, 0, 0, 0)
        self.cmb_kind = QComboBox()
        self.cmb_kind.addItems(["Rectangle", "Circle"])
        self.cmb_kind.currentIndexChanged.connect(self._on_kind_changed)
        type_form.addRow("Type", self.cmb_kind)
        grp_edit_lay.addWidget(self._type_row)

        # Geometry editor (stacked)
        self.geom_stack = QStackedWidget(grp_edit)

        rect_page = QWidget(self.geom_stack)
        rect_form = QFormLayout(rect_page)
        self.sp_rect_x = self._spin()
        self.sp_rect_y = self._spin()
        self.sp_rect_w = self._spin(minimum=0.0)
        self.sp_rect_h = self._spin(minimum=0.0)
        for w in [self.sp_rect_x, self.sp_rect_y, self.sp_rect_w, self.sp_rect_h]:
            w.valueChanged.connect(self._on_geom_changed)
        rect_form.addRow("X", self.sp_rect_x)
        rect_form.addRow("Y", self.sp_rect_y)
        rect_form.addRow("Width", self.sp_rect_w)
        rect_form.addRow("Height", self.sp_rect_h)

        circle_page = QWidget(self.geom_stack)
        circle_form = QFormLayout(circle_page)
        self.sp_cx = self._spin()
        self.sp_cy = self._spin()
        self.sp_r = self._spin(minimum=0.0)
        self.sp_psides = QSpinBox()
        self.sp_psides.setRange(8, 360)
        for w in [self.sp_cx, self.sp_cy, self.sp_r]:
            w.valueChanged.connect(self._on_geom_changed)
        self.sp_psides.valueChanged.connect(self._on_geom_changed)
        circle_form.addRow("Center X", self.sp_cx)
        circle_form.addRow("Center Y", self.sp_cy)
        circle_form.addRow("Radius", self.sp_r)
        circle_form.addRow("Sides", self.sp_psides)

        self.geom_stack.addWidget(rect_page)
        self.geom_stack.addWidget(circle_page)
        grp_edit_lay.addWidget(self.geom_stack)

        # Fill selector (shown only when a shape is selected)
        self._fill_row = QWidget(grp_edit)
        fill_form = QFormLayout(self._fill_row)
        fill_form.setContentsMargins(0, 0, 0, 0)

        self.cmb_pattern = QComboBox()
        self.cmb_pattern.addItems(["None", "Hatch", "Cross Hatch"])
        self.cmb_pattern.currentIndexChanged.connect(self._on_pattern_changed)
        fill_form.addRow("Fill", self.cmb_pattern)
        grp_edit_lay.addWidget(self._fill_row)

        # Pattern editor (stacked)
        self.pattern_stack = QStackedWidget(grp_edit)

        none_page = QWidget(self.pattern_stack)
        none_lay = QVBoxLayout(none_page)
        none_lay.setContentsMargins(0, 0, 0, 0)
        none_lay.addWidget(QLabel("No fill pattern."))

        hatch_page = QWidget(self.pattern_stack)
        hatch_form = QFormLayout(hatch_page)
        self.sp_angle = self._spin()
        self.sp_spacing = self._spin(minimum=0.1)
        self.sp_overscan = self._spin(minimum=0.0)
        for w in [self.sp_angle, self.sp_spacing, self.sp_overscan]:
            w.valueChanged.connect(self._on_pattern_params_changed)
        hatch_form.addRow("Angle", self.sp_angle)
        hatch_form.addRow("Spacing", self.sp_spacing)
        hatch_form.addRow("Overscan", self.sp_overscan)

        # Crosshatch page (two side-by-side parameter sections)
        cross_page = QWidget(self.pattern_stack)
        cross_lay = QHBoxLayout(cross_page)
        cross_lay.setContentsMargins(0, 0, 0, 0)

        grp_a = QGroupBox("Hatch 1", cross_page)
        a_form = QFormLayout(grp_a)
        self.sp_c_angle = self._spin()
        self.sp_c_spacing = self._spin(minimum=0.1)
        self.sp_c_overscan = self._spin(minimum=0.0)
        for w in [self.sp_c_angle, self.sp_c_spacing, self.sp_c_overscan]:
            w.valueChanged.connect(self._on_pattern_params_changed)
        a_form.addRow("Angle", self.sp_c_angle)
        a_form.addRow("Spacing", self.sp_c_spacing)
        a_form.addRow("Overscan", self.sp_c_overscan)

        grp_b = QGroupBox("Hatch 2", cross_page)
        b_form = QFormLayout(grp_b)
        self.sp_c_offset = self._spin()
        self.sp_c2_spacing = self._spin(minimum=0.1)
        self.sp_c2_overscan = self._spin(minimum=0.0)
        for w in [self.sp_c_offset, self.sp_c2_spacing, self.sp_c2_overscan]:
            w.valueChanged.connect(self._on_pattern_params_changed)
        b_form.addRow("Angle Offset", self.sp_c_offset)
        b_form.addRow("Spacing", self.sp_c2_spacing)
        b_form.addRow("Overscan", self.sp_c2_overscan)

        cross_lay.addWidget(grp_a, 1)
        cross_lay.addWidget(grp_b, 1)

        self.pattern_stack.addWidget(none_page)
        self.pattern_stack.addWidget(hatch_page)
        self.pattern_stack.addWidget(cross_page)
        grp_edit_lay.addWidget(self.pattern_stack)

        root.addWidget(grp_edit)
        root.addStretch(1)

        self._set_editor_enabled(False)

    def shapes(self) -> list[Shape]:
        return list(self._shapes)

    def _spin(self, *, minimum: float = -1e9, maximum: float = 1e9) -> QDoubleSpinBox:
        sp = QDoubleSpinBox()
        sp.setRange(minimum, maximum)
        sp.setDecimals(3)
        sp.setSingleStep(1.0)
        return sp

    def _emit(self) -> None:
        self.design_changed.emit(self.shapes())

    def _set_editor_enabled(self, enabled: bool) -> None:
        self.btn_delete.setEnabled(enabled)
        self.lbl_none.setVisible(not enabled)

        self._type_row.setVisible(enabled)
        self.geom_stack.setVisible(enabled)
        self._fill_row.setVisible(enabled)
        self.pattern_stack.setVisible(enabled)

        self.cmb_kind.setEnabled(enabled)
        self.geom_stack.setEnabled(enabled)
        self.cmb_pattern.setEnabled(enabled)
        self.pattern_stack.setEnabled(enabled)

    def _refresh_list(self) -> None:
        self.lst_shapes.blockSignals(True)
        self.lst_shapes.clear()
        for i, s in enumerate(self._shapes, start=1):
            item = QListWidgetItem(f"{i}. {s.kind.capitalize()}")
            self.lst_shapes.addItem(item)
        self.lst_shapes.blockSignals(False)

        if 0 <= self._active_index < len(self._shapes):
            self.lst_shapes.setCurrentRow(self._active_index)

    def _add_selected_kind(self) -> None:
        kind = self.cmb_add_shape.currentText()
        if kind == "Circle":
            s = Shape.circle(center=(60.0, 60.0), radius=20.0, psides=48, fillpattern=none_pattern())
        else:
            s = Shape.rectangle(bottom_left=(20.0, 20.0), width=40.0, height=30.0, fillpattern=none_pattern())
        self._shapes.append(s)
        self._active_index = len(self._shapes) - 1
        self._refresh_list()
        self._load_active()
        self._emit()

    def _delete_selected(self) -> None:
        if not (0 <= self._active_index < len(self._shapes)):
            return
        self._shapes.pop(self._active_index)
        if not self._shapes:
            self._active_index = -1
        else:
            self._active_index = max(0, min(self._active_index, len(self._shapes) - 1))
        self._refresh_list()
        self._load_active()
        self._emit()

    def _on_select_shape(self, row: int) -> None:
        self._active_index = row
        self._load_active()

    def _active(self) -> Optional[Shape]:
        if 0 <= self._active_index < len(self._shapes):
            return self._shapes[self._active_index]
        return None

    def _load_active(self) -> None:
        s = self._active()
        self._loading = True
        try:
            if s is None:
                self._set_editor_enabled(False)
                return

            self._set_editor_enabled(True)

            # Geometry
            if isinstance(s.geometry, RectangleGeometry):
                self.cmb_kind.setCurrentText("Rectangle")
                self.geom_stack.setCurrentIndex(0)
                x, y = s.geometry.bottom_left
                self.sp_rect_x.setValue(x)
                self.sp_rect_y.setValue(y)
                self.sp_rect_w.setValue(float(s.geometry.width))
                self.sp_rect_h.setValue(float(s.geometry.height))
            else:
                self.cmb_kind.setCurrentText("Circle")
                self.geom_stack.setCurrentIndex(1)
                x, y = s.geometry.center
                self.sp_cx.setValue(x)
                self.sp_cy.setValue(y)
                self.sp_r.setValue(float(s.geometry.radius))
                self.sp_psides.setValue(int(s.geometry.psides))

            # Pattern
            if isinstance(s.fillpattern, hatch_pattern):
                self.cmb_pattern.setCurrentText("Hatch")
                self.pattern_stack.setCurrentIndex(1)
                self.sp_angle.setValue(float(s.fillpattern.angle))
                self.sp_spacing.setValue(float(s.fillpattern.spacing))
                self.sp_overscan.setValue(float(s.fillpattern.overscan))
            elif isinstance(s.fillpattern, crosshatch_pattern):
                self.cmb_pattern.setCurrentText("Cross Hatch")
                self.pattern_stack.setCurrentIndex(2)
                self.sp_c_angle.setValue(float(s.fillpattern.angle))
                self.sp_c_spacing.setValue(float(s.fillpattern.spacing))
                self.sp_c_overscan.setValue(float(s.fillpattern.overscan))
                self.sp_c_offset.setValue(float(s.fillpattern.angle_offset))
                self.sp_c2_spacing.setValue(float(s.fillpattern.spacing2 if s.fillpattern.spacing2 is not None else s.fillpattern.spacing))
                self.sp_c2_overscan.setValue(float(s.fillpattern.overscan2 if s.fillpattern.overscan2 is not None else s.fillpattern.overscan))
            else:
                self.cmb_pattern.setCurrentText("None")
                self.pattern_stack.setCurrentIndex(0)
                # Defaults for when user switches to hatch
                self.sp_angle.setValue(0.0)
                self.sp_spacing.setValue(2.0)
                self.sp_overscan.setValue(0.0)
                self.sp_c_angle.setValue(0.0)
                self.sp_c_spacing.setValue(2.0)
                self.sp_c_overscan.setValue(0.0)
                self.sp_c_offset.setValue(90.0)
                self.sp_c2_spacing.setValue(2.0)
                self.sp_c2_overscan.setValue(0.0)

        finally:
            self._loading = False

    def _on_kind_changed(self) -> None:
        if self._loading:
            return
        s = self._active()
        if s is None:
            return

        kind = self.cmb_kind.currentText()
        if kind == "Rectangle" and not isinstance(s.geometry, RectangleGeometry):
            # Convert circle -> rectangle (keep roughly similar size)
            cx, cy = s.geometry.center  # type: ignore[attr-defined]
            r = float(getattr(s.geometry, "radius", 10.0))
            s.geometry = RectangleGeometry(bottom_left=(cx - r, cy - r), width=2 * r, height=2 * r)
        elif kind == "Circle" and not isinstance(s.geometry, CircleGeometry):
            x, y = s.geometry.bottom_left  # type: ignore[attr-defined]
            w = float(getattr(s.geometry, "width", 10.0))
            h = float(getattr(s.geometry, "height", 10.0))
            r = max(1.0, min(w, h) * 0.5)
            s.geometry = CircleGeometry(center=(x + w * 0.5, y + h * 0.5), radius=r, psides=48)

        self._refresh_list()
        self._load_active()
        self._emit()

    def _on_geom_changed(self) -> None:
        if self._loading:
            return
        s = self._active()
        if s is None:
            return

        if self.cmb_kind.currentText() == "Rectangle":
            s.geometry = RectangleGeometry(
                bottom_left=(self.sp_rect_x.value(), self.sp_rect_y.value()),
                width=self.sp_rect_w.value(),
                height=self.sp_rect_h.value(),
            )
        else:
            s.geometry = CircleGeometry(
                center=(self.sp_cx.value(), self.sp_cy.value()),
                radius=self.sp_r.value(),
                psides=int(self.sp_psides.value()),
            )

        self._emit()

    def _on_pattern_changed(self) -> None:
        if self._loading:
            return
        s = self._active()
        if s is None:
            return

        if self.cmb_pattern.currentText() == "Hatch":
            self.pattern_stack.setCurrentIndex(1)
            s.fillpattern = hatch_pattern(
                angle=self.sp_angle.value(),
                spacing=max(0.1, self.sp_spacing.value()),
                overscan=max(0.0, self.sp_overscan.value()),
            )
        elif self.cmb_pattern.currentText() == "Cross Hatch":
            self.pattern_stack.setCurrentIndex(2)
            s.fillpattern = crosshatch_pattern(
                angle=self.sp_c_angle.value(),
                spacing=max(0.1, self.sp_c_spacing.value()),
                overscan=max(0.0, self.sp_c_overscan.value()),
                angle_offset=self.sp_c_offset.value(),
                spacing2=max(0.1, self.sp_c2_spacing.value()),
                overscan2=max(0.0, self.sp_c2_overscan.value()),
            )
        else:
            self.pattern_stack.setCurrentIndex(0)
            s.fillpattern = none_pattern()

        self._emit()

    def _on_pattern_params_changed(self) -> None:
        if self._loading:
            return
        s = self._active()
        if s is None:
            return
        mode = self.cmb_pattern.currentText()
        if mode == "Hatch":
            s.fillpattern = hatch_pattern(
                angle=self.sp_angle.value(),
                spacing=max(0.1, self.sp_spacing.value()),
                overscan=max(0.0, self.sp_overscan.value()),
            )
        elif mode == "Cross Hatch":
            s.fillpattern = crosshatch_pattern(
                angle=self.sp_c_angle.value(),
                spacing=max(0.1, self.sp_c_spacing.value()),
                overscan=max(0.0, self.sp_c_overscan.value()),
                angle_offset=self.sp_c_offset.value(),
                spacing2=max(0.1, self.sp_c2_spacing.value()),
                overscan2=max(0.0, self.sp_c2_overscan.value()),
            )
        else:
            return
        self._emit()
