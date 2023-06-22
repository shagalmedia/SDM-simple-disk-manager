import sys
import os
import psutil
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QMovie

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

class DiskAccessThread(QThread):
    access_started = pyqtSignal()
    access_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        # Имитация доступа к диску на протяжении 3 секунд
        self.access_started.emit()
        self.sleep(3)
        self.access_finished.emit()

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
        self.timer.timeout.connect(self.update_table)
        self.timer.start(5000)  # Обновление таблицы каждые 5 секунд

        self.disk_access_thread = DiskAccessThread()
        self.disk_access_thread.access_started.connect(self.show_disk_access_label)
        self.disk_access_thread.access_finished.connect(self.hide_disk_access_label)

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

    def show_disk_access_label(self):
        self.access_label.setText("Accessing Disk...")
        movie = QMovie("loader.gif")
        self.access_label.setMovie(movie)
        movie.start()
        self.access_label.show()

    def hide_disk_access_label(self):
        self.access_label.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            selected_rows = self.disks_table.selectionModel().selectedRows()
            for row in reversed(selected_rows):
                self.disks_table.removeRow(row.row())
        elif event.key() == Qt.Key_Space:
            self.disk_access_thread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
