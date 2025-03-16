import os
import asyncio
import numpy as np
import cv2
import telebot
import psycopg2
from datetime import datetime
from datetime import time as dt_time
import time
import requests
import shutil
from concurrent.futures import ProcessPoolExecutor
import CalculatePeople_detect_object
import CalculatePeople_get_spisok_kamer

host_ = '109.71.243.170'
database_ = 'calc_people_camera'
user_ = 'gen_user'
password_ = 'rftk56^67'
port_ = '5432'

TOKEN = '7067388213:AAEWGOHb1uOzmlOzczYbKYx8_D5IG57W6rs'
bot = telebot.TeleBot(TOKEN)


class Konstant_class:
    name = ''
    value = ''
    
    
# проверка является ли значение числом
def is_number(test_value):
    test_value = str(test_value)
    if test_value.isdigit():
        return True
    if len(test_value) > 1:
        if test_value[0].startswith('-') and test_value[1:].isdigit():
            return True
    try:
        float(test_value)  # Пробуем преобразовать строку в число
        return True
    except ValueError:
        return False


# РАБОТА С КОНСТАНТАМИ
# получаем все константы из базы
def get_all_konstant(conn):
    konstants = []
    cur = conn.cursor()
    sql = """ select name, value
                 from public.konstant
                 """

    cur.execute(sql)
    conn.commit()
    rows = cur.fetchall()
    for row in rows:
        konstant = Konstant_class()
        konstant.name = row[0]
        konstant.value = row[1]
        konstants.append(konstant)
    cur.close()

    return konstants


# получаем значене константы
# type_out 1 - строка, 2 - число, 3 - дата
def get_konstant(konstant_name, konstants, type_out):
    for konstant in konstants:
        if konstant_name == konstant.name:
            if type_out == 1:
                return konstant.value
            elif type_out == 2:
                if is_number(konstant.value):
                    return int(konstant.value)
            elif type_out == 3:
                try:
                    return datetime.strptime(konstant.value, '%d.%m.%Y')
                except Exception as e:
                    print(f"Ошибка преобразования в дату: {e}")
                    return ''
    return ''


def add_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


# копируем картинки с камер на диск
def get_pic_from_camera(spisok_camer):
    for i, camera in enumerate(spisok_camer):
        try:
            if camera.b_video_potok:
                cap = cv2.VideoCapture(camera.url)
                ret, frame = cap.read()
                if not ret:
                    spisok_camer[i].folder_name = 'error'
                    spisok_camer[i].file_name = 'error'
                else:
                    spisok_camer[i].image = frame
                    folder_name = 'photo_camera/' + "{:04d}".format(camera.id)
                    add_folder(folder_name)
                    file_name = '{:04d}'.format(camera.id) + '_' + \
                                datetime.now().strftime('%Y-%m-%d__%H_%M_%S') + '.jpg'
                    # папка куда загружен файл
                    spisok_camer[i].folder_name = folder_name
                    spisok_camer[i].file_name = file_name
                    cv2.imwrite(folder_name + '/' + file_name, frame)
                cap.release()
                cv2.destroyAllWindows()
            else:
                headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
                        }
                response = requests.get(camera.url, stream=True, headers=headers)
                #print(kamera.url)
                #print (response.status_code)
                # Проверка успешности запроса
                if response.status_code == 200:
                    # Открытие файла для сохранения картинки
                    folder_name = 'photo_camera/' + "{:04d}".format(camera.id)
                    add_folder(folder_name)
                    file_name = '{:04d}'.format(camera.id) + '_' + \
                                datetime.now().strftime('%Y-%m-%d__%H_%M_%S') + '.jpg'
                    # папка куда загружен файл
                    spisok_camer[i].folder_name = folder_name
                    spisok_camer[i].file_name = file_name

                    image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                    
                    if img is not None:
                        # Сохраняем изображение в память
                        spisok_camer[i].image = img
                        # И также записываем на диск для будущего использования
                        with open(folder_name + '/' + file_name, 'wb') as file:
                            file.write(response.content)  # Используем content вместо raw для прямой записи
                    
#                    with open(folder_name + '/' + file_name, 'wb') as file:
#                        response.raw.decode_content = True
#                        shutil.copyfileobj(response.raw, file)
#                    
#                    spisok_camer[i].image = cv2.imread(folder_name + '/' + file_name)
                    
                else:
                    spisok_camer[i].folder_name = 'error'
                    spisok_camer[i].file_name = 'error'    
        except:
            spisok_camer[i].folder_name = 'error'
            spisok_camer[i].file_name = 'error'

# удаляем файлы картинок при превышении заданного числа
async def clear_photo_folder(spisok_camer, cnt_file):

    for camera in spisok_camer:
        if camera.folder_name != 'error':
            files = []
            for item in sorted(os.listdir(camera.folder_name)):
                if os.path.isfile(camera.folder_name + '/' + item):
                    files.append(camera.folder_name + '/' + item)
            if len(files) > cnt_file:
                for file in files[:len(files) - cnt_file]:
                    #print(file)
                    os.remove(file)


