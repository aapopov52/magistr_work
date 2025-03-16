from datetime import datetime
from datetime import time as dt_time

class Сamera_zona_coord_class:
    id = 0
    x = 0
    y = 0
    
    
class Result_detection_class:
    id_camera_zona = None # зона первого появления - для трекинга
    box = None       # область с об-том
    confidence = None # уверенность 
    class_id = None   # класс об-та
    mask_np = None      # маски объектов   
    track_id = None   # УН трека
    
    
class Сamera_zona_class:
    # из базы
    id = 0
    name = ''
    opisanie = ''
    usl_send_less = 0   # сообщение уйдёт если значение будет меньше заданного
    usl_send_more = 0   # сообщение уйдёт если значение будет больше заданного
    usl_change_min = 0  # ухудшение ситуации на величину
    usl_norm_less = 0   # нормализация условий после снижения
    usl_norm_more = 0   # нормализация условий псле превышения
    active_st = dt_time(hour=0, minute=0, second=0)  # начало действия
    active_end = dt_time(hour=0, minute=0, second=0)  # окончание действия
    id_class_yolo_coco = ''
    id_class_yolo_coco_sp = []
    detect_object_b_write_box = False
    detect_object_b_write_contur = False
    detect_object_b_detect_main_color = False
    detect_object_box_color_r = 0
    detect_object_box_color_g = 0
    detect_object_box_color_b = 0
    detect_object_contur_color_r = 0
    detect_object_contur_color_g = 0
    detect_object_contur_color_b = 0
    contur_zona_color_r = 0
    contur_zona_color_g = 0
    contur_zona_color_b = 0
    confidence_min = 0 # минимальная увереность при обнаружении объекта
   
    cnt_object = 0      # кол-во объектов в зоне
    # условия на собщения
    # условия на превышение
    last_send_more_usl_dt = datetime(1900, 1, 1)   # посл сообщ по условиям
    last_send_more_usl_cnt = 0   # количество людей в последнем сообщении
    last_send_more_norm_dt = datetime(1900, 1, 1)  # посл сообщ по нормал
    last_send_more_norm_cnt = 0  # кол-во лиц в последнем сообщении по нормал
    # условия на снижение
    last_send_less_usl_dt = datetime(1900, 1, 1)   # посл сообщ по условиям
    last_send_less_usl_cnt = 0   # количество людей в последнем сообщении
    last_send_less_norm_dt = datetime(1900, 1, 1)  # посл сообщ по нормал
    last_send_less_norm_cnt = 0  # кол-во лиц в последнем сообщении по нормал
    # Создать сообщения для услолвия превышения:
    b_add_mess_usl_more = 0       # создать сообщение для условия превышения
    b_add_mess_usl_more_norm = 0  # создать сообщение о нормализации
    # Создать сообщения для услолвия снижения:
    b_add_mess_usl_less = 0       # создать сообщение для условия превышения
    b_add_mess_usl_less_norm = 0  # создать сообщение о нормализации
    camera_zona_coords = []     # точки зон
    contours = []               # контуры зон ()
    results_detect : Result_detection_class = [] # мгновенная детекция
    
class Сamera_class:
    id = 0
    name = ''
    url = ''
    b_video_potok = False # загружаем видео-поток (не картинка)
    folder_name = ''
    file_name = ''
    file_name_obr = ''  # имя обработанного файла (посчитаны объекты) )
    b_descript_info_write = False
    camera_zonas = []
    image = 0
    image_result = 0
    b_tracking = False # трэкинг
    
    # все об-ты, что нашли на интерации
    results_detect_interation = []
    # обнаруженные об-ты - для трэкинга
    results_detect_tracking = []
    