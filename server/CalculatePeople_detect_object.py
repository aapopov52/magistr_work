import os
import cv2
from ultralytics import YOLO
from sklearn.cluster import KMeans
import numpy as np
import copy
#import torch
#from byte_tracker.byte_tracker_model import BYTETracker as ByteTracker
from PIL import Image, ImageDraw, ImageFont
from CalculatePeople_Class import Сamera_zona_coord_class, Сamera_zona_class, Сamera_class, Result_detection_class
#from Tracker_class import Tracker_class

# анализ изображения

#model_yolo = YOLO('YOLOv8n.pt') # детекция

# модели с сегментацией
#YOLOv8n (nano): минимальная модель, самая быстрая, но с наименьшей точностью.
#YOLOv8s (small)
#YOLOv8m (medium)
#YOLOv8l (large)
#YOLOv8x (extra-large): самая большая и самая точная модель, но медленнее всех.
model_yolo = YOLO('yolov8l-seg.pt')  # Модель с сегментацией - самая малая


model_yolo_classes = {
    0: "Человек", 1: "Велосипед", 2: "Автомобиль", 3: "Мотоцикл", 4: "Самолет", 5: "Автобус",
    6: "Поезд", 7: "Грузовик", 8: "Лодка", 9: "Светофор", 10: "Пожарный гидрант", 11: "Знак STOP",
    12: "Паркомат", 13: "Скамейка", 14: "Птица", 15: "Кошка", 16: "Собака", 17: "Лошадь",
    18: "Овца", 19: "Корова", 20: "Слон", 21: "Медведь", 22: "Зебра", 23: "Жираф",
    24: "Рюкзак", 25: "Зонт", 26: "Сумка", 27: "Галстук", 28: "Чемодан", 29: "Фрисби",
    30: "Лыжи", 31: "Сноуборд", 32: "Мяч", 33: "Воздушный змей", 34: "Бейсбольная бита",
    35: "Бейсбольная перчатка", 36: "Скейтборд", 37: "Серфборд", 38: "Теннисная ракетка",
    39: "Бутылка", 40: "Бокал", 41: "Чашка", 42: "Вилка", 43: "Нож", 44: "Ложка",
    45: "Миска", 46: "Банан", 47: "Яблоко", 48: "Сэндвич", 49: "Апельсин", 50: "Брокколи",
    51: "Морковь", 52: "Хот-дог", 53: "Пицца", 54: "Пончик", 55: "Торт", 56: "Стул",
    57: "Диван", 58: "Растение", 59: "Кровать", 60: "Обеденный стол", 61: "Туалет",
    62: "Телевизор", 63: "Ноутбук", 64: "Мышь", 65: "Пульт", 66: "Клавиатура",
    67: "Телефон", 68: "Микроволновка", 69: "Духовка", 70: "Тостер", 71: "Раковина",
    72: "Холодильник", 73: "Книга", 74: "Часы", 75: "Ваза", 76: "Ножницы", 77: "Плюшевый мишка",
    78: "Фен", 79: "Зубная щетка"
    }


