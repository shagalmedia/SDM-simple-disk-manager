import sys
import os
import psutil
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar
from PyQt5.QtCore import Qt, QTimer

def get_drives_info():
    drives = []
    for part in psutil.disk_partitions(all=False):
        disk_usage = psutil.disk_usage(part.mountpoint)
        drive_info = {
            "device": part.device,
            "mountpoint": part.mountpoint,
            "fstype": part.fstype,
            "used": disk_usage.used / (1024 ** 3), # В гигабайтах
            "total": disk_usage.total / (1024 ** 3), # В гигабайтах
            "percent": disk_usage.percent,
        }
        drives.append(drive_info)
    return drives

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(800, 500)
        self.setWindowTitle("Simple Disk Manager")

        self.layout = QVBoxLayout()

        self.refresh_button = QPushButton("Refresh", self)
        self.refresh_button.clicked.connect(self.update_table)
        self.layout.addWidget(self.refresh_button)

        self.access_label = QLabel(self)
        self.layout.addWidget(self.access_label)

        self.disks_table = QTableWidget(self)
        self.disks_table.setColumnCount(7)
        self.disks_table.setHorizontalHeaderLabels(["Device", "Mountpoint", "File System", "Used (GB)", "Total (GB)", "Used (%)", "Space"])
        self.disks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.layout.addWidget(self.disks_table)

        self.setLayout(self.layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_disk_access)
        self.timer.start(1000)  # Проверка доступа к диску каждую секунду

        self.disk_states = {}  # Состояния дисков (True - доступ, False - отключен)
        self.previous_disks = []  # Предыдущее состояние дисков

        self.update_table()

    def update_table(self):
        disks = get_drives_info()
        self.disks_table.setRowCount(len(disks))

        for i, disk in enumerate(disks):
            for j, key in enumerate(disk):
                if key in ["used", "total"]:
                    item = QTableWidgetItem("{:.2f}".format(disk[key])) # Отображение с двумя знаками после запятой
                elif key == "percent":
                    item = QTableWidgetItem("{:.1f}%".format(disk[key])) # Отображение с % и одним знаком после запятой
                else:
                    item = QTableWidgetItem(str(disk[key]))

                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.disks_table.setItem(i, j, item)

            # Добавление визуального отображения заполненности диска (спарклайн)
            progress_bar = QProgressBar(self.disks_table)
            progress_bar.setValue(int(disk["percent"]))
            self.disks_table.setCellWidget(i, len(disk), progress_bar)

    def check_disk_access(self):
        current_disks = get_drives_info()
        disk_accessed = False

        for disk in current_disks:
            device = disk["device"]
            if device in self.disk_states:
                if self.disk_states[device] != disk["used"]:
                    disk_accessed = True
                    self.disk_states[device] = disk["used"]
            else:
                self.disk_states[device] = disk["used"]

        if disk_accessed:
            self.show_disk_access_label()
        else:
            self.hide_disk_access_label()

        self.previous_disks = current_disks

    def show_disk_access_label(self):
        self.access_label.setText("Disk Access")
        self.access_label.setStyleSheet("background-color: green; color: white;")
        self.access_label.show()

    def hide_disk_access_label(self):
        self.access_label.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            selected_rows = self.disks_table.selectionModel().selectedRows()
            for row in reversed(selected_rows):
                self.disks_table.removeRow(row.row())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
