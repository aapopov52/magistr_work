import os
import pickle
import sys
from PyQt5 import QtWidgets, QtCore
import psycopg2
import getpass
import Window_group 
import Password_window
import function_use

# Параметры подключения к базе данных PostgreSQL
def get_db_connection():
    """Возвращает подключение к базе данных"""

    file_param = 'connection_params.bin'
    if os.path.isfile(file_param):
        with open(file_param, 'rb') as file:
            loaded_params = pickle.load(file)

    try:
        params = {
        'dbname': loaded_params['dbname'],
        'user': loaded_params['user'],
        'password': loaded_params['password'],
        'host': loaded_params['host'],
        'port': loaded_params['port'],
        'save_password': loaded_params['save_password'],
        'table_main_shema': loaded_params['table_main_shema']
        }
    except:
        params = {
        'dbname': 'test_dwh',
        'user': '',
        'password': function_use.encrypt_data(''.encode('utf-8')),
        'host': 'vs-dwh-gpm2.st.tech',
        'port': 5432,
        'save_password': False,
        'table_main_shema': 'stage'
        }
    
    try:
        # проверяем возможность распаковки ключа (на этом ли ПК он "упакован")
        s1 = function_use.decrypt_data(params['password']).decode('utf-8')
    except:
        params['password'] = function_use.encrypt_data(''.encode('utf-8'))
        
    try:
        conn = psycopg2.connect(
                            host=params['host'],
                            database=params['dbname'],
                            user=params['user'],
                            password=function_use.decrypt_data(params['password']).decode('utf-8'),
                            port=params['port']
                            )
        return conn, params['table_main_shema']
    except:
        pass
    
    dialog = Password_window.ConnectionParametersDialog(params)
    # Выполняем диалог как модальное окно
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        # После закрытия окна получаем данные
        params = dialog.get_params()
    
    try:
        conn = psycopg2.connect(
                            host=params['host'],
                            database=params['dbname'],
                            user=params['user'],
                            password=function_use.decrypt_data(params['password']).decode('utf-8'),
                            port=params['port']
                            )
    except:
        return None, None
        
    if not params['save_password']:
        params['password'] = function_use.encrypt_data(''.encode('utf-8'))
    
    with open(file_param, 'wb') as file:
        pickle.dump(params, file)
    
    try:
        cur = conn.cursor()
        cur.execute(f''' SELECT id, num_1, num_2, num_3, name, b_act
                    FROM {params['table_main_shema']}.interface_forms
                    limit 1
                ''')
        result = cur.fetchone()
        cur.close()
        conn.commit()
    except:
        cur.close()
        conn.close()
        return None, None
    
    return conn, params['table_main_shema']
    
    
def main():
    app = QtWidgets.QApplication(sys.argv)
    conn, table_main_shema = get_db_connection()
    if conn is None:
        QtWidgets.QMessageBox.critical(None, "Ошибка подключения", "Подключиться к базе не удалось.")
        return

    # Получаем соединение с базой данных PostgreSQL
    main_window = Window_group.Class_Windowgroup(conn, table_main_shema)
    main_window.show()
    
    exit_code = app.exec_()
    conn.close()
    sys.exit(exit_code)

main()