# функция по выделению объектов на картинке
def detect_object(camera : Сamera_class):
    if camera.file_name == 'error':
        for camera_zona in camera.camera_zonas:
            camera_zona.cnt_object = -1
        return camera
    
    camera.results_detect_interation = []
    for i in range(len(camera.camera_zonas)):
        camera.camera_zonas[i].results_detect = []
        camera.camera_zonas[i].cnt_object = 0
    
    # ДЕТЕКЦИЯ
    results = model_yolo(source=camera.image,  
                        imgsz=max(camera.image.shape[:2])   )  # максимальный из размеров входного изображения (оригинальный размер)
    
    
    # формируем два списка:
    # все об-ты, подходящие под любую из зон
    # 
    for r in results:
        for box_num, box in enumerate(r.boxes):
            b_insert = False
            class_id = int(box.cls[0])  # Класс (0 - человек, 2 - авто ...)
            confidence = float(box.conf[0])
            for camera_zona in camera.camera_zonas:
                if (class_id in camera_zona.id_class_yolo_coco_sp or len(camera_zona.id_class_yolo_coco_sp) == 0) and \
                                confidence > camera_zona.confidence_min:  # Если обнаружен искомые об-ты с определённой вероятностью
                    
                    
                    x1, y1, x2, y2 = map(int, box.xyxy[0])  # Верхний левый и нижний правый угол
                    if len(camera_zona.contours) > 0:
                        contour = np.array(camera_zona.contours, dtype=np.int32)
                        contour = contour.reshape((-1, 1, 2))
                        # определяем находится ли центр объекта в контуре
                        x = int((x1 + x2) / 2)
                        y = int((y1 + y2) / 2)
                        in_contur = cv2.pointPolygonTest(contour, (x, y), False)
                        #- `> 0` → Точка внутри контура.
                        #- `= 0` → Точка на границе контура.
                        #- `< 0` → Точка снаружи контура.
                    else:
                        # если котнтуры зоны не определены, то считаем все об-ты в зоне
                        in_contur = 1
                        
                    result_detection = Result_detection_class()
                    result_detection.id_camera_zona = camera_zona.id
                    result_detection.box = [x1, y1, x2, y2]
                    result_detection.confidence = float(confidence)
                    result_detection.class_id = class_id
                    
                    # т.к. Йола перед обработкой изменяет размер избражения, координаты в масках отличаются от исходных
                    # Получаем текущую маску в формате тензора
                    # masks исползуется в модели сегментации для отрисовки контуров объектов
                    mask_tensor = r.masks.data[box_num]  # Текущая маска как PyTorch Tensor
                    
                    # Конвертируем тензор в NumPy
                    mask_np = mask_tensor.cpu().numpy().astype('uint8')  # Преобразуем в NumPy массив (uint8)
                    
                    
                    # Меняем размер маски, чтобы он соответствовал исходному изображению
                    result_detection.mask_np = cv2.resize(
                        mask_np,
                        (camera.image.shape[1], camera.image.shape[0]),  # размеры: (width, height)
                        interpolation=cv2.INTER_NEAREST  # Используем ближайший сосед для корректной маски
                        )
                    
                    # добавляем для расчёта трекинга (зоны могут накладываться, следим, чтобы об-т попал 1 раз)
                    if not b_insert:
                        camera.results_detect_interation.append(copy.deepcopy(result_detection))
                        b_insert = True
                    
                    # добавляем в "мгновенную" картину по каждой зоне
                    if in_contur >= 0:
                        camera_zona.cnt_object += 1
                        camera_zona.results_detect.append(copy.deepcopy(result_detection))
    
    return camera
    
   
#----------------------------------------------------------------------------------------------------------------------------------
# ТРЕКИНГ
#def track_object(camera : Сamera_class, tracker : Tracker_class):
#    
#    detections_list = generate_list_for_tracker(camera)
#    #deep_sort
#    tracker.update(camera.image, detections_list)
#    
#    camera.results_detect_interation = []
#    for inum, track in enumerate(tracker.tracks):
#        camera.results_detect_interation[inum].track_id = track.track_id
#        
#    return camera
    
def generate_list_for_tracker(camera : Сamera_class):
    # Приведение данных в правильную форму для трекера
    detections_list = []
    
    for results_detect in camera.results_detect_interation:

            merged_detection = [
                results_detect.box[0],
                results_detect.bbox[1],
                results_detect.bbox[2],
                results_detect.bbox[3],
                results_detect.confidence#,
                #results_detect.class_id,
            ]

            detections_list.append(merged_detection)

    if len(detections_list) == 0:
        detections_list = np.empty((0, 6))
            
    return np.array(detections_list)
    


