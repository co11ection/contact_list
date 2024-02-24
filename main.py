import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QListWidget, QMessageBox, QInputDialog)

# Создание базы данных SQLite и таблицы контактов
conn = sqlite3.connect('contacts.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             email TEXT,
             password TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS contacts
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             user_id INTEGER,
             name TEXT,
             phone TEXT,
             email TEXT,
             FOREIGN KEY (user_id) REFERENCES users(id))''')
conn.commit()

class ContactManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Менеджер контактов')
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.init_ui()
        self.logged_in_user_id = None

    def init_ui(self):
        # Registration and Login UI
        self.email_input_login = QLineEdit()
        self.password_input_login = QLineEdit()
        self.password_input_login.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton('Вход')
        self.register_button = QPushButton('Регистрация')

        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)

        self.layout.addWidget(QLabel('Email (для входа):'))
        self.layout.addWidget(self.email_input_login)
        self.layout.addWidget(QLabel('Пароль:'))
        self.layout.addWidget(self.password_input_login)
        self.layout.addWidget(self.login_button)
        self.layout.addWidget(self.register_button)

        # Contact management UI (hidden initially)
        self.contact_layout = QVBoxLayout()
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.add_button = QPushButton('Добавить контакт')
        self.search_input = QLineEdit()
        self.search_button = QPushButton('Искать контакт')
        self.contact_list = QListWidget()
        self.delete_button = QPushButton('Удалить контакт')
        self.update_button = QPushButton('Обновить контакт')

        self.add_button.clicked.connect(self.add_contact)
        self.search_button.clicked.connect(self.search_contact)
        self.delete_button.clicked.connect(self.delete_contact)
        self.update_button.clicked.connect(self.update_contact)

        self.contact_layout.addWidget(QLabel('Имя:'))
        self.contact_layout.addWidget(self.name_input)
        self.contact_layout.addWidget(QLabel('Телефон:'))
        self.contact_layout.addWidget(self.phone_input)
        self.contact_layout.addWidget(QLabel('Email:'))
        self.contact_layout.addWidget(self.email_input)
        self.contact_layout.addWidget(self.add_button)
        self.contact_layout.addWidget(QLabel('Поиск:'))
        self.contact_layout.addWidget(self.search_input)
        self.contact_layout.addWidget(self.search_button)
        self.contact_layout.addWidget(self.contact_list)
        self.contact_layout.addWidget(self.delete_button)
        self.contact_layout.addWidget(self.update_button)
        self.contact_layout.setEnabled(False)
        self.layout.addLayout(self.contact_layout)

    def register(self):
        email, ok = QInputDialog.getText(self, "Регистрация", "Введите ваш email:")
        if not ok:
            return

        password, ok = QInputDialog.getText(self, "Регистрация", "Введите пароль:")
        if not ok:
            return

        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        QMessageBox.information(self, 'Успех', 'Вы успешно зарегистрированы!')

    def login(self):
        email = self.email_input_login.text()
        password = self.password_input_login.text()

        c.execute("SELECT id FROM users WHERE email = ? AND password = ?", (email, password))
        user = c.fetchone()
        if user:
            self.logged_in_user_id = user[0]
            self.contact_layout.setEnabled(True)
            self.refresh_contact_list()
            QMessageBox.information(self, 'Успех', 'Вы успешно вошли в систему!')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Неправильный email или пароль!')


    def add_contact(self):
        name = self.name_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()
        if name and phone:
            c.execute("INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)", (name, phone, email))
            conn.commit()
            self.refresh_contact_list()
            self.clear_input_fields()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Имя и телефон обязательны для заполнения!')

    def search_contact(self):
        keyword = self.search_input.text()
        c.execute("SELECT * FROM contacts WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?", ('%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%'))
        contacts = c.fetchall()
        self.contact_list.clear()
        for contact in contacts:
            self.contact_list.addItem(f"Имя: {contact[1]}, Телефон: {contact[2]}, Email: {contact[3]}")

    def refresh_contact_list(self):
        c.execute("SELECT * FROM contacts")
        contacts = c.fetchall()
        self.contact_list.clear()
        for contact in contacts:
            print(contact)
            self.contact_list.addItem(f"Имя: {contact[2]}, Телефон: {contact[3]}, Email: {contact[4]}")
            
    
    def delete_contact(self):
        selected_items = self.contact_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Ошибка', 'Выберите контакт для удаления!')
            return

        selected_item = selected_items[0]
        contact_info = selected_item.text()
        name = contact_info.split(',')[0].split(': ')[1]
        c.execute("DELETE FROM contacts WHERE name = ?", (name,))
        conn.commit()
        self.refresh_contact_list()

    def update_contact(self):
        selected_items = self.contact_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Ошибка', 'Выберите контакт для обновления!')
            return

        selected_item = selected_items[0]
        contact_info = selected_item.text()
        name, phone, email = (
            contact_info.split(',')[0].split(': ')[1],
            contact_info.split(',')[1].split(': ')[1],
            contact_info.split(',')[2].split(': ')[1]
        )

        new_name, ok = QInputDialog.getText(self, "Введите новое имя", "Новое имя:")
        if not ok:
            return

        new_phone, ok = QInputDialog.getText(self, "Введите новый телефон", "Новый телефон:")
        if not ok:
            return

        new_email, ok = QInputDialog.getText(self, "Введите новый email", "Новый email:")
        if not ok:
            return

        c.execute("UPDATE contacts SET name = ?, phone = ?, email = ? WHERE name = ?", (new_name, new_phone, new_email, name))
        conn.commit()
        self.refresh_contact_list()

    def clear_input_fields(self):
        self.name_input.clear()
        self.phone_input.clear()
        self.email_input.clear()

if __name__ == '__main__':
    app = QApplication([])
    window = ContactManager()
    window.show()
    app.exec_()
