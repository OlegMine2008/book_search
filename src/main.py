import sqlite3
import sys

from book_searcher_ui import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QInputDialog
from PyQt6.QtSql import QSqlQueryModel


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
    
    # def search(self):
    #     cur = self.con.cursor()
    #     methode, ok_pressed = QInputDialog.getItem(self, "Поиск", "Выберите метод поиска", ("Код", "Название", "Автор"), 1, False)
    #     if ok_pressed and methode == 'Код':
    #         info, new_pressed = QInputDialog.getText(self, "Поиск по коду", "Введите код книги")
    #         if new_pressed:
    #             model = QSqlQueryModel()
    #             model.setQuery('SELECT * FROM ')
    #             self.tableView.setModel(f'SELECT * FROM {}')
    #     elif ok_pressed and methode == 'Название':
    #         info, new_pressed = QInputDialog.getText(self, "Поиск по названию", "Введите название книги")
    #     elif ok_pressed and methode == 'Автор':
    #         info, new_pressed = QInputDialog.getText(self, "Поиск по автору", "Введите имя автора")


if __name__ == "__main__":
    app = QApplication([])
    w = Book_Search()
    w.show()
    app.exec()