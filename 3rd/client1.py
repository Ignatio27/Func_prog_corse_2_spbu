import sys
import os
import socket
from threading import Thread
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox, QLabel, QDialog, QFormLayout, QHBoxLayout, QInputDialog, QFileDialog
)
from PyQt5.QtCore import pyqtSignal, QObject


class Client(QObject):
    message_received = pyqtSignal(str)
    file_received = pyqtSignal(str, bytes)
    connection_lost = pyqtSignal()

    def __init__(self, host, port, name, room):
        super().__init__()
        self.host = host
        self.port = port
        self.name = name
        self.room = room
        self.socket = None

    def connect(self):
        try:
            self.socket = socket.socket()
            self.socket.connect((self.host, self.port))
            self.join_room(self.room)
            Thread(target=self.listen_for_messages, daemon=True).start()
        except Exception as e:
            QMessageBox.critical(None, "Connection Error", f"Could not connect to server: {e}")
            self.connection_lost.emit()

    def listen_for_messages(self):
        try:
            while True:
                message = self.socket.recv(1024).decode(errors="ignore")
                if not message:
                    break

                if message.startswith("/file"):
                    file_name = message.split(" ", 1)[-1].strip()
                    file_data = b""
                    while True:
                        chunk = self.socket.recv(1024)
                        if chunk.endswith(b"<EOF>"):
                            file_data += chunk[:-5]
                            break
                        file_data += chunk
                    self.file_received.emit(file_name, file_data)
                else:
                    self.message_received.emit(message)
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            self.connection_lost.emit()

    def join_room(self, room):
        try:
            self.room = room
            self.socket.send(f"/join {room}\n".encode())
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Could not join room: {e}")

    def send_message(self, message):
        try:
            formatted_message = f"{self.name}: {message}"
            self.socket.send(formatted_message.encode())
        except Exception as e:
            print(f"[ERROR] Could not send message: {e}")

    def send_file(self, file_path):
        try:
            file_name = os.path.basename(file_path)
            self.socket.send(f"/sendfile {file_name}\n".encode())
            with open(file_path, "rb") as f:
                while chunk := f.read(1024):
                    self.socket.send(chunk)
            self.socket.send(b"<EOF>")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Could not send file: {e}")

    def disconnect(self):
        if self.socket:
            self.socket.close()


class ChatWindow(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.client = client

        self.setWindowTitle(f"Chat Client - Room: {self.client.room}")
        self.resize(600, 400)

        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)

        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.send_message)

        self.send_file_button = QPushButton("Send File", self)
        self.send_file_button.clicked.connect(self.send_file)

        self.change_room_button = QPushButton("Change Room", self)
        self.change_room_button.clicked.connect(self.change_room)

        self.exit_button = QPushButton("Exit", self)
        self.exit_button.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self.chat_display)
        layout.addWidget(self.input_field)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.send_file_button)
        button_layout.addWidget(self.change_room_button)
        button_layout.addWidget(self.exit_button)

        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.client.message_received.connect(self.display_message)
        self.client.file_received.connect(self.save_file)
        self.client.connection_lost.connect(self.handle_disconnection)

    def display_message(self, message):
        if not message.startswith("Other User:"):
            self.chat_display.append(message)

    def send_message(self):
        message = self.input_field.text().strip()
        if message:
            self.client.send_message(message)
            self.chat_display.append(f"{self.client.name}: {message}")
            self.input_field.clear()

    def send_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            try:
                self.client.send_file(file_path)
                self.chat_display.append(f"[INFO] Sent file: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not send file: {e}")

    def save_file(self, file_name, file_data):
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", file_name)
        if save_path:
            try:
                with open(save_path, "wb") as f:
                    f.write(file_data)
                self.chat_display.append(f"[INFO] File saved as: {save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {e}")

    def change_room(self):
        new_room, ok = QInputDialog.getText(self, "Change Room", "Enter new room name:")
        if ok and new_room.strip():
            self.client.join_room(new_room.strip())
            self.chat_display.append(f"[INFO] Switched to room: {new_room.strip()}")

    def handle_disconnection(self):
        QMessageBox.warning(self, "Disconnected", "The connection to the server was lost.")
        self.close()

    def closeEvent(self, event):
        self.client.disconnect()
        event.accept()


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login to Chat")
        self.resize(300, 200)

        self.name_field = QLineEdit(self)
        self.name_field.setPlaceholderText("Enter your name")

        self.room_field = QLineEdit(self)
        self.room_field.setPlaceholderText("Enter room name")

        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)

        layout = QFormLayout()
        layout.addRow("Name:", self.name_field)
        layout.addRow("Room:", self.room_field)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)

    def get_inputs(self):
        return self.name_field.text().strip(), self.room_field.text().strip()


def main():
    app = QApplication(sys.argv)

    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.Accepted:
        name, room = login_dialog.get_inputs()
        if not name or not room:
            QMessageBox.critical(None, "Error", "Name and Room cannot be empty!")
            sys.exit()

        host = "127.0.0.1"
        port = 5002
        client = Client(host, port, name, room)
        chat_window = ChatWindow(client)

        client.connect()
        chat_window.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()
