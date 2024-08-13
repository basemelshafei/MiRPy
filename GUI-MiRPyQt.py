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
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon

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

        self.data_fetcher = DataFetcher()
        self.data_fetcher.dataFetched.connect(self.update_table)
        self.fetched_data = {}
        self.submodels = None
        self.property_selection = None

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


        for prop in property_selection.get('Header', []):
            html_content += f"<li>{prop}: {data.get(prop, 'N/A')}</li>"

        html_content += """
                        </ul>
                    </div>
                </div>
        """

        for submodel in submodels:
            html_content += f"""
            <div class="box">
                <h3>{submodel}</h3>
                <div class="box-content">
                    <ul>
        """

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