#----------------------------------------------------------------------------------------------------------------------------------
# ПОДПИСИ НА КАРТИНКЕ
def add_picture_ramki(camera : Сamera_class, b_save_result = True):
     # ОТРИСОВКА Р
    image_result = camera.image.copy() # отдельный объект для отрисовки
    #indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    font = cv2.FONT_HERSHEY_PLAIN
    slabel = ''
    max_x_main_label = 0
    
    font_path = "arial.ttf" # шрифт для подписей на русском
    if not camera.b_tracking: # если без трекинга
        for i_cam_num, camera_zona in enumerate(camera.camera_zonas):
            if len(camera_zona.contours) > 0:
                contour = np.array(camera_zona.contours, dtype=np.int32)
                contour = contour.reshape((-1, 1, 2))
                
                cv2.drawContours(image_result, [contour], -1, (camera_zona.contur_zona_color_b, 
                                                               camera_zona.contur_zona_color_g, 
                                                               camera_zona.contur_zona_color_r), 2)
            
            for i in range(len(camera_zona.results_detect)):
                #if i in indexes:
                slabel = model_yolo_classes.get(camera_zona.results_detect[i].class_id, f'''класс {str(camera_zona.results_detect[i].class_id)}''') + ' '
                x1, y1, x2, y2 = camera_zona.results_detect[i].box
                if camera_zona.detect_object_b_write_box: # код для отрисовки прямоугольника
                    cv2.rectangle(image_result, (x1, y1), (x2, y2), (camera_zona.detect_object_box_color_b, 
                                                                     camera_zona.detect_object_box_color_g, 
                                                                     camera_zona.detect_object_box_color_r), 2)
                
                #if kamera.id_class_yolo_coco == 0: slabel = 'person'
                if camera_zona.detect_object_b_write_contur: # код для отрисовки контура
                    mask_np = camera_zona.results_detect[i].mask_np
                    # Находим контуры
                    contours, _ = cv2.findContours(mask_np, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    # Рисуем контуры на изображении
                    for contour in contours:
                        cv2.drawContours(image_result, [contour], -1, (camera_zona.detect_object_contur_color_b, 
                                                                       camera_zona.detect_object_contur_color_g, 
                                                                       camera_zona.detect_object_contur_color_r), 2)
                
                if camera_zona.detect_object_b_detect_main_color: # код для детекции основного цвета
                    mask_np = camera_zona.results_detect[i].mask_np
                    # Находим контуры
                    contours, _ = cv2.findContours(mask_np, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    binary_mask = np.zeros(mask_np.shape, dtype=np.uint8)
                    # Рисуем полигон, заполняя его белым цветом на бинарной маске
                    cv2.drawContours(binary_mask, contours, -1, 255, thickness=cv2.FILLED)
                    
                    # Находим координаты всех ненулевых точек (т.е., внутри контура)
                    points = np.column_stack(np.where(binary_mask > 0))  # Строки и столбцы ненулевых пикселей
                    image_object = np.zeros_like(camera.image)
                    # Распаковываем координаты points (строки и столбца)
                    rows, cols = points[:, 0], points[:, 1]
                    # Заполняем только нужные точки из исходного изображения
                    #print ('image_object.shape=', image_object.shape, ', image.shape=', image.shape, ', rows.max=', rows.max(), ', cols.max=', cols.max(), ', mask_np.shape=', mask_np.shape)
                    image_object[rows, cols] = camera.image[rows, cols]
                    
                    #cv2.imwrite('tmp/' + kamera.file_name[:-4] + '_' + datetime.now().strftime('%Y-%m-%d__%H_%M_%S') + '_' + str(i) + '.jpg', image_object[y1:y2, x1:x2])
                        
                    pixels_cnt, sp_color_car_rgb, sp_cnt = get_color_car(image_object, camera, rows, cols) # функция для определения цвета авто
                    #image_object[y1:y2, x1:x2]
                    
                    cv2.rectangle(image_result, (x2, y1), (x2 + 20, y1 + 20), sp_color_car_rgb[0][::-1], -1)
                    cv2.rectangle(image_result, (x2, y1 + 20), (x2 + 20, y1 + 40), sp_color_car_rgb[1][::-1], -1)
                    cv2.rectangle(image_result, (x2, y1 + 40), (x2 + 20, y1 + 60), sp_color_car_rgb[2][::-1], -1)
                    
#                    font = ImageFont.truetype(font_path, 15)  # Размер шрифта
#                    s1 = f" {cnt} ({cnt / pixels_cnt * 100:.0f}%) RGB({color_car_rgb[0]}, {color_car_rgb[1]}, {color_car_rgb[2]})"
#                    cv2.putText(image_result, s1, (x2 + 25, y1 + 20), font, 1, (255, 0, 0), 2)
#                    s1 = f" {cnt_1} ({cnt_1 / pixels_cnt * 100:.0f}%) RGB({color_car_rgb_1[0]}, {color_car_rgb_1[1]}, {color_car_rgb_1[2]})"
#                    cv2.putText(image_result, s1, (x2 + 25, y1 + 40), font, 1, (255, 0, 0), 2)
#                    s1 = f" {cnt_2} ({cnt_2 / pixels_cnt * 100:.0f}%) RGB({color_car_rgb_2[0]}, {color_car_rgb_2[1]}, {color_car_rgb_2[2]})"
#                    cv2.putText(image_result, s1, (x2 + 25, y1 + 60), font, 1, (255, 0, 0), 2)
                    for i_ in range(len(sp_cnt)):
                        s1 = f" {sp_cnt[i_]} ({sp_cnt[i_] / pixels_cnt * 100:.0f}%) RGB({sp_color_car_rgb[i_][0]}, {sp_color_car_rgb[i_][1]}, {sp_color_car_rgb[i_][2]})"
                        image_result = write_text(image = image_result, 
                                          font_path = font_path, 
                                          font_size = 15, 
                                          s_text = s1,
                                          x=x2 + 25,
                                          y=y1 + 20 * (i_ + 1), 
                                          color_r=camera_zona.detect_object_contur_color_r, 
                                          color_g=camera_zona.detect_object_contur_color_g, 
                                          color_b=camera_zona.detect_object_contur_color_b)
                    
                    rgb_text = f" {pixels_cnt} RGB({sp_color_car_rgb[0][0]}, {sp_color_car_rgb[0][1]}, {sp_color_car_rgb[0][2]})"
                
                slabel = slabel + str(round(camera_zona.results_detect[i].confidence, 2))
                
                if camera_zona.detect_object_b_detect_main_color == 2:
                    slabel =  slabel + rgb_text
                #print(slabel)
#                
#                # подписи к объектам на родном языке
#                image_pil = Image.fromarray(cv2.cvtColor(image_result, cv2.COLOR_BGR2RGB))
#                
#                font = ImageFont.truetype(font_path, 15)  # Размер шрифта
#                draw = ImageDraw.Draw(image_pil)
#                # подпись к сгенерированной области
#                draw.text((x1, y1 - 15), slabel, font=font, fill=(camera_zona.detect_object_box_color_r, 
#                                                                  camera_zona.detect_object_box_color_g, 
#                                                                  camera_zona.detect_object_box_color_b))
#                image_result = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
                
                image_result = write_text(image = image_result, 
                                          font_path = font_path, 
                                          font_size = 15, 
                                          s_text = slabel,
                                          x=x1,
                                          y=y1 - 15, 
                                          color_r=camera_zona.detect_object_box_color_r, 
                                          color_g=camera_zona.detect_object_box_color_g, 
                                          color_b=camera_zona.detect_object_box_color_b)
                                
            
            # эта штука нужна для расчёта белого прямоугольника под надписями
            if camera.b_descript_info_write:
                y1 = 15 + 20 * i_cam_num
                image_pil = Image.fromarray(cv2.cvtColor(image_result, cv2.COLOR_BGR2RGB))
                font = ImageFont.truetype(font_path, 15)  # Размер шрифта
                draw = ImageDraw.Draw(image_pil)
                slabel = f'''{str(i_cam_num)} {camera_zona.name} - {camera_zona.cnt_object} объект(-f, -ов)'''
                bbox = draw.textbbox((15, y1), slabel, font=font)
                if max_x_main_label < bbox[2] + 2: max_x_main_label = bbox[2] + 2
        
        # подписи к картинке на родном языке
        if camera.b_descript_info_write:
            cv2.rectangle(image_result, (15-2, 15-2), (max_x_main_label + 2, 15 + 20 * len(camera.camera_zonas) + 2), 
                          [255,255,255], -1)
            
            for i_cam_num, camera_zona in enumerate(camera.camera_zonas):               
                image_result = write_text(image = image_result, 
                                          font_path = font_path, 
                                          font_size = 15, 
                                          s_text = f'''{str(i_cam_num)} {camera_zona.name} - {camera_zona.cnt_object} объектов''', 
                                          x = 15,  
                                          y=15 + 20 * i_cam_num, 
                                          color_r=camera_zona.contur_zona_color_r, 
                                          color_g=camera_zona.contur_zona_color_g, 
                                          color_b=camera_zona.contur_zona_color_b)
                    
                    
#                image_pil = Image.fromarray(cv2.cvtColor(image_result, cv2.COLOR_BGR2RGB))
#                font = ImageFont.truetype(font_path, 15)  # Размер шрифта
#                draw = ImageDraw.Draw(image_pil)
#                # подпись к сгенерированной области
#                slabel = 
#                y1 = 
#                draw.text((15, y1), slabel, font=font, fill=(, 
#                                                             , 
#                                                             ))
#                image_result = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)    
            
                #cv2.putText(image_result, slabel, (x1, y1), font, 1, (255, 0, 0), 2)
    else: # если трекинг
        for results_detect in camera.results_detect_interation:
            slabel = f'''трэк {results_detect.track_id} - ''' 
            slabel += model_yolo_classes.get(results_detect.class_id, f'''класс {str(results_detect.class_id)}''')
            x1, y1, x2, y2 = camera_zona.results_detect[i].box
            if camera_zona.detect_object_b_write_box: # код для отрисовки прямоугольника
                cv2.rectangle(image_result, (x1, y1), (x2, y2), (250, 
                                                                 0, 
                                                                 0), 2)        
#            # подписи к объектам на родном языке
#            image_pil = Image.fromarray(cv2.cvtColor(image_result, cv2.COLOR_BGR2RGB))
#            font_path = "arial.ttf"  
#            font = ImageFont.truetype(font_path, 15)  # Размер шрифта
#            draw = ImageDraw.Draw(image_pil)
#            # подпись к сгенерированной области
#            draw.text((x1, y1 - 15), slabel, font=font, fill=(250, 
#                                                              0, 
#                                                              0))
#            image_result = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
                
            image_result = write_text(image = image_result, 
                                          font_path = font_path, 
                                          font_size = 15, 
                                          s_text = slabel, 
                                          x = 15,  
                                          y=15 + 20 * i_cam_num, 
                                          color_r=0, 
                                          color_g=0, 
                                          color_b=250)
                
                
    camera.image_result = image_result
    # Сохраняем изображение
    if b_save_result:
        file_name_new = camera.file_name[:-4] + '_'
        prefix = ''
        i = 0
        while os.path.exists(camera.folder_name + '/' +
                             file_name_new + prefix + '.jpg'):
            i += 1
            prefix = '_' + str(i)
        
        camera.file_name_obr = file_name_new + prefix + '.jpg'
        cv2.imwrite(camera.folder_name + '/' + camera.file_name_obr, image_result)
    
        camera.file_name_obr = camera.file_name_obr
        
    return camera
    
# Пишем текст на картинке
def write_text(image, font_path, font_size, s_text, x,  y, color_r, color_g, color_b):
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    font = ImageFont.truetype(font_path, font_size)  # Размер шрифта
    draw = ImageDraw.Draw(image_pil)
    # подпись к сгенерированной области
    draw.text((x, y), s_text, font=font, fill=(color_r, color_g, color_b))
    image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR) 
    
    return image
                
# находим цвет авто
def get_color_car(image, kamera, rows, cols):
    
    # Преобразуем изображение в цветовую модель LAB
    filtered_lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    # сглаживаем изображение
    filtered_lab = cv2.medianBlur(filtered_lab, 5)  # Применяем медианный фильтр
    # оставляем точки, входящие в rows, cols
    
    # Преобразуем пиксели в одномерный массив для кластеризации
    #pixels = filtered_lab.reshape((-1, 3))
    pixels = filtered_lab[rows, cols]
    pixels = np.float32(pixels)
    # цвет должен быть "осовным", поэтому боьшоре количество кластеров будет избыточным
    # попробуем 5
    kmeans = KMeans(n_clusters=4, random_state=42)
    kmeans.fit(pixels)
    
    # Вычислим количество точек в каждом кластере
    labels, counts = np.unique(kmeans.labels_, return_counts=True)
    sorted_indices = np.argsort(-counts)  # Индексы кластеров, отсортированные по убыванию
    pixels_cnt = counts.sum()
    
    dominant_cluster = sorted_indices[0]  # Индекс крупнейшего кластера
    dominant_cluster_cnt = counts[dominant_cluster]
    dominant_color = kmeans.cluster_centers_[dominant_cluster]
    dominant_color_bgr = cv2.cvtColor(np.uint8([[dominant_color]]), cv2.COLOR_LAB2BGR)[0][0]
    dominant_color_rgb = cv2.cvtColor(np.uint8([[dominant_color_bgr]]), cv2.COLOR_BGR2RGB)[0][0]
    
    dominant_cluster_1_cnt = 0
    dominant_color_rgb_1 = np.array([0, 0, 0]) 
    
    dominant_cluster_2_cnt = 0
    dominant_color_rgb_2 = np.array([0, 0, 0]) 
    
    if len(sorted_indices) >= 2:
        dominant_cluster_1 = sorted_indices[1]  # Индекс второго по величине кластера
        dominant_cluster_1_cnt = counts[dominant_cluster_1]
        dominant_color_1 = kmeans.cluster_centers_[dominant_cluster_1]
        dominant_color_bgr_1 = cv2.cvtColor(np.uint8([[dominant_color_1]]), cv2.COLOR_LAB2BGR)[0][0]
        dominant_color_rgb_1 = cv2.cvtColor(np.uint8([[dominant_color_bgr_1]]), cv2.COLOR_BGR2RGB)[0][0]
    
    if len(sorted_indices) >= 3:
        dominant_cluster_2 = sorted_indices[2]  # Индекс второго по величине кластера
        dominant_cluster_2_cnt = counts[dominant_cluster_2]
        dominant_color_2 = kmeans.cluster_centers_[dominant_cluster_2]
        dominant_color_bgr_2 = cv2.cvtColor(np.uint8([[dominant_color_2]]), cv2.COLOR_LAB2BGR)[0][0]
        dominant_color_rgb_2 = cv2.cvtColor(np.uint8([[dominant_color_bgr_2]]), cv2.COLOR_BGR2RGB)[0][0]
    
    # Возвращаем цвет кластера
    sp_color_car_rgb = [tuple(map(int, dominant_color_rgb)), tuple(map(int, dominant_color_rgb_1)), tuple(map(int, dominant_color_rgb_2))]
    sp_cnt = [dominant_cluster_cnt, dominant_cluster_1_cnt, dominant_cluster_2_cnt]
    return pixels_cnt, sp_color_car_rgb, sp_cnt
