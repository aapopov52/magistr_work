from Table_Class import Class_columns_opisanie, Class_tables_col_nastr
import copy
import win32crypt

def encrypt_data(data: bytes) -> bytes:
    # Шифрует данные с помощью DPAPI
    blob = win32crypt.CryptProtectData(data, None, None, None, None, 0)
    return blob

def decrypt_data(encrypted_data: bytes) -> bytes:
    # Расшифровывает данные с помощью DPAPI
    description, decrypted_data = win32crypt.CryptUnprotectData(encrypted_data, None, None, None, 0)
    return decrypted_data


def to_int(val):
    try:
        i1 = int(val)
        return i1
    except:
        return None   
        
def is_number(test_value, type_db = '', numeric_precision = 0, numeric_scale = 0, truncate_sacale_for_bd = False):
    test_value = str(test_value)
    if test_value.isdigit():
        try:
            value_numeric = int(test_value)
        except:
            False
    elif len(test_value) > 1:
        if test_value[0] == '-' and test_value[1:].isdigit():
            try:
                value_numeric = int(test_value)
            except:
                return False
        else:
            try:
                value_numeric = float(test_value)
            except:
                return False
    else:
        return False
    
    try:
        if type_db == '':
            pass # любое число оно уже преобразовано
        if type_db == 'smallint':
            if '.' in test_value: return False
            if value_numeric < -1 * 2 ** (16 - 1) or \
               value_numeric > 2 ** (16 - 1) - 1:
                return False
        if type_db == 'integer':
            if '.' in test_value: return False
            if value_numeric < -1 * 2 ** (32 - 1) or \
               value_numeric > 2 ** (32 - 1) - 1:
                return False
        if type_db == 'bigint':
            if '.' in test_value: return False
            if value_numeric < -1 * 2 ** (64 - 1) or \
               value_numeric > 2 ** (64 - 1) - 1:
                return False
        if type_db == 'numeric':
            if '.' in test_value:
                int_str, frac_str = test_value.split('.')
            else:
                int_str = test_value
                frac_str = ''
            if truncate_sacale_for_bd and len(frac_str) > numeric_scale:
                frac_str = frac_str[:numeric_scale]
                    
            if int_str == '' or \
               len(int_str) > numeric_precision - numeric_scale or \
               len(frac_str) > numeric_scale:
                return False
    except:
        return False
    
    return True


# загружаем данные о таблице
def load_table_inf(conn, table_name = '', arr_tables_col_nastr : Class_tables_col_nastr = []):
    cur = conn.cursor()
    s1 = table_name.split('.')
    if len(s1) == 2:
        table_name_shema = s1[0]
        table_name_table = s1[1]
    else:
        table_name_shema = ''
        table_name_table = table_name
            
    sql = f'''SELECT 
                t1.column_name, 
                t1.data_type, 
                t1.character_maximum_length, 
                t1.ordinal_position,
                t1.numeric_precision, 
                t1.numeric_scale, 
                t1.numeric_precision_radix, 
                col_description('{table_name}'::regclass, t1.ordinal_position) AS description 
              FROM information_schema.columns t1 
              WHERE table_schema = '{table_name_shema}' and
                    table_name = '{table_name_table}'
              ORDER BY t1.ordinal_position; '''
    
    cur.execute(sql)
    rows = cur.fetchall()
    col = 0
    arr_columns_opisanie : Class_columns_opisanie = []
    for row in rows:
        col += 1
        columns_opisanie = Class_columns_opisanie()
        columns_opisanie.ordinal_position_new = col
        if row[0] is not None:
            columns_opisanie.column_name = row[0]
        if row[1] is not None:
            columns_opisanie.data_type = row[1]
        if row[2] is not None:
            columns_opisanie.character_maximum_length = row[2]
        if row[3] is not None:
            columns_opisanie.ordinal_position = row[3]
        if row[4] is not None:
            columns_opisanie.numeric_precision = row[4]
        if row[5] is not None:
            columns_opisanie.numeric_scale = row[5]
        if row[6] is not None:
            columns_opisanie.numeric_precision_radix = row[6]
        if row[7] is not None:
            columns_opisanie.description = row[7]
        arr_columns_opisanie.append(copy.copy(columns_opisanie))
    
    
    sql = f'''SELECT d.description
        FROM pg_class c
        JOIN pg_namespace ns ON ns.oid = c.relnamespace
        LEFT JOIN pg_description d ON d.objoid = c.oid AND d.objsubid = 0
        WHERE ns.nspname = '{table_name_shema}' AND 
              c.relname = '{table_name_table}' 
              '''
    cur.execute(sql)
    rows = cur.fetchall()
    table_description = ''
    if len(rows) > 0:
        if rows[0][0] is not None:
            table_description = rows[0][0]
    
    # дополнительная информация о позиции колонок и т.д.
    if len(arr_tables_col_nastr) > 0:
        for i, columns_opisanie in enumerate(arr_columns_opisanie):  # возвращаемое значение
            for tables_col_nastr in arr_tables_col_nastr:  # дополнительные параметры
                if columns_opisanie.column_name == tables_col_nastr.column_name:
                    arr_columns_opisanie[i].zapros_sql_combobox = tables_col_nastr.zapros_sql_combobox
                    arr_columns_opisanie[i].ordinal_position_vrem = tables_col_nastr.ordinal_position_new
                    if arr_columns_opisanie[i].zapros_sql_combobox != '':
                        arr_columns_opisanie[i].combobox_item_data = get_items_data_combobox(conn, arr_columns_opisanie[i].zapros_sql_combobox)
        # все ли позиции дял сортировок заполнены
        b_sort = True
        for i in range(len(arr_columns_opisanie)):
            if arr_columns_opisanie[i].ordinal_position_vrem == 0:
                b_sort = False
                break
        
        arr_columns_opisanie1 = []
        if b_sort: 
            for i in range(1):
                pass
            
            
    cur.close()
    
    return arr_columns_opisanie, table_description

# данные для comboBox
def get_items_data_combobox(conn, zapros_sql_combobox=''):
    #print(zapros_sql_combobox)
    cur = conn.cursor()
    cur.execute(zapros_sql_combobox)
    rows = cur.fetchall()
    
    items_data = []
    items_data.append( ( None, '' ) )
    for row in rows:
        if row[0] is not None and row[1] is not None:
            #print(row[0], row[1])
            items_data.append( ( row[0], row[1] ) )
    
    cur.close()
    conn.commit()
    
    return items_data
    