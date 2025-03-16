import os
import psycopg2
from datetime import datetime


host_ = '109.71.243.170'
database_ = 'calc_people_camera'
user_ = 'gen_user'
password_ = 'rftk56^67'
port_ = '5432'


# включаем пользователя в список
def insert_user_into_spisok(message):
    conn = psycopg2.connect(
        host=host_,
        database=database_,
        user=user_,
        password=password_,
        port=port_
        )

    sql = f"""do $$
               declare id1 integer;
               declare tg_username1 varchar;
               begin
                 id1:= null;
                 select id, tg_username into id1, tg_username1
                 from tg_users where tg_id = '{message.from_user.id}';

                if id1 is null then
                  insert into tg_users(tg_id, tg_username)
                              values ({message.from_user.id},
                                      '{message.from_user.username}');
                end if;

                if id1 is not null and tg_username1 <>
                                    '{message.from_user.username}' then
                     update tg_users set tg_username =
                                     '{message.from_user.username}'
                     where id = id1;
                end if;

                end $$;   """

    cur = conn.cursor()
    cur.execute(sql)
    cur.close()
    conn.commit()
    conn.close()


# выводим список объектов
def get_spisok_kamer():
    # параметры соединения с базой
    conn = psycopg2.connect(
        host=host_,
        database=database_,
        user=user_,
        password=password_,
        port=port_
        )

    sql = '''select c.id, c.name, url 
            from camera c
            order by c.id'''
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    sOut = ''
    for row in rows:
        if row[0] is not None and row[1] is not None:
            if sOut != '':
                sOut += '\n'
            sOut += str(row[0]) + ' - ' + row[1]

    cur.close()
    conn.close()

    return sOut


class Camera_zona_info_class:
    id = 0
    name = ''
    id_class = ''
    cnt_object = 0
    id_class_yolo_coco = ''


class Camera_info_class:
    id = 0
    name = ''
    photo_datetime = datetime(1900, 1, 1)
    photo = ''
    camera_zonas = []
    file_name = ''


# выводим список фото объектов
def get_photos_kamer(bot, message):
    # параметры соединения с базой
    conn = psycopg2.connect(
        host=host_,
        database=database_,
        user=user_,
        password=password_,
        port=port_
        )

    sql = """ select C.id, C.name, CZ.id, CZ.name, t_photo.cnt_object, t_photo.date_time,
                     t_photo.folder_name || '/' || t_photo.file_name,
                     CZ.id_class_yolo_coco
                from public.camera C
                left join public.camera_zona CZ on CZ.id_camera = C.id
                left join (select tc.id_camera_zona, max(id) id_max
                             from camera_zona_rezult tc
                             group by tc.id_camera_zona) t_last_id on
                          t_last_id.id_camera_zona = CZ.id
                left join camera_zona_rezult t_photo on
                          t_photo.id = t_last_id.id_max
                where C.b_act = true and CZ.b_act = true
              """
    if message.text.lower() not in ['*', 'all', 'все', 'всё']:
        sql += f""" and C.id = {message.text} """
    sql += """ ORDER BY C.id, CZ.id """

    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    
    cameras = []
    i_cam = -1
    if len(rows) == 0:
        sOut = 'Записи отсутсвуют - указан неверный номер'
        bot.send_message(message.chat.id, sOut, parse_mode='html')
    for row in rows:
        camera = Camera_info_class()
        camera.camera_zonas = []
        if row[0] is not None:
            camera.id = row[0]
        if row[1] is not None:
            camera.name = row[1]
        
        camera_zona = Camera_zona_info_class()
        if row[2] is not None:
            camera_zona.id = row[2]
        if row[3] is not None:
            camera_zona.name = row[3]
        if row[4] is not None:
            camera_zona.cnt_object = row[4]
        if row[5] is not None:
            camera.photo_datetime = row[5]
        if row[6] is not None:
            camera.file_name = row[6]
        if row[7] is not None:
            camera_zona.id_class_yolo_coco = row[7]
        else:
            camera_zona.id_class_yolo_coco = 'все'
        
        if i_cam >= 0:
            if cameras[i_cam].id != camera.id:
                i_cam = -1
        
        if i_cam == -1:
            for i1 in range(len(cameras)):
                if cameras[i1].id == camera.id:
                    i_cam = i1
                    break
            if i_cam == -1:
                cameras.append(camera)
                i_cam = len(cameras) - 1
                cameras[i_cam].camera_zonas = []
        
        cameras[i_cam].camera_zonas.append(camera_zona)
        
    for cam in cameras:
        sOut = f'''Камера {str(cam.id)} - {cam.name} - снято {camera.photo_datetime.strftime("%d.%m.%Y %H:%M:%S")}. Зоны:'''
        for cam_zona in cam.camera_zonas:
            sOut += f'''\nЗона {str(cam_zona.id)} - {cam_zona.name} - классы об-тов {cam_zona.id_class_yolo_coco}, кол-во об-тов {cam_zona.cnt_object}.'''
        
        bot.send_message(message.chat.id, sOut, parse_mode='html')
        
        if os.path.exists(cam.file_name):
            photo = open(cam.file_name, 'rb')
            bot.send_photo(message.chat.id, photo)
        else:
            sOut = 'фото отсутствует'
            bot.send_message(message.chat.id, sOut, parse_mode='html')
        
    cur.close()
    conn.close()

    return sOut


# проверка - является ли числом
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
