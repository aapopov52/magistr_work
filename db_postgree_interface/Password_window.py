import sys
import function_use
from PyQt5.QtWidgets import (QApplication, QDialog, QFormLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QVBoxLayout, QMessageBox, QCheckBox, QWidget)

class ConnectionParametersDialog(QDialog):
    def __init__(self, params):
        super().__init__()
        self.setWindowTitle("Параметры подключения")
        self.connection_params = None  # Здесь будут сохранены данные соединения
        self.params = params
        self.init_ui()
    
    
    def init_ui(self):
        # Создаем поля ввода
        self.dbname_edit = QLineEdit(self)
        self.user_edit = QLineEdit(self)
        self.password_edit = QLineEdit(self)
        self.host_edit = QLineEdit(self)
        self.port_edit = QLineEdit(self)
        self.table_main_shema_edit = QLineEdit(self)
        
        # Скрываем символы пароля
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setText(function_use.decrypt_data(self.params['password']).decode('utf-8'))
        
        # Значения по умолчанию (если нужно)
        self.dbname_edit.setText(self.params['dbname'])
        self.user_edit.setText(self.params['user'])
        self.host_edit.setText(self.params['host'])
        self.port_edit.setText(str(self.params['port']))
        self.table_main_shema_edit.setText(self.params['table_main_shema'])
        
        # Чекбокс "Сохранить пароль"
        self.save_password_checkbox = QCheckBox("Сохранить пароль", self)
        self.save_password_checkbox.setChecked(self.params['save_password'])

        # Компоновка формы
        form_layout = QFormLayout()
        form_layout.addRow("База данных:", self.dbname_edit)
        form_layout.addRow("Пользователь (логин):", self.user_edit)
        
        # Размещаем поле пароля и чекбокс в одном ряду
        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_edit)
        password_layout.addWidget(self.save_password_checkbox)
        password_widget = QWidget()
        password_widget.setLayout(password_layout)
        
        form_layout.addRow("Пароль:", password_widget)
        form_layout.addRow("Хост:", self.host_edit)
        form_layout.addRow("Порт:", self.port_edit)
        form_layout.addRow("Схема для таблиц с параметрами:", self.table_main_shema_edit)

        # Кнопка для подключения
        self.connect_button = QPushButton("Подключиться", self)
        self.connect_button.clicked.connect(self.on_connect)

        # Основная компоновка
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.connect_button)

        self.setLayout(main_layout)
        
        self.setTabOrder(self.dbname_edit, self.user_edit)
        self.setTabOrder(self.user_edit, self.password_edit)
        self.setTabOrder(self.password_edit, self.save_password_checkbox)
        self.setTabOrder(self.save_password_checkbox, self.host_edit)
        self.setTabOrder(self.host_edit, self.port_edit)
        self.setTabOrder(self.port_edit, self.table_main_shema_edit)
        self.setTabOrder(self.table_main_shema_edit, self.connect_button)
    
    
    def on_connect(self):
        # Чтение введённых данных
        self.params = {
            'dbname': self.dbname_edit.text(),
            'user': self.user_edit.text(),
            'password': function_use.encrypt_data(self.password_edit.text().encode('utf-8')),
            'host': self.host_edit.text(),
            'port': int(self.port_edit.text()) if self.port_edit.text().isdigit() else None,
            'save_password': self.save_password_checkbox.isChecked(),
            'table_main_shema': self.table_main_shema_edit.text(),
            }
        
        # Если нужно можно показать информацию
        # QMessageBox.information(self, "Параметры подключения", f"Получены параметры:\n{self.connection_params}")
        
        # Закрываем окно, возвращая Accepted
        self.accept()
    
    
    def get_params(self):
        """Метод для получения введённых данных после закрытия окна."""
        return self.params
