import sys
import psycopg2
import copy
import re
import datetime
from PyQt5 import QtCore, QtGui
from Table_Class import Class_window_inf, Class_columns_opisanie
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout, \
                            QTableWidget, QPushButton, QCheckBox, QTableWidgetItem, QComboBox, QMessageBox, \
                            QMenu
from PyQt5.QtCore import Qt
import function_use


class Class_TableWindow(QWidget):
    def __init__(self, table_name, db_conn, parent=None, window_inf : Class_window_inf = None ):
        super().__init__(parent)
        self.table_name = table_name
        s1 = self.table_name.split('.')
        if len(s1) == 2:
            self.table_name_shema = s1[0]
            self.table_name_table = s1[1]
        else:
            self.table_name_shema = ''
            self.table_name_table = self.table_name
        
        self.table_description = ''
        self.db_conn = db_conn
        self.parent_table_id = 0
        self.child_table_col_sviaz = ''
        self.window_inf = window_inf
        self.arr_columns_opisanie = []
        
        self.arr_columns_opisanie, self.table_description = \
            function_use.load_table_inf(self.db_conn, self.table_name, self.window_inf.arr_tables_col_nastr)
        
        self.init_ui()
        self.select_data()
    
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        label_table = QLabel(f'''{self.table_name} ({self.table_description})''', self)
        layout.addWidget(label_table)
        
        # Таблица для отображения данных
        self.table = QTableWidget()
        #layout.setContentsMargins(100, 100, 500, 500)  # отступы: left, top, right, bottom
        #self.table.setGeometry(10, 10, 480, 480)
        
        layout.addWidget(self.table)
        self.setLayout(layout)
        
        self.table.currentCellChanged.connect(self.table_cell_select)
        self.table.cellChanged.connect(self.table_cell_changed)
        
        # Кнопки операций
        button_layout = QHBoxLayout()

        btn_update = QPushButton("Обновить")
        btn_update.clicked.connect(self.select_data)
        button_layout.addWidget(btn_update)
        
        if not self.window_inf.b_read_only:
            btn_add = QPushButton("Добавить")
            btn_add.clicked.connect(self.add_record)
            button_layout.addWidget(btn_add)
            
            btn_copy_record = QPushButton("Копировать")
            btn_copy_record.clicked.connect(self.copy_record)
            button_layout.addWidget(btn_copy_record)
        
        btn_delete = QPushButton("Удалить")
        btn_delete.clicked.connect(self.delete_record)
        button_layout.addWidget(btn_delete)
        
        # специальные команды, привязанные к окнам
        if len(self.window_inf.arr_tables_command) > 0:
            self.btn_spec_command = QPushButton("Команды")
            button_layout.addWidget(self.btn_spec_command)
            self.add_spec_command_menu()
        