# проверка условий на необходимость направления сообщений
async def usl_send_mess(spisok_camer, konstants):
    min_inrerval_sec = get_konstant('Мин интервал оповещения - сек',
                                    konstants, 2)

    for i_cam, cam in enumerate(spisok_camer):
        for i_zona, cam_zona in enumerate(cam.camera_zonas):
            if cam_zona.cnt_object >= 0:
                # сообщение на выполнение условия превышения
                if cam_zona.usl_send_more > 0 and cam_zona.cnt_object > cam_zona.usl_send_more and \
                   (
                    (
                        cam_zona.active_st == dt_time(hour=0, minute=0, second=0) and
                        cam_zona.active_end == dt_time(hour=0, minute=0, second=0)
                    ) or
                    (
                        cam_zona.active_st <= datetime.now().time() and
                        cam_zona.active_end >= datetime.now().time()
                    )
                   ) and \
                   (
                     cam_zona.last_send_more_usl_dt == datetime(1900, 1, 1) or
                     (datetime.now() - cam_zona.last_send_more_usl_dt).total_seconds() >
                     min_inrerval_sec or
                     (cam_zona.last_send_more_norm_dt != datetime(1900, 1, 1) and
                      cam_zona.last_send_more_norm_dt > cam_zona.last_send_more_usl_dt) or
                     cam_zona.cnt_object > cam_zona.last_send_more_usl_cnt + cam_zona.usl_change_min
                   ):
                    spisok_camer[i_cam].camera_zonas[i_zona].b_add_mess_usl_more = 1
                # сообщение на выполнения условия занижения
                if cam_zona.usl_send_less > 0 and cam_zona.cnt_object < cam_zona.usl_send_less and \
                   (
                    (
                        cam_zona.active_st == dt_time(hour=0, minute=0, second=0) and
                        cam_zona.active_end == dt_time(hour=0, minute=0, second=0)
                    ) or
                    (
                        cam_zona.active_st <= datetime.now().time() and
                        cam_zona.active_end >= datetime.now().time()
                    )
                   ) and \
                   (
                     cam_zona.last_send_less_usl_dt == datetime(1900, 1, 1) or
                     (datetime.now() - cam_zona.last_send_less_usl_dt).total_seconds() >=
                     min_inrerval_sec or
                     (cam_zona.last_send_less_norm_dt != datetime(1900, 1, 1) and
                      cam_zona.last_send_less_norm_dt > cam_zona.last_send_less_usl_dt) or
                     cam_zona.cnt_object < cam_zona.last_send_less_usl_cnt - cam_zona.usl_change_min
                   ):
                    spisok_camer[i_cam].camera_zonas[i_zona].b_add_mess_usl_less = 1
                # сообщение на выполнение условия нормализации при превышении
                if cam_zona.usl_send_more > 0 and cam_zona.cnt_object <= cam_zona.usl_norm_more and \
                   cam_zona.last_send_more_usl_dt > datetime(1900, 1, 1) and \
                   (
                    (
                        cam_zona.active_st == dt_time(hour=0, minute=0, second=0) and
                        cam_zona.active_end == dt_time(hour=0, minute=0, second=0)
                    ) or
                    (
                        cam_zona.active_st <= datetime.now().time() and
                        cam_zona.active_end >= datetime.now().time()
                    )
                   ) and \
                   (
                     cam_zona.last_send_more_norm_dt == datetime(1900, 1, 1) or
                     cam_zona.last_send_more_norm_dt < cam_zona.last_send_more_usl_dt
                   ):
                    spisok_camer[i_cam].camera_zonas[i_zona].b_add_mess_usl_more_norm = 1
                # сообщение на выполнение условия нормализации при снижении
                if cam_zona.usl_send_less > 0 and cam_zona.cnt_object >= cam_zona.usl_norm_less and \
                   cam_zona.last_send_less_usl_dt > datetime(1900, 1, 1) and \
                   (
                    (
                        cam_zona.active_st == dt_time(hour=0, minute=0, second=0) and
                        cam_zona.active_end == dt_time(hour=0, minute=0, second=0)
                    ) or
                    (
                        cam_zona.active_st <= datetime.now().time() and
                        cam_zona.active_end >= datetime.now().time()
                    )
                   ) and \
                   (
                       cam_zona.last_send_less_norm_dt == datetime(1900, 1, 1) or
                       cam_zona.last_send_less_norm_dt < cam_zona.last_send_less_usl_dt
                   ):
                    spisok_camer[i_cam].camera_zonas[i_zona].b_add_mess_usl_less_norm = 1


