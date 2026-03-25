import sys
import cv2
import json
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel,
    QPushButton, QVBoxLayout, QHBoxLayout,
    QSpinBox, QStackedWidget, QTextEdit,
    QMessageBox, QLineEdit, QFrame, QSizePolicy, QComboBox
)
from PyQt6.QtGui import (QFont, QPixmap, QIcon, QImage)
from PyQt6.QtCore import QTimer, Qt

from kociemba_solver import solve_from_file
from m2op_solver import solve_from_file_2

import serial
import serial.tools.list_ports
import time

# ==========================================================
# CONFIG
# ==========================================================

COLOR_ORDER = ["White", "Red", "Green", "Yellow", "Orange", "Blue"]

COLOR_TO_FACE = {
    "White": "U",
    "Yellow": "D",
    "Green": "F",
    "Red": "R",
    "Orange": "L",
    "Blue": "B"
}

# ==========================================================
# CLASSIFICATION
# ==========================================================

def euclidean(a, b):
    return np.linalg.norm(np.array(a) - np.array(b))

def classify(mean_hsv, mean_lab, mean_rgb, colors_ref_roi):
    W_HSV = 0.4
    W_LAB = 0.6
    W_RGB = 0.0

    return min(
        colors_ref_roi.keys(),
        key=lambda c: (
            W_HSV * euclidean(mean_hsv, colors_ref_roi[c]["HSV"]) +
            W_LAB * euclidean(mean_lab, colors_ref_roi[c]["LAB"]) +
            W_RGB * euclidean(mean_rgb, colors_ref_roi[c]["RGB"])
        )
    )

# ==========================================================
# ROI CALIBRATION PAGE
# ==========================================================

class CalibrationPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
 
        self.camera_index = 0  

        self.center_x = 400
        self.center_y = 300
        self.roi_size = 60
        self.gap = 20

        self.current_frame = None

        # ================= CAMERA SELECTOR =================
        self.camera_spin = QSpinBox()
        self.camera_spin.setRange(0, 5)
        self.camera_spin.setValue(self.stacked_widget.camera_index)
        self.camera_spin.valueChanged.connect(self.change_camera)

        camera_layout = QHBoxLayout()
        camera_layout.addWidget(QLabel("Camera"))
        camera_layout.addWidget(self.camera_spin)
        camera_layout.addStretch()

        # ================= IMAGE =================
        self.image_label = QLabel()
        self.image_label.setFixedSize(800, 600)

        # ================= ROI SETTINGS =================
        self.size_spin = QSpinBox()
        self.size_spin.setRange(20, 200)
        self.size_spin.setValue(self.roi_size)
        self.size_spin.valueChanged.connect(lambda v: setattr(self, "roi_size", v))

        self.gap_spin = QSpinBox()
        self.gap_spin.setRange(0, 100)
        self.gap_spin.setValue(self.gap)
        self.gap_spin.valueChanged.connect(lambda v: setattr(self, "gap", v))

        settings = QHBoxLayout()
        settings.addWidget(QLabel("ROI Size"))
        settings.addWidget(self.size_spin)
        settings.addWidget(QLabel("Gap"))
        settings.addWidget(self.gap_spin)

        # ================= MOVE CONTROLS =================
        btn_up = QPushButton("Up")
        btn_down = QPushButton("Down")
        btn_left = QPushButton("Left")
        btn_right = QPushButton("Right")

        btn_up.clicked.connect(lambda: self.move(0, -10))
        btn_down.clicked.connect(lambda: self.move(0, 10))
        btn_left.clicked.connect(lambda: self.move(-10, 0))
        btn_right.clicked.connect(lambda: self.move(10, 0))

        controls = QHBoxLayout()
        controls.addWidget(btn_left)
        controls.addWidget(btn_up)
        controls.addWidget(btn_down)
        controls.addWidget(btn_right)

        # ================= ACTION BUTTONS =================
        btn_save = QPushButton("Save ROIs")
        btn_save.clicked.connect(self.save_rois)

        btn_back = QPushButton("Back")
        btn_back.clicked.connect(self.go_home)

        # ================= MAIN LAYOUT =================
        layout = QVBoxLayout()
        layout.setSpacing(6)        
        layout.setContentsMargins(8, 8, 8, 8)  

        layout.addLayout(camera_layout)
        layout.addWidget(self.image_label)
        layout.addLayout(controls)
        layout.addLayout(settings)
        layout.addWidget(btn_save)
        layout.addWidget(btn_back)
        layout.addStretch(0) 

        self.setLayout(layout)

    def start_camera(self, cam_index):
        self.stop_camera()
        self.cap = cv2.VideoCapture(cam_index)
        self.timer.start(30)

    def stop_camera(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None

    def change_camera(self, value):
        self.stacked_widget.camera_index = value
        self.stacked_widget.cover_page.camera_index = value
        self.stacked_widget.cover_page.btn_calib.setText(
            f"Calibration (Cam {value})"
        )
        self.start_camera(value)

    def move(self, dx, dy):
        self.center_x += dx
        self.center_y += dy

    def draw_grid(self, frame):
        rois = []
        total = 3 * self.roi_size + 2 * self.gap
        start_x = self.center_x - total // 2
        start_y = self.center_y - total // 2

        for row in range(3):
            for col in range(3):
                x = start_x + col * (self.roi_size + self.gap)
                y = start_y + row * (self.roi_size + self.gap)

                cv2.rectangle(frame, (x, y), (x + self.roi_size, y + self.roi_size), (0, 255, 0), 2)
                rois.append({"x": x, "y": y, "size": self.roi_size})

        return frame, rois

    def save_rois(self):
        if self.current_frame is None:
            return

        _, rois = self.draw_grid(self.current_frame.copy())
        with open("Software\Cube_app\rois.json", "w") as f:
            json.dump(rois, f, indent=4)

        self.stop_camera()
        self.stacked_widget.color_page.load_rois(rois)
        self.stacked_widget.setCurrentIndex(2)
        self.stacked_widget.color_page.start_camera(self.stacked_widget.camera_index)

    def update_frame(self):
        if not self.cap:
            return
        ret, frame = self.cap.read()
        if not ret:
            return
        frame = cv2.flip(frame, 1)
        self.current_frame = frame.copy()
        frame, _ = self.draw_grid(frame)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qt))

    def go_home(self):
        self.stop_camera()
        self.stacked_widget.setCurrentIndex(0)

