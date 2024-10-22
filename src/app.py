import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QTextEdit, QVBoxLayout, QWidget, QFileDialog, QHBoxLayout
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QObject
import threading
import sys
import time  # Import time module for start timestamp
from src.services import watch_folder
import json  # For saving the selected folder path

class Communicate(QObject):
    log_message_signal = pyqtSignal(str)
    update_status_signal = pyqtSignal(str, QColor)


class App(QMainWindow):
    CONFIG_FILE = "config.json"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Class Watcher")
        self.setGeometry(300, 300, 500, 400)

        # Central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Title label
        self.title = QLabel("Class Watcher", self)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.title)

        # Status label
        self.status_label = QLabel("Status: Not Watching", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.update_status("Not Watching", QColor("gray"))
        layout.addWidget(self.status_label)

        # Horizontal layout for selected folder label and select button
        folder_layout = QHBoxLayout() # Align items to the center vertically and to the left

        # Selected folder label
        self.selected_folder_label = QLabel("No folder selected", self)
        self.selected_folder_label.setAlignment(Qt.AlignLeft)
        self.selected_folder_label.setStyleSheet("font-size: 12px; color: gray;")  # Smaller and gray text
        folder_layout.addWidget(self.selected_folder_label)

        # Select folder button
        self.select_folder_button = QPushButton("Select Folder", self)
        self.select_folder_button.setFixedSize(100, 30)  # Set fixed size for the button
        self.select_folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.select_folder_button)

        folder_layout.addStretch()  # Add stretchable space to push items to the top
        folder_layout.setAlignment(Qt.AlignBottom)
        layout.addLayout(folder_layout)

        # Start/Stop listening button
        self.listen_button = QPushButton("Start Listening", self)
        self.listen_button.clicked.connect(self.toggle_listening)
        self.listen_button.setEnabled(False)  # Initially disabled
        layout.addWidget(self.listen_button)

        # Log area
        self.log_area = QTextEdit(self)
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        self.setCentralWidget(central_widget)

        # Initialize communication signals
        self.comm = Communicate()
        self.comm.log_message_signal.connect(self.log_message)
        self.comm.update_status_signal.connect(self.update_status)

        # Variables to track state
        self.start_time = time.time()
        self.is_listening = False
        self.folder_path = None
        self.thread = None
        self.stop_event = threading.Event()  # Event to signal the thread to stop

        # Load folder path from config
        self.load_folder_path()

    def select_folder(self):
        """Open a dialog to select a folder."""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.folder_path = folder_path
            self.save_folder_path(folder_path)  # Save the selected folder
            self.listen_button.setEnabled(True)
            self.selected_folder_label.setText(f"Selected folder: {folder_path}")  # Update label text
            self.log_message(f"Selected folder: {folder_path}")

    def toggle_listening(self):
        """Start or stop listening based on the current state."""
        if self.folder_path is None:
            self.log_message("Please select a folder first.")
            return

        if self.is_listening:
            self.is_listening = False
            self.listen_button.setText("Start Listening")
            self.update_status("Not Watching", QColor("gray"))
            self.log_message("Stopping listening...")

            self.stop_event.set()  # Signal the thread to stop
            # Wait for the thread to finish without blocking the GUI
            if self.thread is not None:
                self.thread.join(timeout=1)  # Join with a timeout
                if self.thread.is_alive():
                    self.log_message("Stopping listening...")
                self.thread = None

            self.log_message("Stopped listening.")
            self.stop_event.clear()  # Clear the stop event for future use
        else:
            self.is_listening = True
            self.listen_button.setText("Stop Listening")
            self.update_status("Watching...", QColor("green"))
            self.log_message(f"Watching folder: {self.folder_path} for audio files...")
            self.stop_event.clear()  # Clear the stop event
            self.thread = threading.Thread(target=watch_folder,
                                           args=(self.folder_path, self.stop_event, self.comm, self.start_time),
                                           daemon=True)
            self.thread.start()

    def update_status(self, status, color):
        """Update the status label with the given status and color."""
        self.status_label.setText(f"Status: {status}")
        palette = self.status_label.palette()
        palette.setColor(QPalette.WindowText, color)
        self.status_label.setPalette(palette)

    def log_message(self, message):
        """Add a message to the log area."""
        self.log_area.append(message)

    def save_folder_path(self, path):
        """Save the selected folder path to a configuration file."""
        with open(self.CONFIG_FILE, 'w') as config_file:
            json.dump({"folder_path": path}, config_file)

    def load_folder_path(self):
        """Load the folder path from a configuration file if it exists."""
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r') as config_file:
                config = json.load(config_file)
                self.folder_path = config.get("folder_path")
                if self.folder_path:
                    self.listen_button.setEnabled(True)  # Enable listening button if a folder is loaded
                    self.log_message(f"Loaded folder: {self.folder_path}")
                    self.selected_folder_label.setText(f"Selected folder: {self.folder_path}")  # Update label text


