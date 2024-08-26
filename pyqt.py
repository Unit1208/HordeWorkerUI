from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QPushButton,
    QMessageBox,
    QScrollArea,
    QGroupBox,
    QDialog,
    QProgressBar,
)
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread, pyqtSignal
import keyring
import requests
from http import HTTPStatus

ANON_API_KEY = "0000000000"
BASE_URL = "https://aihorde.net/api/v2/"


class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Loading...")
        self.setWindowModality(Qt.ApplicationModal)
        layout = QVBoxLayout()
        self.label = QLabel("Please wait...")
        layout.addWidget(self.label)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(self.progress)
        self.setLayout(layout)
        self.setFixedSize(300, 100)


class WorkerThread(QThread):
    user_info_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key

    def run(self):
        try:
            r = requests.get(
                BASE_URL + "find_user",
                headers={
                    "apikey": self.api_key,
                    "Client-Agent": "HordeWorkerManager:0.1.0:Unit1208",
                },
            )
            if r.status_code == HTTPStatus.NOT_FOUND:
                self.error_signal.emit(
                    "User not found. You may register at https://aihorde.net/register"
                )
                return
            self.user_info_signal.emit(r.json())
        except Exception as e:
            self.error_signal.emit(f"An error occurred: {str(e)}")


class WorkerInfo(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(2)
        self.setHeaderLabels(["Attribute", "Value"])
        self.setColumnWidth(0, 200)
        self.setColumnWidth(1, 400)

    def updatevals(self, value: dict):
        self.clear()
        items = [
            ("Worker Name", value.get("name", "")),
            ("Worker ID", value.get("id", "")),
            ("Online", "Yes" if value.get("online", False) else "No"),
            ("Requests Fulfilled", str(value.get("requests_fulfilled", ""))),
            ("Kudos Rewards", str(value.get("kudos_rewards", ""))),
            (
                "Kudos Generated",
                str(value.get("kudos_details", {}).get("generated", "")),
            ),
            ("Kudos Uptime", str(value.get("kudos_details", {}).get("uptime", ""))),
            ("Performance", value.get("performance", "")),
            ("Threads", str(value.get("threads", ""))),
            ("Uptime", str(value.get("uptime", ""))),
            (
                "Maintenance Mode",
                "Yes" if value.get("maintenance_mode", False) else "No",
            ),
            ("NSFW", "Yes" if value.get("nsfw", False) else "No"),
            ("Trusted", "Yes" if value.get("trusted", False) else "No"),
            ("Flagged", "Yes" if value.get("flagged", False) else "No"),
            ("Uncompleted Jobs", str(value.get("uncompleted_jobs", ""))),
            ("Models", ", ".join(value.get("models", []))),
            (
                "Team",
                f"{value.get('team', {}).get('name', 'N/A')} (ID: {value.get('team', {}).get('id', 'N/A')})",
            ),
            ("Bridge Agent", value.get("bridge_agent", "")),
            ("Max Pixels", str(value.get("max_pixels", ""))),
            (
                "Megapixelsteps Generated",
                str(value.get("megapixelsteps_generated", "")),
            ),
            ("Img2Img", "Yes" if value.get("img2img", False) else "No"),
            ("Painting", "Yes" if value.get("painting", False) else "No"),
            ("Post-Processing", "Yes" if value.get("post-processing", False) else "No"),
            ("LoRA", "Yes" if value.get("lora", False) else "No"),
            ("ControlNet", "Yes" if value.get("controlnet", False) else "No"),
            ("SDXL ControlNet", "Yes" if value.get("sdxl_controlnet", False) else "No"),
            ("Type", value.get("type", "")),
        ]

        for item in items:
            QTreeWidgetItem(self, item)


class UserInfo(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("User Info", parent)
        layout = QFormLayout()

        self.username = QLabel()
        layout.addRow("Username:", self.username)

        self.user_id = QLabel()
        layout.addRow("ID:", self.user_id)

        self.kudos = QLabel()
        layout.addRow("Kudos:", self.kudos)

        self.workers = QLabel()
        layout.addRow("Workers:", self.workers)

        self.trusted = QLabel()
        layout.addRow("Trusted:", self.trusted)

        self.concurrency = QLabel()
        layout.addRow("Concurrency:", self.concurrency)

        self.setLayout(layout)

    def updatevals(self, value: dict):
        self.username.setText(value.get("username", ""))
        self.user_id.setText(str(value.get("id", "")))
        self.kudos.setText(str(value.get("kudos", "")))
        self.workers.setText(str(value.get("worker_count", "")))
        self.trusted.setText("Yes" if value.get("trusted", False) else "No")
        self.concurrency.setText(str(value.get("concurrency", "")))


class App(QWidget):
    def __init__(self):
        super().__init__()

        self.service_name = (
            "AIHordeWorkerManager"  # A unique name for your application in the keyring
        )
        self.api_key = (
            keyring.get_password(self.service_name, "api_key") or ANON_API_KEY
        )

        self.setWindowTitle("AI Horde Worker Manager")
        self.setGeometry(300, 100, 800, 600)

        layout = QVBoxLayout()

        self.api_key_entry = QLineEdit()
        self.api_key_entry.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        self.api_key_entry.setPlaceholderText("Enter API Key and press Enter")
        self.api_key_entry.returnPressed.connect(self.enter_key)
        layout.addWidget(self.api_key_entry)

        if self.api_key != ANON_API_KEY:
            self.api_key_entry.setText(self.api_key)
        self.user_info = UserInfo()
        layout.addWidget(self.user_info)

        self.workers_area = QScrollArea()
        self.workers_area.setWidgetResizable(True)

        self.workers_widget = QWidget()
        self.workers_layout = QVBoxLayout()
        self.workers_widget.setLayout(self.workers_layout)
        self.workers_area.setWidget(self.workers_widget)

        layout.addWidget(self.workers_area)

        self.setLayout(layout)

    def enter_key(self):
        api_key = self.api_key_entry.text()
        if api_key == "":
            self.show_error("Must provide an API key.")
            return
        if api_key == ANON_API_KEY:
            self.show_error(f"Anonymous ({ANON_API_KEY}) can't run workers")
            return

        # If user enters a new API key, save it to keyring
        if api_key != self.api_key:
            keyring.set_password(self.service_name, "api_key", api_key)
            self.api_key = api_key

        # Show loading dialog
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()

        # Start the thread to fetch user info
        self.worker_thread = WorkerThread(self.api_key)
        self.worker_thread.user_info_signal.connect(self.handle_user_info)
        self.worker_thread.error_signal.connect(self.show_error)
        self.worker_thread.finished.connect(self.loading_dialog.close)
        self.worker_thread.start()

    def handle_user_info(self, user_info):
        self.user_info.updatevals(user_info)
        for i in reversed(range(self.workers_layout.count())):
            widget_to_remove = self.workers_layout.itemAt(i).widget()
            self.workers_layout.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()

        for worker in user_info["worker_ids"]:
            worker_deets = requests.get(BASE_URL + "workers/" + worker)
            if worker_deets.status_code == HTTPStatus.NOT_FOUND:
                self.show_error("Invalid worker id. This shouldn't happen.")
                continue
            worker_info = WorkerInfo()
            worker_info.updatevals(worker_deets.json())
            self.workers_layout.addWidget(worker_info)

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)


if __name__ == "__main__":
    app = QApplication([])
    window = App()
    window.show()
    app.exec_()