#        if self.table_name_table in ['uaip_column_maska_group', 'uaip_column_maska_pos', 'uaip_posledovat_gruppa']:
#            self.btn_spec_command = QtWidgets.QPushButton("Команды")
#            button_layout.addWidget(self.btn_spec_command)
#            self.add_spec_command_menu()
        
        layout.addLayout(button_layout)
    
    
    # перемещаемся по ячейкам таблицы object_main
    def table_cell_select(self, currentRow, currentColumn, previousRow, previousColumn):
        if currentRow is not None and currentRow != previousRow:
            
            for i in range(len(self.arr_columns_opisanie)):
                if self.arr_columns_opisanie[i].column_name == self.window_inf.col_id_name:
                    id_col = self.arr_columns_opisanie[i].ordinal_position_new - 1
            id_n = function_use.to_int(self.table.item(currentRow, 0).text())
            if id_n is not None:
                self.parent().parent().select_child_table(t_name=self.table_name, 
                                                          t_id=id_n)
    
    
    # вносим изменения в БД при корректировке в таблице
    def table_cell_changed(self, row, col):
        # Получаем текст измененной ячейки
        for i in range(len(self.arr_columns_opisanie)):
            if self.arr_columns_opisanie[i].ordinal_position_new == col + 1:
                i_pos = i
            if self.arr_columns_opisanie[i].column_name == self.window_inf.col_id_name:
                item = self.table.item(row, self.arr_columns_opisanie[i].ordinal_position_new - 1)
                col_id = item.text()
        
        item = self.table.item(row, col)
        value = item.text()
        if self.arr_columns_opisanie[i_pos].data_type in ['character varying']:
            if value == '[null]':
                value = 'null'
            else:
                if len(value) > self.arr_columns_opisanie[i_pos].character_maximum_length:
                    reply = QMessageBox.question(self, 'Ошибка изменения',
                             f"Строка превышает допустимую длину {self.arr_columns_opisanie[i_pos].character_maximum_length}.\n Изменение данных невозможно.",
                             QMessageBox.Ok)
                    return
                value = "'" + value.replace("'", "''") + "'"
        elif self.arr_columns_opisanie[i_pos].data_type in ['text']:
            if value == '[null]':
                value = 'null'
            else:
                value = "'" + value.replace("'", "''") + "'"                
        elif self.arr_columns_opisanie[i_pos].data_type in ['smallint', 'integer', 'bigint', 'numeric']:
            if value in ['[null]', '']:
                value = 'null'
            else:
                if not function_use.is_number(test_value = value,
                                              type_db = self.arr_columns_opisanie[i_pos].data_type, 
                                              numeric_precision = self.arr_columns_opisanie[i_pos].numeric_precision, 
                                              numeric_scale = self.arr_columns_opisanie[i_pos].numeric_scale):
                    reply = QMessageBox.question(self, 'Ошибка изменения',
                             f"Введённые данные не соответсвуют формату поля {self.arr_columns_opisanie[i_pos].data_type}.\n Изменение данных невозможно.",
                             QMessageBox.Ok)
                    return
                else:
                    value = value.replace(',', '.')
        
        elif self.arr_columns_opisanie[i_pos].data_type in ['date']:
            if value in ['[null]', '']:
                value = 'null'
            else:
                try:
                    d1 = datetime.datetime.strptime(value, '%Y-%m-%d')
                    value = "'" + d1.strftime('%Y-%m-%d') + "'"
                except:
                    reply = QMessageBox.question(self, 'Ошибка изменения',
                             f"Введённые данные не соответсвуют формату поля {self.arr_columns_opisanie[i_pos].data_type}.\n Дату следует вести в формате 2024-01-15.\nИзменение данных невозможно.",
                             QMessageBox.Ok)
                    return
        
        elif self.arr_columns_opisanie[i_pos].data_type in ['timestamp with time zone', 'timestamp without time zone']:
            if value in ['[null]', '']:
                value = 'null'
            else:
                try:
                    d1 = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                    value = "'" + d1.strftime('%Y-%m-%d %H:%M:%S') + "'"
                except:
                    reply = QMessageBox.question(self, 'Ошибка изменения',
                             f"Введённые данные не соответсвуют формату поля {self.arr_columns_opisanie[i_pos].data_type}.\n Дату, время следует вести в формате 2024-01-15 00:00:00.\nИзменение данных невозможно.",
                             QMessageBox.Ok)
                    return
        
        sql = f'''UPDATE {self.table_name} tu set {self.arr_columns_opisanie[i_pos].column_name} = {value}
                    where {self.window_inf.col_id_name} = {col_id}'''
