import sqlite3
import sys

from book_searcher_ui import Ui_MainWindow
from asking_ui import Ui_Form
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QDialog, QMessageBox, QInputDialog
from PyQt6.QtSql import QSqlQueryModel


class Book_Search(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.con = None
        self.db_connect.clicked.connect(self.db_connection)
        # self.search_method.clicked.connect(self.search)
        # self.add_book.clicked.connect(self.new_book)
        self.update_info.clicked.connect(self.update_infor)

    def db_connection(self):
        db_name = QFileDialog.getOpenFileName(self, 'Выберите базу данных', '', '(*.db);;(*.sqlite3)')[0]
        self.con = sqlite3.connect(db_name)
    
    # def new_book(self):
    #     cur = self.con.cursor()

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

    def update_infor(self):
        if not self.con:
            QMessageBox.warning(self, "Ошибка", "Сначала подключите базу данных")
            return
    
        cur = self.con.cursor()
    
        books_data = cur.execute('''SELECT id, book_name, 
                               (SELECT author_name FROM authors WHERE id == author_id) 
                               FROM books''').fetchall()
    
        if not books_data:
            QMessageBox.warning(self, "Ошибка", "База данных пуста")
            return
    
        book_items = [f"{book_id}, {book_name}, {author}" for book_id, book_name, author in books_data]
    
        book, ok_pressed = QInputDialog.getItem(
            self, "Выбор", "Выберите книгу", book_items, 0, False
        )
    
        if ok_pressed and book:
            selected_id = int(book.split(',')[0].strip())
            u = Asking_Window(cur, self, selected_id)
            u.exec()
            self.con.commit()


class Asking_Window(QDialog, Ui_Form):
    def __init__(self, cursor, main=None, book_id=None):
        super().__init__(main)
        self.setupUi(self)
        self.cur = cursor
        self.book_id = book_id
        
        all_info = list(self.cur.execute(f'''SELECT info, notes FROM books 
                                       WHERE id == {self.book_id}'''))
        self.inform.setPlainText(all_info[0][0])
        self.notes.setPlainText(all_info[0][1])
        
        self.sure_button.clicked.connect(self.approve)
                
    
    def approve(self):
        info_result = self.inform.toPlainText()
        notes_result = self.notes.toPlainText()
        
        self.cur.execute('''UPDATE books 
                         SET info = ?, notes = ? 
                         WHERE id == ?''', 
                    (info_result, notes_result, self.book_id))
            
        self.accept()
        

if __name__ == "__main__":
    app = QApplication([])
    w = Book_Search()
    w.show()
    app.exec()