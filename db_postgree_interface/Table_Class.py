

class Class_tables_col_nastr:
    def __init__(self):
        self.id_interface_forms_tables : int = 0
        self.column_name : str = ''
        self.ordinal_position_new : int = 0
        self.zapros_sql_combobox : str = ''


class Class_tables_command:
    def __init__(self):
        self.id_interface_forms_tables : int = 0
        self.num : int = 0
        self.name : str = ''
        self.command : str = ''
        self.menu_text : str = ''
        self.mess_col_id_null : str = ''
        self.mess_ok : str = ''
        self.mess_err : str = ''
        self.b_update_child_table : bool = False
        
        
class Class_tables_command:
    def __init__(self):
        self.id_interface_forms_tables : int = 0
        self.num : int = 0
        self.name : str = ''
        self.command : str = ''
        self.menu_text : str = ''
        self.mess_col_id_null : str = ''
        self.mess_ok : str = ''
        self.mess_err : str = ''
        self.b_update_child_table : bool = False


class Class_child_tables_sviaz:
    def __init__(self):
        self.id_interface_forms_tables : int = 0
        self.table_name : str = ''
        self.table_col_sviaz : str = ''


class Class_window_inf():
    def __init__(self):
        self.id_interface_forms_tables : int = 0
        self.table_name : str = ''
        self.col_id_name : str = ''
        self.order_uslovie : str = ''
        self.row_limit : int = 1000
        self.arr_child_tables_sviaz : Class_child_tables_sviaz = []
        self.arr_tables_command : Class_tables_command = []
        self.arr_tables_col_nastr : Class_tables_col_nastr = []
        self.table_widget = None
        self.b_main = True
        self.left : int = 0
        self.top: int = 0
        self.width : int = 0
        self.heigth : int = 0
        self.b_read_only : bool = False


class Class_columns_opisanie():
    def __init__(self):
        self.column_name : str = ''
        self.data_type : str = ''
        self.character_maximum_length : int = 0
        self.ordinal_position : int = 0
        self.ordinal_position_new : int = 0
        self.ordinal_position_vrem : int = 0  # используется для получения информации о полноте
        self.numeric_precision : int = 0
        self.numeric_scale : int = 0
        self.numeric_precision_radix : int = 0
        self.description : str = ''
        self.zapros_sql_combobox : str = ''
        self.combobox_item_data = []
    