#        print(sql)
        cur = self.db_conn.cursor()
        cur.execute(sql)
        self.db_conn.commit()
        cur.close()
    
    
    # для галочек - булевые значения
    def on_checkbox_state_changed(self, state, row, col):
        for i in range(len(self.arr_columns_opisanie)):
            if self.arr_columns_opisanie[i].ordinal_position_new == col + 1:
                i_pos = i
            if self.arr_columns_opisanie[i].column_name == self.window_inf.col_id_name:
                item = self.table.item(row, i)
                col_id = item.text()
        if state == 0: value = 'false'
        elif state == 1: value = 'null'
        elif state == 2: value = 'true'
            
        sql = f'''UPDATE {self.table_name} tu set {self.arr_columns_opisanie[i_pos].column_name} = {value}
                    where {self.window_inf.col_id_name} = {col_id}'''
        cur = self.db_conn.cursor()
        cur.execute(sql)
        self.db_conn.commit()
        cur.close()
    
    
    def on_combobox_index_changed(self, index, row, col):
        for i in range(len(self.arr_columns_opisanie)):
            if self.arr_columns_opisanie[i].ordinal_position_new == col + 1:
                i_pos = i
            if self.arr_columns_opisanie[i].column_name == self.window_inf.col_id_name:
                item = self.table.item(row, i)
                col_id = item.text()
        
        combobox = self.table.cellWidget(row, col)
        selected_id = combobox.itemData(index)
        selected_text = combobox.itemText(index)
    
        #print('selected_id =', selected_id, 'selected_text =', selected_text)
        
        if selected_id is None:
            selected_id = 'null'
        
        sql = f'''UPDATE {self.table_name} tu set {self.arr_columns_opisanie[i_pos].column_name} = {str(selected_id)}
                    where {self.window_inf.col_id_name} = {col_id}'''
        cur = self.db_conn.cursor()
        cur.execute(sql)
        self.db_conn.commit()
        cur.close()
        
    
    def select_data(self):
        try:
            cur = self.db_conn.cursor()
            sp_col = ''
            for co in self.arr_columns_opisanie:
                if sp_col != '': sp_col += ', '
                sp_col += co.column_name
            
            sql = f'''SELECT {sp_col} FROM {self.table_name}'''
            if self.window_inf.b_main == False and self.parent_table_id > 0 and self.child_table_col_sviaz != '':
                sql += f''' WHERE {self.child_table_col_sviaz} = {str(self.parent_table_id)} ''' 
            elif self.window_inf.b_main == False:
                sql += f''' WHERE id = 0 ''' 
            
            if self.window_inf.order_uslovie != '':
                sql += f''' ORDER BY {self.window_inf.order_uslovie} '''
            
            if self.window_inf.row_limit > 0:
                sql += f''' limit {str(self.window_inf.row_limit)} '''
            
            try:
                cur.execute(sql)
            except Exception as e:
                #print(sql)
                QMessageBox.critical(self, "Ошибка загрузки данных", f'''Ошибка:\n{str(e)}\nЗапрос:\n{sql}''')
                cur.close()
                self.db_conn.rollback()
            
            rows = cur.fetchall()
            headers = [desc[0] for desc in cur.description]
            
            self.table.blockSignals(True)  # Блокируем отправку сигналов
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)
            for co in self.arr_columns_opisanie:
                header_item = QTableWidgetItem(co.column_name)
                header_item.setToolTip(co.description)
                self.table.setHorizontalHeaderItem(co.ordinal_position_new - 1, header_item)
            
            self.table.setRowCount(len(rows))
            
            self.table.setWordWrap(False)
            # Определяем высоту одной строки, используя текущий шрифт и немного добавив отступ
            one_line_height = QtGui.QFontMetrics(self.table.font()).height() + 4
            
            for row_idx, row in enumerate(rows):
                self.table.setRowHeight(row_idx, one_line_height)
                for col_idx, value in enumerate(row):
                    
                    if self.arr_columns_opisanie[col_idx].data_type == 'boolean':
                        # Создаем QCheckBox с трёхсостоящим режимом
                        checkbox = QCheckBox('')
                        checkbox.setTristate(True)  # Включаем трёхсостоящий режим
                        # Устанавливаем начальное состояние, например, для Null используем PartiallyChecked
                        if value == True:
                            checkbox.setCheckState(Qt.Checked)
                        elif value == False:
                            checkbox.setCheckState(Qt.Unchecked)
                        else: # Null
                            checkbox.setCheckState(Qt.PartiallyChecked)                        
                        
                        if self.window_inf.b_read_only:
                            #checkbox.setCheckable(False)
                            checkbox.setEnabled(False)
                            #pass
                        else:                           
                            checkbox.stateChanged.connect(lambda state, row=row_idx, col=col_idx: self.on_checkbox_state_changed(state, row, col))
                        
                        # Размещаем чекбокс в ячейке (1,1) таблицы
                        self.table.setCellWidget(row_idx, col_idx, checkbox)
                        
                    elif self.arr_columns_opisanie[col_idx].zapros_sql_combobox != '':
                        if self.window_inf.b_read_only:
                            # если запрет на редактирование - просто заносим в поле текст
                            if value is None:
                                value = '[null]'
                            else:
                                for item_id, item_name in self.arr_columns_opisanie[col_idx].combobox_item_data:
                                    if value == item_id:
                                        value = item_name
                            
                            item = QTableWidgetItem(str(value))
                            # делаем поле не редактируемым
                            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                            self.table.setItem(row_idx, col_idx, item)
                        else:
                            combobox = QComboBox() # Создаем QComboBox
                            combobox.setStyleSheet('''QComboBox { background-color: white;
                                                                  border: none;}''')                            
                            for item_id, item_name in self.arr_columns_opisanie[col_idx].combobox_item_data:
                                combobox.addItem(item_name, item_id)
                            
                            index = combobox.findData(value)
                            if index >= 0:
                                combobox.setCurrentIndex(index)
        
                            # Подключаем сигнал изменения выбранного элемента
                            combobox.currentIndexChanged.connect(lambda index, row=row_idx, col=col_idx: self.on_combobox_index_changed(index, row, col))
                            
                            # Размещаем QComboBox в ячейке таблицы
                            self.table.setCellWidget(row_idx, col_idx, combobox)
                    else:
                        if value is None:
                            value = '[null]'
                        item = QTableWidgetItem(str(value))
                        # делаем поле не редактируемым
                        if self.window_inf.b_read_only or self.arr_columns_opisanie[col_idx].column_name in [self.window_inf.col_id_name, self.child_table_col_sviaz]:
                            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    
                        self.table.setItem(row_idx, col_idx, item)
            
            
            cur.close()
            self.db_conn.commit()
            self.table.blockSignals(False)  # Снимаем блокировку сигналов (изменени ятаблицы руками будут вноситься в базу)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки данных", str(e))
            self.db_conn.rollback()
            cur.close()
    
    
    def add_record(self):
        # Здесь предполагается, что таблица имеет два столбца (например, name, description)
        if self.window_inf.b_main:
            sql = f'''INSERT INTO {self.table_name} DEFAULT VALUES;'''
        elif self.parent_table_id > 0 and self.child_table_col_sviaz != '':
            sql = f'''INSERT INTO {self.table_name}({self.child_table_col_sviaz}) VALUES ({self.parent_table_id});'''
        else:
            QMessageBox.critical(self, "Ошибка добавления записи", "Строка родительской таблицы не выбрана.")
        if sql != '':
            try:
                cur = self.db_conn.cursor()
                cur.execute(sql)
                self.db_conn.commit()
                cur.close()
                self.select_data()  # обновляем таблицу
            except Exception as e:
                self.db_conn.rollback()
                cur.close()
                QMessageBox.critical(self, "Ошибка добавления записи", str(e))
    
    
    def copy_record(self):
        col_id = self.get_select_id()
        if col_id is None:
            QMessageBox.critical(self, "Выбор записи", "Необходимо выбрать запись для копирования.")
            return
        
        if col_id == '' or self.window_inf.col_id_name == '':
            QMessageBox.critical(self, "Ошибка копирования", "Не определён УН записи для копирования.")
            return
        
        self.parent().parent().copy_tables(t_name=self.table_name, t_id=col_id, t_col_parent_name='', t_col_parent_id=0, b_kaskad=True)
        self.select_data()  # обновляем таблицу
    
    
    def delete_record(self):
        col_id = self.get_select_id()
        if col_id is None:
            QMessageBox.critical(self, "Выбор записи", "Необходимо выбрать запись для удаления.")
            return
        
        if col_id == '' or self.window_inf.col_id_name == '':
            QMessageBox.critical(self, "Ошибка удаления", "Не определён УН записи для удаления.")
            return
        
        reply = QMessageBox.question(self, 'Удаление записи',
                     f"Вы действительно хотите удалить запись с {self.window_inf.col_id_name} = {col_id}?",
                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.parent().parent().delete_from_tables(t_name=self.table_name, t_id=col_id, b_kaskad=True)
            self.select_data()  # обновляем таблицу
    
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # получаем выделенную id-шку
    def get_select_id(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None
        
        row = selected_items[0].row()
        col_id = ''
        for i in range(len(self.arr_columns_opisanie)):
            if self.arr_columns_opisanie[i].column_name == self.window_inf.col_id_name:
                item = self.table.item(row, i)
                col_id = item.text()
                return col_id
    
    # создаём меню
    def add_spec_command_menu(self):
        self.menu_command = QMenu(self)
        for tc in self.window_inf.arr_tables_command:
            action_run = self.menu_command.addAction(tc.menu_text)
            action_run.triggered.connect(lambda checked, c=tc: self.btn_spec_command__run_command(c.command, c.mess_col_id_null, c.mess_ok, c.mess_err, c.b_update_child_table))
            self.btn_spec_command.setMenu(self.menu_command)


    # выполняем команды меню
    def btn_spec_command__run_command(self, command, mess_col_id_null, mess_ok, mess_err, b_update_child_table):
        col_id = self.get_select_id()
        
        if col_id is None:
            QMessageBox.critical(self, "Выбор записи", mess_col_id_null)
            return
        
        match = re.search('{col_id}', command)        
        if match is None:
            QMessageBox.critical(self, "Выбор записи", f'''Команда должна содержать {col_id}, иначе выполнение не возможно. \n{command}''')
        
        try:
            command = command.replace('{col_id}', col_id)
            sql = command
            mess_col_id_null = mess_col_id_null.replace('{col_id}', col_id).replace('{sql}', sql)
            mess_ok = mess_ok.replace('{col_id}', col_id).replace('{sql}', sql)
            mess_err = mess_err.replace('{col_id}', col_id).replace('{sql}', sql)
            
            cur = self.db_conn.cursor()
            cur.execute(sql)
            self.db_conn.commit()
            cur.close()
            QMessageBox.information(self, "Команда выполнена\n", mess_ok)
            
            if b_update_child_table:
                id_n = function_use.to_int(col_id)
                if id_n is not None:
                    self.parent().parent().select_child_table(t_name=self.table_name, 
                                                              t_id=id_n)
                
        except Exception as e:
            self.db_conn.rollback()
            cur.close()
            QMessageBox.critical(self, "Ошибка выполнения\n", mess_err)
            