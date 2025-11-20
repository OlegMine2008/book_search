from data.book_searcher_ui import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow, QApplication


class Book_Search(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == "__main__":
    app = QApplication([])
    w = Book_Search()
    w.show()
    app.exec()