import sqlite3
import sys

from book_searcher_ui import Ui_MainWindow
from asking_ui import Ui_Form
from adding_with_new_ui import Ui_Dialog
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QDialog, QMessageBox, QInputDialog
from PyQt6.QtSql import QSqlQueryModel
from adding_ui import Ui_Dialog_2


class Book_Search(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.con = None
        self.db_connect.clicked.connect(self.db_connection)
        # self.search_method.clicked.connect(self.search)
        self.add_book.clicked.connect(self.new_book)
        self.update_info.clicked.connect(self.update_infor)
        self.delete_book.clicked.connect(self.delete)

    def db_connection(self):
        db_name = QFileDialog.getOpenFileName(self, 'Выберите базу данных', '', '(*.db);;(*.sqlite3)')[0]
        if db_name:
            self.con = sqlite3.connect(db_name)
    
    def new_book(self):
        if not self.con:
            QMessageBox.warning(self, "Ошибка", "Сначала подключите базу данных")
            return
        
        cur = self.con.cursor()
        author_id = cur.execute('''SELECT author_id, (SELECT author_name FROM authors WHERE id == author_id) 
                                FROM books''').fetchall()
        
        if not author_id:
            QMessageBox.warning(self, "Ошибка", "База данных пуста")
            return
        
        author_id = [f"{author_cur_id}, {name}" for author_cur_id, name in author_id]
        author_id.append('Новый автор')
        author, ok_pressed = QInputDialog.getItem(self, "Выбор", "Выберите автора или введите нового", author_id, 0, False)
        if ok_pressed:
            if author == 'Новый автор':
                u = Adding_Window_new(cur, self)
                u.exec()
                self.con.commit()
            else:
                auth_id = int(author.split(',')[0].strip())
                u = Adding_Window(cur, self, auth_id)
                u.exec()
                self.con.commit()

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
        
    def delete(self):
        if not self.con:
            QMessageBox.warning(self, "Ошибка", "Сначала подключите базу данных")
            return
    
        cur = self.con.cursor()
        choose, ok_got = QInputDialog.getItem(self, "Выбор", "Выберите, что хотите удалить", ['Автора', 'Книгу'], 0, False)
        if ok_got and choose == 'Книгу':
            operate, ok_pressed = QInputDialog.getText(self, 'Удаление', 'Введите id книги, которую хотите удалить')
            if ok_pressed:
                try:
                    cur.execute('''DELETE FROM books WHERE id == ?''', (int(operate),))
                    cur.execute('''UPDATE books
                                SET id == id - 1
                                WHERE id > ?''', (int(operate),))
                    self.con.commit()
                except ValueError:
                    QMessageBox.warning(self, 'Ошибка', 'Вы должны ввести id в виде числа, а не навзание книги или чего либо другого')
        elif ok_got and choose == 'Автора':
            operate, ok_pressed = QInputDialog.getText(self, 'Удаление', 'Введите имя автора, которого хотите удалить')
            if ok_pressed:
                if operate.isalpha():
                    check = list(cur.execute('''SELECT book_name FROM books WHERE author_id == (
                                SELECT id FROM authors WHERE author_name == ?)''', (operate,)))
                    if check:
                        message = 'Вы не можете удалить автора, если в базе данных есть его книги: ' + ''.join(map(str, check))
                        QMessageBox.warning(self, 'Ошибка', message)
                    else:
                        cur.execute('''DELETE FROM authors WHERE author_name == ?''', (operate,))
                        cur.execute('''UPDATE books
                                    SET id == id - 1
                                    WHERE id > ?''', (operate,))
                        self.con.commit()
                else:
                    QMessageBox.warning(self, 'Ошибка', 'Имя автора должно состоять из букв')


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


class Adding_Window_new(QDialog, Ui_Dialog):
    def __init__(self, cursor, main=None):
        super().__init__(main)
        self.setupUi(self)
        self.cur = cursor
        
        self.sureButton.clicked.connect(self.approve)
    
    def approve(self):
        name = self.author_name.toPlainText()
        book = self.book_name.toPlainText()
        info_result = self.information.toPlainText()
        notes_result = self.notes.toPlainText()
        
        self.cur.execute('''INSERT INTO authors(author_name)
                         VALUES(?)''', 
                    (name,))
        self.cur.execute('''INSERT INTO books(book_name, info, notes, author_id)
                         VALUES(?, ?, ?, (SELECT id FROM authors
                         WHERE author_name == ?))''', 
                    (book, info_result, notes_result, name))
            
        self.accept()


class Adding_Window(QDialog, Ui_Dialog_2):
    def __init__(self, cursor, main=None, auth=None):
        super().__init__(main)
        self.setupUi(self)
        self.cur = cursor
        self.auth_id = auth
        
        self.pushButton.clicked.connect(self.approve)
                
    def approve(self):
        book = self.book_name.toPlainText()
        info_result = self.info.toPlainText()
        notes_result = self.notes.toPlainText()
        
        self.cur.execute('''INSERT INTO books(book_name, info, notes, author_id)
                         VALUES(?, ?, ?, ?)''', 
                    (book, info_result, notes_result, self.auth_id))
            
        self.accept()


if __name__ == "__main__":
    app = QApplication([])
    w = Book_Search()
    w.show()
    app.exec()