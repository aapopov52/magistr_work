import sys
import psycopg2
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
import Table_window
import copy
from Table_Class import Class_window_inf, Class_child_tables_sviaz, Class_tables_command, Class_tables_col_nastr
import function_use


class Class_Windowgroup(QtWidgets.QMainWindow):
    
    """
    Главное окно приложения, где таблицы размещаются напрямую на центральном виджете без использования табов.
    """
    def __init__(self, db_conn, table_main_shema):
        super().__init__()
        self.db_conn = db_conn
        self.arr_window_inf = []
        self.table_main_shema = table_main_shema
        self.init_ui()
    
    
    def init_ui(self):
        
        self.setWindowTitle("Приложение для работы с базой данных PostgreSQL")
        self.resize(1700, 950)
        
        # Создаем центральный виджет
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Базовая таблица
        layout = QtWidgets.QVBoxLayout(self.central_widget) 
        layout.setContentsMargins(10, 10, 1700 - 280, 10) 
        
        
        self.btn_update = QtWidgets.QPushButton("Обновить")
        self.btn_update.clicked.connect(self.load_data_table_spisok)
        layout.addWidget(self.btn_update)
        
        self.table_spisok = QtWidgets.QTableWidget() 
        layout.addWidget(self.table_spisok) 
        self.table_spisok.currentCellChanged.connect(self.table_spisok_cell_changed)
        
        # грузим информцаию о имеющихся таблицах
        self.load_data_table_spisok()
    
    
    # Загрузка основного списка
    def load_data_table_spisok(self):
        try:
            cur = self.db_conn.cursor()
            # Данный запрос может быть изменён в зависимости от структуры вашей таблицы
            sql = f'''SELECT id,  coalesce(num_1, 0) :: varchar ||
                    	case when num_2 is not null then '.' || num_2 :: varchar else '' end ||
                    	case when num_3 is not null then '.' || num_3 :: varchar else '' end ||
                    	' ' ||
                    	name,
                        case when num_3 is not null then 3
                             when num_2 is not null then 2
                             else 1 end
                    FROM {self.table_main_shema}.interface_forms
                    where b_act = True
                    order by coalesce(num_1, 0), coalesce(num_2, 0), coalesce(num_3, 0), id '''
            cur.execute(sql)
            rows = cur.fetchall()
            headers = ['УН', 'Наименование']
            
            self.table_spisok.verticalHeader().setVisible(False)
            self.table_spisok.setColumnCount(len(headers))
            self.table_spisok.setHorizontalHeaderLabels(headers)
            self.table_spisok.setRowCount(len(rows))
            
            self.table_spisok.setColumnWidth(0, 10)
            self.table_spisok.setColumnWidth(1, 250)
            
            
            self.table_spisok.setWordWrap(False)
            # Определяем высоту одной строки, используя текущий шрифт и немного добавив отступ
            one_line_height = QtGui.QFontMetrics(self.table_spisok.font()).height() + 4
            
            for row_idx, row in enumerate(rows):
                self.table_spisok.setRowHeight(row_idx, one_line_height)
                i_level = 2
                if row[2] is not None: i_level = row[2]
                for col_idx in range(2):
                    value = row[col_idx]
                    if i_level == 2 and col_idx == 1:
                        value = '  ' + str(value)
                    elif i_level == 3 and col_idx == 1:
                        value = '    ' + str(value)
                    item = QtWidgets.QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    if i_level == 1:
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                    elif i_level == 3:
                        font = item.font()
                        font.setItalic(True)
                        item.setFont(font)
                    self.table_spisok.setItem(row_idx, col_idx, item)
                    
            cur.close()
            self.db_conn.commit()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка загрузки данных", str(e))
    
    
    # ОСНОВНАЯ ТАБЛИЦА - перемещение по ячейкам (выбор формы для отображения)
    def table_spisok_cell_changed(self, currentRow, currentColumn, previousRow, previousColumn):
        if currentRow is not None and currentRow != previousRow:
            id_interface_forms = function_use.to_int(self.table_spisok.item(currentRow, 0).text())
            
            # удаление старых форм
            for wi in self.arr_window_inf:
                widget = wi.table_widget
                if widget is not None:
                    layout = widget.parentWidget().layout() # Если виджет находится в менеджере компоновки - удаляем 
                    if layout is not None:
                        layout.removeWidget(widget)
                    widget.setParent(None) # Отключаем виджет от родительского виджета
                    widget.deleteLater() # Запрашиваем удаление виджета
            self.arr_window_inf = []
            
            # загружаем информацию по отображаемым на форме окнам
            sql = f''' select id, table_name, col_id_name, order_uslovie, row_limit, left_, top_, width_, heigth_, b_read_only
                        from {self.table_main_shema}.interface_forms_tables
                        where id_interface_forms = {id_interface_forms}
                        order by id ''' 
            
            cur = self.db_conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            
            for row in rows:
                window_inf = Class_window_inf()
                if row[0] is not None:
                    window_inf.id_interface_forms_tables = row[0]
                if row[1] is not None:
                    window_inf.table_name = row[1]
                if row[2] is not None:
                    window_inf.col_id_name = row[2]
                if row[3] is not None:
                    window_inf.order_uslovie = row[3]
                if row[4] is not None:
                    window_inf.row_limit = row[4]    
                if row[5] is not None:
                    window_inf.left = row[5] + 270 # смещаем на ширину основной формы
                if row[6] is not None:
                    window_inf.top = row[6]
                if row[7] is not None:
                    window_inf.width = row[7]
                if row[8] is not None:
                    window_inf.heigth = row[8]
                if row[9] is not None:
                    window_inf.b_read_only = row[9]
                    
                self.arr_window_inf.append(copy.deepcopy(window_inf))
            
            cur.close()
            # interface_forms_tables_sviaz
            sql = f''' select t_ift_sv.id_interface_forms_tables, t_ift_sv.table_name, t_ift_sv.table_col_sviaz 
                        from {self.table_main_shema}.interface_forms_tables_sviaz t_ift_sv
                        join {self.table_main_shema}.interface_forms_tables t_ift on t_ift.id = t_ift_sv.id_interface_forms_tables
                        where t_ift.id_interface_forms = {id_interface_forms}
                        order by t_ift_sv.id_interface_forms_tables ''' 
            cur = self.db_conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            arr_child_tables = []
            i_wi = -1
            for row in rows:
                child_tables_sviaz = Class_child_tables_sviaz()
                if row[0] is not None:
                    child_tables_sviaz.id_interface_forms_tables = row[0]
                if row[1] is not None:
                    child_tables_sviaz.table_name = row[1]
                if row[2] is not None:
                    child_tables_sviaz.table_col_sviaz = row[2]
                
                if i_wi >= 0:
                    if self.arr_window_inf[i_wi].id_interface_forms_tables == child_tables_sviaz.id_interface_forms_tables:
                        self.arr_window_inf[i_wi].arr_child_tables_sviaz.append(copy.copy(child_tables_sviaz))
                        arr_child_tables.append(copy.copy(child_tables_sviaz.table_name))
                    else:
                        i_wi = -1
                
                if i_wi == -1:
                    for i1 in range(len(self.arr_window_inf)):
                        if self.arr_window_inf[i1].id_interface_forms_tables == child_tables_sviaz.id_interface_forms_tables:
                            i_wi = i1
                            break
                    if i_wi >= 0:
                        self.arr_window_inf[i_wi].arr_child_tables_sviaz.append(copy.copy(child_tables_sviaz))
                        arr_child_tables.append(copy.copy(child_tables_sviaz.table_name))
            cur.close()
            
            # interface_forms_tables_command
            sql = f''' select t_ift_com.id_interface_forms_tables, t_ift_com.num, t_ift_com.name, t_ift_com.command, t_ift_com.menu_text, t_ift_com.mess_col_id_null, t_ift_com.mess_ok, t_ift_com.mess_err, t_ift_com.b_update_child_table
                        from {self.table_main_shema}.interface_forms_tables_command t_ift_com 
                        join {self.table_main_shema}.interface_forms_tables t_ift on t_ift.id = t_ift_com.id_interface_forms_tables 
                        where t_ift.id_interface_forms = {id_interface_forms} 
                        order by t_ift_com.id_interface_forms_tables, t_ift_com.num ''' 
            cur = self.db_conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            i_wi = -1
            for row in rows:
                tables_command = Class_tables_command()
                if row[0] is not None:
                    tables_command.id_interface_forms_tables = row[0]
                if row[1] is not None:
                    tables_command.num = row[1]
                if row[2] is not None:
                    tables_command.name = row[2]
                if row[3] is not None:
                    tables_command.command = row[3]
                if row[4] is not None:
                    tables_command.menu_text = row[4]
                if row[5] is not None:
                    tables_command.mess_col_id_null = row[5]
                if row[6] is not None:
                    tables_command.mess_ok = row[6]
                if row[7] is not None:
                    tables_command.mess_err = row[7]
                if row[8] is not None:
                    tables_command.b_update_child_table = row[8]

                if i_wi >= 0:
                    if self.arr_window_inf[i_wi].id_interface_forms_tables == tables_command.id_interface_forms_tables:
                        self.arr_window_inf[i_wi].arr_tables_command.append(copy.copy(tables_command))
                    else:
                        i_wi = -1
                
                if i_wi == -1:
                    for i1 in range(len(self.arr_window_inf)):
                        if self.arr_window_inf[i1].id_interface_forms_tables == tables_command.id_interface_forms_tables:
                            i_wi = i1
                            break
                    if i_wi >= 0:
                        self.arr_window_inf[i_wi].arr_tables_command.append(copy.copy(tables_command))
                        
            # 
            sql = f''' select t_ift_cn.id_interface_forms_tables, t_ift_cn.col_name, 
                              t_ift_cn.ordinal_position_new, t_ift_cn.zapros_sql_combobox 
                        from {self.table_main_shema}.interface_forms_tables_col_nastr t_ift_cn 
                        join {self.table_main_shema}.interface_forms_tables t_ift on t_ift.id = t_ift_cn.id_interface_forms_tables 
                        where t_ift.id_interface_forms = {id_interface_forms} 
                        order by t_ift_cn.id_interface_forms_tables, t_ift_cn.ordinal_position_new ''' 
            cur = self.db_conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            i_wi = -1
            i_col = 0
            for row in rows:
                tables_col_nastr = Class_tables_col_nastr()
                i_col += 1 
                tables_col_nastr.ordinal_position_new = i_col # в базе номера столбоц могут идти с пропусками (не последовательно), делаем цельную картину
                if row[0] is not None:
                    tables_col_nastr.id_interface_forms_tables = row[0]
                if row[1] is not None:
                    tables_col_nastr.column_name = row[1]
                if row[3] is not None:
                    tables_col_nastr.zapros_sql_combobox = row[3]
                
                if i_wi >= 0:
                    if self.arr_window_inf[i_wi].id_interface_forms_tables == tables_col_nastr.id_interface_forms_tables:
                        self.arr_window_inf[i_wi].arr_tables_col_nastr.append(copy.copy(tables_col_nastr))
                    else:
                        i_wi = -1
                
                if i_wi == -1:
                    for i1 in range(len(self.arr_window_inf)):
                        if self.arr_window_inf[i1].id_interface_forms_tables == tables_col_nastr.id_interface_forms_tables:
                            i_wi = i1
                            break
                    if i_wi >= 0:
                        self.arr_window_inf[i_wi].arr_tables_col_nastr.append(copy.copy(tables_col_nastr))
                    
            
            cur.close()
            self.db_conn.commit()
            
        
        # Создаем экземпляры Class_TableWindow для разных таблиц
        for irow, wi in enumerate(self.arr_window_inf):
            # определяем, является ли форма "подчинёной"
            if wi.table_name in arr_child_tables: 
                wi.b_main = False
            self.arr_window_inf[irow].table_widget = Table_window.Class_TableWindow(table_name = wi.table_name, 
                                                            db_conn = self.db_conn,
                                                            window_inf = wi)
            self.arr_window_inf[irow].table_widget.setParent(self.central_widget)
            self.arr_window_inf[irow].table_widget.setGeometry(wi.left, wi.top, wi.width, wi.heigth)
            
            if self.arr_window_inf[irow].b_main:
                self.arr_window_inf[irow].table_widget.select_data()
            self.arr_window_inf[irow].table_widget.show()
    
    
    # РАБОТА С ТАБЛИЦАМИ ФОРМЫ
    # перемещаемся по "главной" таблице - изменяем данные в "подчинённых"
    #t_name - главная таблица
    #t_id - значение идентификатора главной таблицы
    def select_child_table(self, t_name='', t_id=0):
        # ищем таблицы, котрые следует обновить (подчинённые)
        for wi in self.arr_window_inf:
            if wi.table_name == t_name:
                wi_m = copy.copy(wi)
                break
        
        # обновляем подчинённые таблицы
        if len(wi_m.arr_child_tables_sviaz) > 0:
            for i in range(len(wi_m.arr_child_tables_sviaz)):
                for wi in self.arr_window_inf:
                    if wi.table_name == wi_m.arr_child_tables_sviaz[i].table_name:
                        wi.table_widget.parent_table_id = t_id
                        wi.table_widget.child_table_col_sviaz = wi_m.arr_child_tables_sviaz[i].table_col_sviaz
                        wi.table_widget.select_data()
                        #print ('rowСount =', wi.table_widget.table.rowCount())
                        self.select_child_table(wi.table_name) # рекурсией очищаем все вложенные окна
    
    
    # копирование (в т.ч. каскадное)
    def copy_tables(self, t_name='', t_id=0, t_col_parent_name='', t_col_parent_id=0, b_kaskad=False):
        
        # копируем строку в основной таблице
        cur = self.db_conn.cursor()
        arr_columns_opisanie = []
        # набираем данные о параметрах вставки
        for wi in self.arr_window_inf:
            if wi.table_name == t_name:
                wi_m = copy.copy(wi)
                break
        
        arr_columns_opisanie, table_description = \
            function_use.load_table_inf(conn=self.db_conn, table_name=t_name)
        col_ins = ''
        col_ins_values = ''
        for col in arr_columns_opisanie:
            
            if col.column_name != wi_m.col_id_name:
                if col_ins != '': col_ins += ', '
                col_ins += col.column_name
            if col.column_name != wi_m.col_id_name:
                if col_ins_values != '': col_ins_values += ', '
                if col.column_name != t_col_parent_name:
                    col_ins_values += col.column_name
                else:
                    col_ins_values += str(t_col_parent_id)
        
        sql = f""" 
               do $$
               declare 
                   id_new_ int;
               begin     
        
                   insert into {t_name} ({col_ins})
                                    select {col_ins_values}
                                    from {t_name}
                                    where {wi_m.col_id_name} = {str(t_id)}
                   RETURNING id INTO id_new_;
                   
                   RAISE INFO 'id_new_%', id_new_;
               end; $$
                """
        
        #print(sql_query)
        self.db_conn.notices = []
        cur.execute(sql)
        self.db_conn.commit()
        id_new = 0
        for notice in self.db_conn.notices:
            if 'id_new' in notice:
                id_new = int(notice[notice.find('id_new') + len('id_new') + 1:])
                break
        if b_kaskad:
            # дополняем подчинённые таблицы
            if len(wi_m.arr_child_tables_sviaz) > 0:
                for i in range(len(wi_m.arr_child_tables_sviaz)):
                    for wi in self.arr_window_inf:
                        if wi.table_name == wi_m.arr_child_tables_sviaz[i].table_name:
                            parent_col_id = id_new
                            parent_col_name = wi_m.arr_child_tables_sviaz[i].table_col_sviaz
                            # выбираем все строки в подчинёной таблице
                            # и каждую из них копируем, но уже с учётом id_parent
                            sp_id = self.copy_tables_get_id_table(t_name = wi.table_name, col_usl_name = parent_col_name, col_usl_value = t_id, col_id_name = wi.col_id_name)
                            for id_ in sp_id:
                                self.copy_tables(t_name=wi.table_name, t_id=id_, t_col_parent_name=parent_col_name, t_col_parent_id=parent_col_id, b_kaskad = b_kaskad)
    
    # удаление (в т.ч. каскадное)
    def delete_from_tables(self, t_name='', t_id=0, b_kaskad=False):
        
        # копируем строку в основной таблице
        cur = self.db_conn.cursor()
        # набираем данные о параметрах вставки
        for wi in self.arr_window_inf:
            if wi.table_name == t_name:
                wi_m = copy.copy(wi)
                break        

        if b_kaskad:
            # дополняем подчинённые таблицы
            if len(wi_m.arr_child_tables_sviaz) > 0:
                for i in range(len(wi_m.arr_child_tables_sviaz)):
                    for wi in self.arr_window_inf:
                        if wi.table_name == wi_m.arr_child_tables_sviaz[i].table_name:
                            parent_col_name = wi_m.arr_child_tables_sviaz[i].table_col_sviaz
                            # выбираем все строки в подчинёной таблице
                            # и каждую из них копируем, но уже с учётом id_parent
                            sp_id = self.copy_tables_get_id_table(t_name = wi.table_name, col_usl_name = parent_col_name, col_usl_value = t_id, col_id_name = wi.col_id_name)
                            for id_ in sp_id:
                                self.delete_from_tables(t_name=wi.table_name, t_id=id_, b_kaskad = b_kaskad)

        sql = f""" delete from {t_name} where {wi_m.col_id_name} = {str(t_id)} """
        
        #print(sql_query)
        self.db_conn.notices = []
        cur.execute(sql)
        self.db_conn.commit()
        
                                
    # получаем список значений id таблицы
    def copy_tables_get_id_table(self, t_name = '', # имя подчинённой таблицы
                                 col_usl_name = '', # имя столбца по которой связь с родительской таблицей
                                 col_usl_value = 0, # значение (УН) столбца из родителькой таблицы
                                 col_id_name = 'id' # имя ячейки (УН) значения из которой возвращаем
                                 ):
        sp_out = []
        cur = self.db_conn.cursor()
        sql = f''' select {col_id_name} from {t_name} where {col_usl_name} = {col_usl_value} '''
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            if row is not None:
                sp_out.append(row[0])
        
        cur.close()
        self.db_conn.commit()
        return sp_out