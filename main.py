from PyQt5.QtWidgets import QApplication

from src.app import App

if __name__ == "__main__":
    app = QApplication([])
    window = App()
    window.show()
    app.exec_()
