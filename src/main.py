import sqlite3
import sys

from book_searcher_ui import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog


class Book_Search(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.con = None
        self.db_connect.clicked.connect(self.db_connection)
        self.search_method.clicked.connect(self.search)
    
    def db_connection(self):
        db_name = QFileDialog.getOpenFileName(self, 'Выберите базу данных', '', '(*.db);;(*.sqlite3)')[0]
        self.con = sqlite3.connect(db_name)
    
    def search(self):
        pass

if __name__ == "__main__":
    app = QApplication([])
    w = Book_Search()
    w.show()
    app.exec()