# ==========================================================
# COLOR CALIBRATION PAGE
# ==========================================================

class ColorCalibrationPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.image_label = QLabel()
        self.image_label.setFixedSize(800, 600)

        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_capture = QPushButton("Capture Color")
        btn_capture.clicked.connect(self.capture_color)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.info_label)
        layout.addWidget(btn_capture)
        self.setLayout(layout)

    def load_rois(self, rois):
        self.rois = rois
        self.color_index = 0
        self.results = {}
        self.update_label()

    def update_label(self):
        self.info_label.setText(f"Place color: {COLOR_ORDER[self.color_index]}")

    def start_camera(self, cam_index):
        self.cap = cv2.VideoCapture(cam_index)
        self.timer.start(30)

    def stop_camera(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        frame = cv2.flip(frame, 1)
        self.current_frame = frame.copy()

        for roi in self.rois:
            x, y, s = roi["x"], roi["y"], roi["size"]
            cv2.rectangle(frame, (x, y), (x+s, y+s), (0,255,0), 2)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt = QImage(rgb.data, w, h, ch*w, QImage.Format.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qt))

    def capture_color(self):
        color = COLOR_ORDER[self.color_index]

        for i, roi in enumerate(self.rois):
            x, y, s = roi["x"], roi["y"], roi["size"]
            patch = self.current_frame[y:y+s, x:x+s]

            hsv = cv2.cvtColor(patch, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(patch, cv2.COLOR_BGR2LAB)

            mean_hsv = np.mean(hsv.reshape(-1,3), axis=0)
            mean_lab = np.mean(lab.reshape(-1,3), axis=0)
            mean_rgb = np.mean(patch.reshape(-1,3), axis=0)[::-1]

            roi_id = f"roi_{i+1}"
            if roi_id not in self.results:
                self.results[roi_id] = {}

            self.results[roi_id][color] = {
                "HSV": mean_hsv.tolist(),
                "LAB": mean_lab.tolist(),
                "RGB": mean_rgb.tolist()
            }

        self.color_index += 1

        if self.color_index == len(COLOR_ORDER):
            with open("Software\Cube_app\colors.json", "w") as f:
                json.dump(self.results, f, indent=4)
            self.stop_camera()
            self.stacked_widget.setCurrentIndex(0)
        else:
            self.update_label()

# ==========================================================
# CUBE STATE CAPTURE PAGE
# ==========================================================

class CubeStateCapturePage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.image_label = QLabel()
        self.image_label.setFixedSize(800, 600)

        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_capture = QPushButton("Capture Face")
        btn_capture.clicked.connect(self.capture_face)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.info_label)
        layout.addWidget(btn_capture)
        self.setLayout(layout)

    def load_data(self):
        with open("Software\Cube_app\rois.json") as f:
            self.rois = json.load(f)
        with open("Software\Cube_app\colors.json") as f:
            self.colors_ref = json.load(f)

        self.face_index = 0
        self.cube_string = ""
        self.update_label()

    def update_label(self):
        self.info_label.setText(f"Show face {self.face_index+1}/6")

    def start_camera(self, cam_index):
        self.cap = cv2.VideoCapture(cam_index)
        self.timer.start(30)

    def stop_camera(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        frame = cv2.flip(frame, 1)
        self.current_frame = frame.copy()

        for roi in self.rois:
            x, y, s = roi["x"], roi["y"], roi["size"]
            cv2.rectangle(frame, (x,y), (x+s,y+s), (0,255,0),2)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h,w,ch = rgb.shape
        qt = QImage(rgb.data,w,h,ch*w,QImage.Format.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qt))

    def capture_face(self):
        face_string = ""
        sorted_rois = sorted(self.rois, key=lambda r: (r["y"], -r["x"]))

        for roi in sorted_rois:
            x, y, s = roi["x"], roi["y"], roi["size"]
            patch = self.current_frame[y:y+s, x:x+s]

            hsv = cv2.cvtColor(patch, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(patch, cv2.COLOR_BGR2LAB)

            mean_hsv = np.mean(hsv.reshape(-1,3), axis=0)
            mean_lab = np.mean(lab.reshape(-1,3), axis=0)
            mean_rgb = np.mean(patch.reshape(-1,3), axis=0)[::-1]

            roi_id = self.rois.index(roi) + 1
            roi_key = f"roi_{roi_id}"

            color_name = classify(
                mean_hsv, mean_lab, mean_rgb, self.colors_ref[roi_key]
            )
            face_string += COLOR_TO_FACE[color_name]

        self.cube_string += face_string
        self.face_index += 1

        if self.face_index == 6:
            with open("Software\Cube_app\cube_state.json", "w") as f:
                json.dump({"cube_string": self.cube_string}, f, indent=4)
            QMessageBox.information(self, "Success", "Cube state saved!")
            self.stop_camera()
            self.stacked_widget.setCurrentIndex(0)
        else:
            self.update_label()


# ==========================================================
# COVER PAGE
# ==========================================================
class CoverPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setStyleSheet("font-weight: bold;")

        # ================= SERIAL =================
        self.arduino = None
        self.baudrate = 9600
        self.busy = False  

        # ================= UI =================
        title = QLabel("Rubik’s Cube Robot Solver")
        title.setFont(QFont("Arial", 26, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_label = QLabel()
        pixmap = QPixmap("Software\Cube_app\logo_pro.jpg")
        logo_label.setPixmap(
            pixmap.scaled(
                180, 160,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )
        logo_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.camera_spin = QSpinBox()
        self.camera_spin.setRange(0, 5)
        self.camera_spin.setValue(0)
        self.camera_spin.setStyleSheet("font-weight: bold;")

        # ================= DISPLAY TIME =================
        self.time_display = QLabel("Time: -- s")
        self.time_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_display.setFont(QFont("Arial", 58, QFont.Weight.Bold))
        self.time_display.setFixedHeight(160) 
        self.time_display.setStyleSheet("""
            QLabel {
                background-color: #4A6D70;
                color: white;
                border-radius: 10px;
                padding: 10px;
                font-weight: bold;
            }
        """)

        # ================= Buttons =================
        btn_style_base = "font-size: 16px; font-weight: bold; border-radius: 8px; padding: 10px; min-height: 40px; color: white;"
        btn_fixed_width = 280  
        
        btn_size_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        self.btn_calib = QPushButton("Calibration")
        self.btn_calib.clicked.connect(self.open_calibration)
        self.btn_calib.setFixedWidth(btn_fixed_width)
        self.btn_calib.setSizePolicy(btn_size_policy)
        self.btn_calib.setStyleSheet(f"QPushButton {{ background-color: #e74c3c; {btn_style_base} }} QPushButton:hover {{ background-color: #c0392b; }}")

        btn_capture = QPushButton("Capture Cube State")
        btn_capture.clicked.connect(self.open_capture)
        btn_capture.setFixedWidth(btn_fixed_width)
        btn_capture.setSizePolicy(btn_size_policy)
        btn_capture.setStyleSheet(f"QPushButton {{ background-color: #f39c12; {btn_style_base} }} QPushButton:hover {{ background-color: #e67e22; }}")

        btn_kociemba = QPushButton("Calculate solution with Kociemba")
        btn_kociemba.clicked.connect(self.solve_kociemba)
        btn_kociemba.setFixedWidth(btn_fixed_width)
        btn_kociemba.setSizePolicy(btn_size_policy)
        btn_kociemba.setStyleSheet(f"QPushButton {{ background-color: #3498db; {btn_style_base} }} QPushButton:hover {{ background-color: #2980b9; }}")

        btn_m2op = QPushButton("Calculate solution with M2/OP")
        btn_m2op.clicked.connect(self.solve_m2op)
        btn_m2op.setFixedWidth(btn_fixed_width)
        btn_m2op.setSizePolicy(btn_size_policy)
        btn_m2op.setStyleSheet(f"QPushButton {{ background-color: #3498db; {btn_style_base} }} QPushButton:hover {{ background-color: #2980b9; }}")

        # ================= RESULT AREA =================
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        self.result_area.setMinimumWidth(350) 
        self.result_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.result_area.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        btn_send_robot = QPushButton("Send Solve")
        btn_send_robot.clicked.connect(self.send_to_robot)
        btn_send_robot.setFixedWidth(btn_fixed_width)
        btn_send_robot.setSizePolicy(btn_size_policy)
        btn_send_robot.setStyleSheet(f"QPushButton {{ background-color: #2ecc71; {btn_style_base} }} QPushButton:hover {{ background-color: #27ae60; }}")

        btn_send_inverted = QPushButton("Send Scramble (Reverse)")
        btn_send_inverted.clicked.connect(self.send_inverted_to_robot)
        btn_send_inverted.setFixedWidth(btn_fixed_width)
        btn_send_inverted.setSizePolicy(btn_size_policy)
        btn_send_inverted.setStyleSheet(f"QPushButton {{ background-color: #2ecc71; {btn_style_base} }} QPushButton:hover {{ background-color: #27ae60; }}")

        # ================= MANUAL =================
        self.manual_input = QLineEdit()
        self.manual_input.setStyleSheet("""
            QLineEdit {
                background-color: #6527F5;
                color: white;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }""")
        btn_send_manual = QPushButton("Send Manual Sequence")
        btn_send_manual.clicked.connect(self.send_manual_sequence)
        btn_send_manual.setStyleSheet(f"QPushButton {{ background-color: #B027F5; {btn_style_base} }} QPushButton:hover {{ background-color: #27ae60; }}")

        # ================= ROBOT SETTINGS =================
        self.port_combo = QComboBox()
        # Estilo para deixar o fundo da lista preto e o texto branco
        self.port_combo.setStyleSheet("""
            QComboBox {
                padding: 6px; 
                font-weight: bold;
            }
            QComboBox QAbstractItemView {
                background-color: black;
                color: white;
                selection-background-color: #3498db;
            }
        """)
        
        # Se você adicionou o botão de refresh na etapa anterior, mantenha ele aqui
        self.btn_refresh_ports = QPushButton("↻ Refresh")
        self.btn_refresh_ports.setStyleSheet("padding: 6px; font-weight: bold; background-color: #95a5a6; color: white; border-radius: 4px;")
        self.btn_refresh_ports.clicked.connect(self.atualizar_portas)

        self.atualizar_portas() 

        # Estilo para alargar os botões das setas (up/down)
        spinbox_style = """
            QSpinBox {
                padding: 6px; 
                font-weight: bold;
            }
            QSpinBox::up-button {
                width: 35px; /* Deixa o botão de cima mais largo */
            }
            QSpinBox::down-button {
                width: 35px; /* Deixa o botão de baixo mais largo */
            }
        """

        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(1, 10000)
        self.speed_spin.setValue(1000)
        self.speed_spin.setStyleSheet(spinbox_style)

        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 2000)
        self.delay_spin.setValue(10)
        self.delay_spin.setStyleSheet(spinbox_style)

        # ================= LAYOUT =================
        layout = QVBoxLayout()
        layout.addWidget(title)
        
        logo_time_layout = QHBoxLayout()
        logo_time_layout.setAlignment(Qt.AlignmentFlag.AlignLeft) 
        logo_time_layout.setSpacing(10)
        logo_time_layout.addWidget(logo_label)
        logo_time_layout.addWidget(self.time_display, stretch=1) 
        layout.addLayout(logo_time_layout)

        line_style = "border: 1px solid rgba(255, 255, 255, 128); background-color: rgba(255, 255, 255, 128);"
        line_thickness = 2 

        line_top = QFrame()
        line_top.setFrameShape(QFrame.Shape.HLine)
        line_top.setStyleSheet(line_style)
        line_top.setFixedHeight(line_thickness)
        layout.addWidget(line_top)

        split_layout = QHBoxLayout()
        left_panel = QVBoxLayout()
        right_panel = QVBoxLayout()

        columns_layout = QHBoxLayout() 
        column_title_font = QFont("Arial", 16, QFont.Weight.Bold)

        # Col 1
        col1 = QVBoxLayout()
        lbl_col1 = QLabel("Calibration")
        lbl_col1.setFont(column_title_font)
        lbl_col1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        col1.addWidget(lbl_col1)
        col1.addWidget(self.btn_calib)
        col1.addWidget(btn_capture)
        columns_layout.addLayout(col1)

        line_v1 = QFrame()
        line_v1.setFrameShape(QFrame.Shape.VLine)
        line_v1.setStyleSheet(line_style)
        line_v1.setFixedWidth(line_thickness)
        columns_layout.addWidget(line_v1)

        # Col 2
        col2 = QVBoxLayout()
        lbl_col2 = QLabel("Calculate Solution")
        lbl_col2.setFont(column_title_font)
        lbl_col2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        col2.addWidget(lbl_col2)
        col2.addWidget(btn_kociemba)
        col2.addWidget(btn_m2op)
        columns_layout.addLayout(col2)

        line_v2 = QFrame()
        line_v2.setFrameShape(QFrame.Shape.VLine)
        line_v2.setStyleSheet(line_style)
        line_v2.setFixedWidth(line_thickness)
        columns_layout.addWidget(line_v2)

        # Col 3
        col3 = QVBoxLayout()
        lbl_col3 = QLabel("Send to Robot")
        lbl_col3.setFont(column_title_font)
        lbl_col3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        col3.addWidget(lbl_col3)
        col3.addWidget(btn_send_robot)
        col3.addWidget(btn_send_inverted)
        columns_layout.addLayout(col3)

        left_panel.addLayout(columns_layout)

        line_mid = QFrame()
        line_mid.setFrameShape(QFrame.Shape.HLine)
        line_mid.setStyleSheet(line_style)
        line_mid.setFixedHeight(line_thickness)
        left_panel.addWidget(line_mid)

        # --- SETTINGS ---
        settings_matrix_layout = QHBoxLayout()
        
        matrix_col_port = QVBoxLayout()
        lbl_port = QLabel("Serial Port")
        lbl_port.setStyleSheet("font-weight: bold;")
        matrix_col_port.addWidget(lbl_port)
        matrix_col_port.addWidget(self.port_combo)
        settings_matrix_layout.addLayout(matrix_col_port)

        matrix_col_speed = QVBoxLayout()
        lbl_speed = QLabel("Robot Speed")
        lbl_speed.setStyleSheet("font-weight: bold;")
        matrix_col_speed.addWidget(lbl_speed)
        matrix_col_speed.addWidget(self.speed_spin)
        settings_matrix_layout.addLayout(matrix_col_speed)

        matrix_col_delay = QVBoxLayout()
        lbl_delay = QLabel("Delay Between Moves (ms)")
        lbl_delay.setStyleSheet("font-weight: bold;")
        matrix_col_delay.addWidget(lbl_delay)
        matrix_col_delay.addWidget(self.delay_spin)
        settings_matrix_layout.addLayout(matrix_col_delay)

        left_panel.addLayout(settings_matrix_layout)

        line_bot = QFrame()
        line_bot.setFrameShape(QFrame.Shape.HLine)
        line_bot.setStyleSheet(line_style)
        line_bot.setFixedHeight(line_thickness)
        left_panel.addWidget(line_bot)

        # --- MANUAL ---
        lbl_manual = QLabel("Manual Sequence")
        lbl_manual.setStyleSheet("font-weight: bold;")
        left_panel.addWidget(lbl_manual)
        left_panel.addWidget(self.manual_input)
        left_panel.addWidget(btn_send_manual)
        
        # --- RESULT AREA ---
        lbl_result = QLabel("Result:")
        lbl_result.setStyleSheet("font-weight: bold;")
        right_panel.addWidget(lbl_result)
        right_panel.addWidget(self.result_area)
        
        split_layout.addLayout(left_panel)
        
        line_v_split = QFrame()
        line_v_split.setFrameShape(QFrame.Shape.VLine)
        line_v_split.setStyleSheet(line_style)
        line_v_split.setFixedWidth(line_thickness)
        split_layout.addWidget(line_v_split)
        
        split_layout.addLayout(right_panel)

        layout.addLayout(split_layout)

        self.setLayout(layout)

        self.serial_timer = QTimer()
        self.serial_timer.timeout.connect(self.check_serial)
        self.serial_timer.start(50)  

    # ================= MÉTODOS =================
    
    def atualizar_portas(self):
        self.port_combo.clear()
        portas = serial.tools.list_ports.comports()
        for porta in portas:
            self.port_combo.addItem(porta.device)

    def init_serial(self):
        if self.arduino is None:
            porta_selecionada = self.port_combo.currentText()
            if not porta_selecionada:
                QMessageBox.warning(self, "Error", "No COM port detected or selected!")
                return

            try:
                # Instanciamos a porta sem a abrir imediatamente
                self.arduino = serial.Serial()
                self.arduino.port = porta_selecionada
                self.arduino.baudrate = self.baudrate
                self.arduino.timeout = 1
                
                # Desativa o DTR para evitar o reset do Arduino!
                self.arduino.setDTR(False) 
                self.arduino.open()
                

                time.sleep(3)   #Não deixe esse tempo abaixo de 3s


                print(f"Serial Connected to {porta_selecionada}!")
            except Exception as e:
                QMessageBox.warning(self, "Serial Error", f"Failed to connect to {porta_selecionada}:\n{str(e)}")
                self.arduino = None

    def check_serial(self):
        if self.arduino and self.arduino.in_waiting:
            response = self.arduino.readline().decode().strip()
            if response.startswith("DONE"):
                try:
                    tempo = response.split()[1]
                    self.time_display.setText(f"Time: {tempo} s")
                except:
                    self.time_display.setText("Time: Error")
                self.busy = False  

    def send_sequence_to_robot(self, sequence):
        if not sequence:
            QMessageBox.warning(self, "Error", "Sequence is empty.")
            return
        if self.busy:
            QMessageBox.information(self, "Robot Busy", "Wait until current execution finishes.")
            return
        self.init_serial()
        if self.arduino is None:
            return
        speed = self.speed_spin.value()
        delay = self.delay_spin.value()
        try:
            self.busy = True
            self.time_display.setText("Executing...")
            
            self.arduino.reset_input_buffer()
            self.arduino.reset_output_buffer()

            self.arduino.write(b"<START>\n")
            self.arduino.write(f"<SPEED:{speed}>\n".encode())
            self.arduino.write(f"<DELAY:{delay}>\n".encode())
            for move in sequence:
                self.arduino.write((move + "\n").encode())
                time.sleep(0.005)
            self.arduino.write(b"<END>\n")
        except Exception as e:
            QMessageBox.warning(self, "Serial Error", str(e))
            self.busy = False


    def send_manual_sequence(self):
        raw_sequence = self.manual_input.text().strip()
        if not raw_sequence:
            QMessageBox.warning(self, "Error", "Manual sequence is empty.")
            return
        try:
            converted = self.converter_movimentos(raw_sequence)
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
            return
        self.send_sequence_to_robot(converted)

    def converter_movimentos(self, seq):
        tabela = {
            "U": "A", "U'": "B", "U2": "C",
            "R": "D", "R'": "E", "R2": "F",
            "F": "G", "F'": "H", "F2": "I",
            "D": "J", "D'": "K", "D2": "L",
            "L": "M", "L'": "N", "L2": "O",
            "B": "P", "B'": "Q", "B2": "R"
        }
        try:
            return "".join(tabela[m] for m in seq.split())
        except KeyError as e:
            raise ValueError(f"Invalid move: {e}")

    def send_to_robot(self):
        text = self.result_area.toPlainText()
        if "SEQUENCE FOR THE ROBOT" not in text:
            QMessageBox.warning(self, "Error", "No robot sequence found.")
            return
        try:
            part = text.split("===== SEQUENCE FOR THE ROBOT =====")[1]
            robot_sequence = part.split("===== INVERTED SEQUENCE =====")[0].strip()
        except:
            QMessageBox.warning(self, "Error", "Could not parse robot sequence.")
            return
        self.send_sequence_to_robot(robot_sequence)

    def send_inverted_to_robot(self):
        text = self.result_area.toPlainText()
        if "INVERTED SEQUENCE" not in text:
            QMessageBox.warning(self, "Error", "No inverted sequence found.")
            return
        try:
            part = text.split("===== INVERTED SEQUENCE =====")[1]
            inverted_sequence = part.strip()
        except:
            QMessageBox.warning(self, "Error", "Could not parse inverted sequence.")
            return
        self.send_sequence_to_robot(inverted_sequence)

    def open_calibration(self):
        self.stacked_widget.camera_index = self.camera_spin.value()
        self.stacked_widget.setCurrentIndex(1)
        self.stacked_widget.calibration_page.start_camera(self.stacked_widget.camera_index)

    def open_capture(self):
        self.stacked_widget.camera_index = self.camera_spin.value()
        self.stacked_widget.setCurrentIndex(3)
        self.stacked_widget.cube_page.load_data()
        self.stacked_widget.cube_page.start_camera(self.stacked_widget.camera_index)

    def solve_kociemba(self):
        try:
            result = solve_from_file("Software\Cube_app\cube_state.json")
            if "error" in result:
                self.result_area.setText(f"Error:\n{result['error']}")
                return
            text = (
                "===== SOLUTION (KOCIEMBA) =====\n\n"
                f"{result['solution']}\n\n"
                "===== NUMBER OF MOVES =====\n\n"
                f"{result['move_count']}\n\n"
                "===== SEQUENCE FOR THE ROBOT =====\n\n"
                f"{result['robot_sequence']}\n\n"
                "===== INVERTED SEQUENCE =====\n\n"
                f"{result['inverted_sequence']}"
            )
            self.result_area.setText(text)
        except FileNotFoundError:
            self.result_area.setText("First capture the cube.")

    def solve_m2op(self):
        try:
            result = solve_from_file_2("Software\Cube_app\cube_state.json")
            if "error" in result:
                self.result_area.setText(f"Error:\n{result['error']}")
                return
            text = (
                "===== SOLUTION (M2/OP) =====\n\n"
                f"{result['solution']}\n\n"
                "===== NUMBER OF MOVES =====\n\n"
                f"{result['move_count']}\n\n"
                "===== SEQUENCE FOR THE ROBOT =====\n\n"
                f"{result['robot_sequence']}\n\n"
                "===== INVERTED SEQUENCE =====\n\n"
                f"{result['inverted_sequence']}"
            )
            self.result_area.setText(text)
        except FileNotFoundError:
            self.result_area.setText("First capture the cube.")

# ==========================================================
# MAIN
# ==========================================================

class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.camera_index = 0

        self.calibration_page = CalibrationPage(self)
        self.color_page = ColorCalibrationPage(self)
        self.cube_page = CubeStateCapturePage(self)
        self.cover_page = CoverPage(self)

        self.addWidget(self.cover_page)        
        self.addWidget(self.calibration_page)  
        self.addWidget(self.color_page)        
        self.addWidget(self.cube_page)         

    def closeEvent(self, event):
        try:
            if self.cover_page.arduino:
                self.cover_page.arduino.close()
                print("Serial fechada.")
        except:
            pass
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    
    # TÍTULO E ÍCONE DEFINIDOS AQUI!
    window.setWindowTitle("Rubik’s Cube Robot Solver")
    window.setWindowIcon(QIcon("Software\Cube_app\logo_pro.jpg"))
    
    window.resize(900, 750)
    window.show()
    sys.exit(app.exec())