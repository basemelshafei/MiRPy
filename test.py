import sys
import random
import time
import webbrowser
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout,
    QDialog, QFormLayout, QSpinBox, QCheckBox, QGroupBox, QScrollArea, QDialogButtonBox
)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QIcon, QPainter, QPen, QColor

class DataFetcher(QThread):
    dataFetched = pyqtSignal(dict)

    def run(self):
        while True:
            # Simulate fetching data
            data = {
                "joystick_low_speed_mode_enabled": random.choice([True, False]),
                "mission_queue_url": "http://example.com/mission_queue",
                "mode_id": random.randint(1, 10),
                "moved": random.randint(0, 1000),
                "mission_queue_id": random.randint(1, 100),
                "robot_name": f"Robot-{random.randint(1, 100)}",
                "joystick_web_session_id": f"Session-{random.randint(1, 100)}",
                "uptime": random.randint(0, 10000),
                "errors": random.choice([[], ["Error 1", "Error 2"]]),
                "unloaded_map_changes": random.randint(0, 5),
                "distance_to_next_target": round(random.uniform(0, 10), 2),
                "serial_number": f"SN-{random.randint(1000, 9999)}",
                "mode_key_state": random.choice(["STATE1", "STATE2"]),
                "battery_percentage": round(random.uniform(0, 100), 2),
                "map_id": random.randint(1, 10),
                "safety_system_muted": random.choice([True, False]),
                "mission_text": "Mission in progress",
                "state_text": "Active",
                "velocity": round(random.uniform(0, 2), 2),
                "footprint": "Normal",
                "user_prompt": "No prompt",
                "allowed_methods": ["GET", "POST"],
                "robot_model": "MiR100",
                "mode_text": "Operational",
                "session_id": f"Session-{random.randint(100, 999)}",
                "state_id": random.randint(1, 5),
                "battery_time_remaining": random.randint(0, 120),
                "position": {"x": round(random.uniform(0, 100), 2), "y": round(random.uniform(0, 100), 2)}
            }

            self.dataFetched.emit(data)
            time.sleep(2)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MiR Data Fetcher")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('path/to/your/icon.png'))  # Set the window icon

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.input_layout = QHBoxLayout()
        self.layout.addLayout(self.input_layout)

        self.label = QLabel("Enter MiR IP:")
        self.input_layout.addWidget(self.label)

        self.ip_input = QLineEdit()
        self.input_layout.addWidget(self.ip_input)

        self.request_button = QPushButton("Request Status Data")
        self.request_button.clicked.connect(self.on_request_button_clicked)
        self.layout.addWidget(self.request_button)

        self.table_widget = QWidget()
        self.table_layout = QVBoxLayout()
        self.table_widget.setLayout(self.table_layout)
        self.layout.addWidget(self.table_widget)
        self.table_widget.hide()

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Parameter", "Value"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_layout.addWidget(self.table)

        self.create_aas_button = QPushButton("Create AAS")
        self.create_aas_button.clicked.connect(self.on_create_aas_clicked)
        self.table_layout.addWidget(self.create_aas_button)

        self.show_map_button = QPushButton("Show Map")
        self.show_map_button.clicked.connect(self.on_show_map_clicked)
        self.table_layout.addWidget(self.show_map_button)

        self.data_fetcher = DataFetcher()
        self.data_fetcher.dataFetched.connect(self.update_table)
        self.data_fetcher.dataFetched.connect(self.update_map_position)
        self.fetched_data = {}
        self.submodels = None
        self.property_selection = None

        self.map_panel = MapPanel()

        # Timer to update the HTML file
        self.html_update_timer = QTimer()
        self.html_update_timer.timeout.connect(self.update_html_file)  # Connect to update_html_file

    def on_request_button_clicked(self):
        self.table.setRowCount(0)
        self.table_widget.show()
        self.data_fetcher.start()
        self.html_update_timer.start(2000)  # Update HTML file every 2 seconds

    def update_table(self, data):
        self.fetched_data = data
        self.table.setRowCount(0)
        for i, (key, value) in enumerate(data.items()):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(key))
            self.table.setItem(i, 1, QTableWidgetItem(str(value)))
            self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

    def on_create_aas_clicked(self):
        dialog = AASConfigDialog(self.fetched_data)
        if dialog.exec_() == QDialog.Accepted:
            self.submodels = dialog.submodels
            self.property_selection = dialog.property_selection
            self.update_html_file()
            webbrowser.open('file://' + os.path.realpath("aas.html"))

    def update_html_file(self):
        self.create_html_file(self.submodels, self.property_selection)

    def create_html_file(self, submodels=None, property_selection=None):
        if submodels is None or property_selection is None:
            submodels = []
            property_selection = {}

        data = self.fetched_data

        # Create HTML content based on the selected structure
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AAS for MiR</title>
            <meta http-equiv="refresh" content="1"> <!-- Refresh every second -->
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 1200px;
                    margin: auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #333;
                    color: #fff;
                    padding: 10px;
                    text-align: center;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .box {{
                    background-color: #fff;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 10px;
                    margin-bottom: 10px;
                }}
                .box h3 {{
                    margin-top: 0;
                }}
                .box-content ul {{
                    list-style-type: none;
                    padding: 0;
                }}
                .box-content ul li {{
                    padding: 5px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>AAS for MiR</h1>
                </div>
                <div class="box">
                    <h3>Header</h3>
                    <div class="box-content">
                        <ul>
        """

        # Add Header properties to the HTML content
        for prop in property_selection.get('Header', []):
            html_content += f"<li>{prop}: {data.get(prop, 'N/A')}</li>"

        html_content += """
                        </ul>
                    </div>
                </div>
        """

        # Add each submodel to the HTML content
        for submodel in submodels:
            html_content += f"""
            <div class="box">
                <h3>{submodel}</h3>
                <div class="box-content">
                    <ul>
        """
            # Add properties to the submodel
            for prop in property_selection.get('Submodels', {}).get(submodel, []):
                html_content += f"<li>{prop}: {data.get(prop, 'N/A')}</li>"

            html_content += "</ul></div></div>"

        html_content += """
            </div>
        </body>
        </html>
        """

        with open("aas.html", "w") as file:
            file.write(html_content)

    def on_show_map_clicked(self):
        self.map_panel.show()

    def update_map_position(self, data):
        if 'position' in data:
            self.map_panel.update_position(data['position'])

class AASConfigDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure AAS Structure")

        self.data = data
        self.submodels = []
        self.property_selection = {'Header': [], 'Submodels': {}}

        self.init_ui()

    def init_ui(self):
        self.step1_layout = QVBoxLayout()
        self.setLayout(self.step1_layout)

        # Step 1: Number of submodels
        self.num_submodels_spinbox = QSpinBox()
        self.num_submodels_spinbox.setMinimum(1)
        self.num_submodels_spinbox.setMaximum(10)  # Limit to 10 submodels
        form_layout = QFormLayout()
        form_layout.addRow("Number of Submodels:", self.num_submodels_spinbox)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.show_step2)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.next_button)
        button_layout.addWidget(self.cancel_button)
        
        form_layout.addRow(button_layout)

        self.step1_layout.addLayout(form_layout)

    def show_step2(self):
        num_submodels = self.num_submodels_spinbox.value()

        self.step2_dialog = QDialog(self)
        self.step2_dialog.setWindowTitle("Enter Submodel Names")

        layout = QVBoxLayout()
        self.step2_dialog.setLayout(layout)

        form_layout = QFormLayout()
        layout.addLayout(form_layout)

        self.submodel_name_inputs = []
        for i in range(num_submodels):
            line_edit = QLineEdit()
            self.submodel_name_inputs.append(line_edit)
            form_layout.addRow(f"Submodel {i + 1} Name:", line_edit)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.show_step3)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.next_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)

        self.step2_dialog.setLayout(layout)
        self.step2_dialog.exec_()

    def show_step3(self):
        self.submodels = [input.text() for input in self.submodel_name_inputs]
        self.property_selection = {'Header': [], 'Submodels': {name: [] for name in self.submodels}}

        self.step3_dialog = QDialog(self)
        self.step3_dialog.setWindowTitle("Select Properties")

        layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        container_widget = QWidget()
        container_layout = QVBoxLayout()
        container_widget.setLayout(container_layout)
        scroll_area.setWidget(container_widget)
        layout.addWidget(scroll_area)

        self.step3_dialog.setLayout(layout)

        form_layout = QFormLayout()
        container_layout.addLayout(form_layout)

        # Header properties
        header_group_box = QGroupBox("Header")
        header_group_box_layout = QVBoxLayout()
        header_group_box.setLayout(header_group_box_layout)
        form_layout.addRow("Header", header_group_box)

        self.header_checkboxes = {}
        for prop in self.data.keys():
            checkbox = QCheckBox(prop)
            header_group_box_layout.addWidget(checkbox)
            self.header_checkboxes[prop] = checkbox

        # Submodel properties
        self.checkboxes = {}
        for submodel in self.submodels:
            group_box = QGroupBox(submodel)
            group_box_layout = QVBoxLayout()
            group_box.setLayout(group_box_layout)
            form_layout.addRow(submodel, group_box)

            for prop in self.data.keys():
                checkbox = QCheckBox(prop)
                group_box_layout.addWidget(checkbox)
                self.checkboxes[(submodel, prop)] = checkbox

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.finish)
        button_box.rejected.connect(self.reject)
        container_layout.addWidget(button_box)

        self.step3_dialog.exec_()

    def finish(self):
        # Save selected properties for Header
        self.property_selection['Header'] = [prop for prop, checkbox in self.header_checkboxes.items() if checkbox.isChecked()]
        # Save selected properties for each submodel
        for (submodel, prop), checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                self.property_selection['Submodels'].setdefault(submodel, []).append(prop)

        self.step3_dialog.accept()  # Close step 3 dialog
        self.step2_dialog.accept()  # Close step 2 dialog
        self.accept()  # Close step 1 dialog

class MapPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Map Panel")
        self.setGeometry(100, 100, 800, 600)
        self.position = None

    def paintEvent(self, event):
        painter = QPainter(self)
        self.draw_map(painter)

    def draw_map(self, painter):
        # Draw shopfloor
        shopfloor_width = 184
        shopfloor_height = 61
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawRect(50, 50, shopfloor_width, shopfloor_height)

        # Draw room
        room_width = 29
        room_height = 77
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawRect(50, 50, room_width, room_height)

        # Draw pentagon area
        pentagon_x1 = 50
        pentagon_y1 = 111
        pentagon_x2 = pentagon_x1 + 60.5
        pentagon_y2 = pentagon_y1 - 19
        pentagon_y3 = pentagon_y1 - 19 - 7

        painter.setPen(QPen(Qt.black, 2, Qt.DashLine))
        painter.drawLine(pentagon_x1, pentagon_y1, int(pentagon_x2), pentagon_y1)
        painter.drawLine(int(pentagon_x2), pentagon_y1, int(pentagon_x2), int(pentagon_y2))
        painter.drawLine(int(pentagon_x2), int(pentagon_y2), int(pentagon_x2 + 7), int(pentagon_y3))

        # Draw angled lines
        start_x = 79
        start_y = 50 + room_height
        line1_length = int(10 * 1.414)  # 45 degree line
        line2_length = 11
        line3_length = int(9 * 1.414)  # 45 degree line
        line4_length = 95

        painter.setPen(QPen(Qt.black, 2, Qt.DashLine))
        painter.drawLine(start_x, start_y, start_x + line1_length, start_y + line1_length)
        painter.drawLine(start_x + line1_length, start_y + line1_length, start_x + line1_length, start_y + line1_length + line2_length)
        painter.drawLine(start_x + line1_length, start_y + line1_length + line2_length, start_x + line1_length + line3_length, start_y + line1_length + line2_length + line3_length)
        painter.drawLine(start_x + line1_length + line3_length, start_y + line1_length + line2_length + line3_length, start_x + line1_length + line3_length + line4_length, start_y + line1_length + line2_length + line3_length)

        # Draw robot position
        if self.position:
            painter.setPen(QPen(Qt.red, 5, Qt.SolidLine))
            pos_x = 50 + self.position["x"]
            pos_y = 50 + shopfloor_height - self.position["y"]
            painter.drawPoint(pos_x, pos_y)

    def update_position(self, position):
        self.position = position
        self.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