# запись результата анализачисленности в базу
async def result_write_base(spisok_camer, conn):
    for cam in spisok_camer:
        for cam_zona in cam.camera_zonas:
            b_add_mess_usl_more, b_add_mess_usl_more_norm = False, False
            b_add_mess_usl_less, b_add_mess_usl_less_norm = False, False
            if cam_zona.b_add_mess_usl_more == 1:
                b_add_mess_usl_more = True
            if cam_zona.b_add_mess_usl_more_norm == 1:
                b_add_mess_usl_more_norm = True
            if cam_zona.b_add_mess_usl_less == 1:
                b_add_mess_usl_less = True
            if cam_zona.b_add_mess_usl_less_norm == 1:
                b_add_mess_usl_less_norm = True
    
            sql = f""" INSERT INTO camera_zona_rezult
                          (id_camera_zona, cnt_object, date_time,
                           b_add_mess_usl_more, b_add_mess_usl_more_norm,
                           b_add_mess_usl_less, b_add_mess_usl_less_norm,
                           folder_name, file_name)
                       VALUES
                          ({cam_zona.id}, {cam_zona.cnt_object}, current_timestamp,
                           {b_add_mess_usl_more}, {b_add_mess_usl_more_norm},
                           {b_add_mess_usl_less}, {b_add_mess_usl_less_norm},
                           '{cam.folder_name}', '{cam.file_name_obr}'
                           )   """
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
            cur.close()


# направляем сообщения
async def send_message(spisok_сamer, konstants, conn):
    
    # ищем шв кому отправлять
    tg_user_name = get_konstant('Адресат - Telegramm', konstants, 1)
    
    cur = conn.cursor()
    sql = f""" select tg_id
                 from public.tg_users
                 where tg_username = '{tg_user_name}'
                 """
    
    cur.execute(sql)
    conn.commit()
    rows = cur.fetchall()
    if len(rows) > 0:
        tg_id = rows[0][0]
        for cam in spisok_сamer:
            for cam_zona in cam.camera_zonas:
                if cam_zona.b_add_mess_usl_more == 1 or \
                   cam_zona.b_add_mess_usl_more_norm == 1 or\
                   cam_zona.b_add_mess_usl_less == 1 or \
                   cam_zona.b_add_mess_usl_less_norm == 1:
                    sOut = str(cam_zona.id) + ' - ' + cam_zona.name
                    sOut += ' кол-во об-тов ' + str(cam_zona.cnt_object)
                    if cam_zona.b_add_mess_usl_more == 1:
                        sOut += ' условие превышения'
                    if cam_zona.b_add_mess_usl_less == 1:
                        sOut += ' условие снижения'
                    if cam_zona.b_add_mess_usl_more_norm == 1:
                        sOut += ' возврат в норму после превышения'
                    if cam_zona.b_add_mess_usl_less_norm == 1:
                        sOut += ' возврат в норму после снижения'
                    bot.send_message(tg_id, sOut, parse_mode='html')
    
                    file_name = cam.folder_name + '/' + cam.file_name_obr
                    if os.path.exists(file_name):
                        photo = open(file_name, 'rb')
                        bot.send_photo(tg_id, photo)
                    else:
                        sOut = 'фото отсутствует'
                        bot.send_message(tg_id, sOut, parse_mode='html')

    cur.close()

    return konstants


async def run_proccess():
    # параметры соединения с базой
    conn = psycopg2.connect(
        host=host_,
        database=database_,
        user=user_,
        password=password_,
        port=port_
        )
    # получаем константы
    konstants = get_all_konstant(conn)
    
    # получаем список камер (с которых будем брать картинки)
    spisok_camer = CalculatePeople_get_spisok_kamer.get_spisok_kamer(conn)
    get_pic_from_camera(spisok_camer)
    
    # считаем кол-во людей на кадом фото
    #tasks = []
    for i in range(len(spisok_camer)):
        spisok_camer[i] = CalculatePeople_detect_object.detect_object(spisok_camer[i])
 #       print("Ставим задачу", spisok_kamer[i].id, spisok_kamer[i].name)
#        tasks.append(asyncio.create_task(find_people(spisok_kamer[i])))
   
#    with ProcessPoolExecutor(max_workers=4) as executor:
#        futures = [executor.submit(detect_object, camera) for camera in spisok_camer]
    

    # Ждём завершения всех задач и собираем результаты
    #spisok_camer = [future.result() for future in futures]

    # отрисовываем информацию на картинках и сохраняем (при необходимости)
    for i in range(len(spisok_camer)):
        spisok_camer[i] = CalculatePeople_detect_object.add_picture_ramki(spisok_camer[i])
    
    # удаляем последние файлы при превышении заданного числа
    
    cnt_file = get_konstant('Макс число картинок по камере', konstants, 2)
    
    # запускаем финальные функции в асинхронном режиме
    await asyncio.gather(
        clear_photo_folder(spisok_camer, cnt_file),
        # проверка условий на необходимость направления сообщений
        usl_send_mess(spisok_camer, konstants)
        )

    await asyncio.gather(
        # собственно направляем сообщения
        send_message(spisok_camer, konstants, conn),
        # записываем результата в базу
        result_write_base(spisok_camer, conn)
        )
    
    conn.close()
    
    # спать - и снова в работу (чтобы не замучить камеры и базу)
    sec_sleep = get_konstant('Периодичность опроса - сек', konstants, 2)
    time.sleep(sec_sleep)


# точка входа
async def main():
    while 1 == 1:
        await run_proccess()


asyncio.run(main())
