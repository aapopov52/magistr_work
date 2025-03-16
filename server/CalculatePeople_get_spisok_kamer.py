from datetime import datetime
from datetime import time as dt_time
from CalculatePeople_Class import Сamera_zona_coord_class, Сamera_zona_class, Сamera_class

# получаем список камер

# Получаем список опрашиваемых камер
def get_spisok_kamer(conn, id_camera = 0):
    cameras = []
    cur = conn.cursor()
    sql = """
        select C.id C_id,
                C.name,
                C.url,
                C.b_video_potok,
                C.b_descript_info_write,
                CZ.id CZ_id,
                CZ.name CZ_name,
                CZ.usl_send_less,
            	CZ.usl_send_more,
            	CZ.usl_change_min,
            	CZ.usl_norm_less,
            	CZ.usl_norm_more,
            	CZ.active_st,
            	CZ.active_end,
            	CZ.id_class_yolo_coco,
            	CZ.detect_object_b_write_box,
            	CZ.detect_object_b_write_contur,
            	CZ.detect_object_b_detect_main_color,
                
                CZ.contur_zona_color_r,
                CZ.contur_zona_color_g,
                CZ.contur_zona_color_b,
                
            	CZ.detect_object_box_color_r,
            	CZ.detect_object_box_color_g,
            	CZ.detect_object_box_color_b,
                CZ.detect_object_contur_color_r,
            	CZ.detect_object_contur_color_g,
            	CZ.detect_object_contur_color_b,
                
                CZ.confidence_min,
                
                t_usl_more_last.date_time last_send_more_usl_dt,
                t_usl_more_last.cnt_object last_send_more_usl_cnt,
                
                t_more_norm_last.date_time last_send_more_norm_dt,
                t_more_norm_last.cnt_object last_send_more_norm_cnt,
                
                t_usl_less_last.date_time last_send_less_usl_dt,
                t_usl_less_last.cnt_object last_send_less_usl_cnt,
                
                t_less_norm_last.date_time last_send_less_norm_dt,
                t_less_norm_last.cnt_object last_send_less_norm_cnt
        from camera C
            left join camera_zona CZ on CZ.id_camera = C.id

        left join (select tc.id_camera_zona, max(id) id_max
                     from camera_zona_rezult tc
                     where tc.b_add_mess_usl_more = True
                     group by tc.id_camera_zona) t_usl_more_last_id on
                                t_usl_more_last_id.id_camera_zona = CZ.id
          left join camera_zona_rezult t_usl_more_last on
                                t_usl_more_last.id = t_usl_more_last_id.id_max

        left join (select tc.id_camera_zona, max(id) id_max
                     from camera_zona_rezult tc
                     where tc.b_add_mess_usl_more_norm = True
                     group by tc.id_camera_zona) t_usl_more_norm_id on
                                t_usl_more_norm_id.id_camera_zona = CZ.id
        left join camera_zona_rezult t_more_norm_last on
                                t_more_norm_last.id = t_usl_more_norm_id.id_max

              left join (select tc.id_camera_zona, max(id) id_max
                     from camera_zona_rezult tc
                     where tc.b_add_mess_usl_less = True
                     group by tc.id_camera_zona) t_usl_less_last_id on
                                t_usl_less_last_id.id_camera_zona = CZ.id
          left join camera_zona_rezult t_usl_less_last on
                                t_usl_less_last.id = t_usl_less_last_id.id_max

        left join (select tc.id_camera_zona, max(id) id_max
                     from camera_zona_rezult tc
                     where tc.b_add_mess_usl_less_norm = True
                     group by tc.id_camera_zona) t_usl_less_norm_id on
                                t_usl_less_norm_id.id_camera_zona = CZ.id
          left join camera_zona_rezult t_less_norm_last on
                                t_less_norm_last.id = t_usl_less_norm_id.id_max
        where C.b_act = true and CZ.b_act = true $id_camera$
        order by C.id, CZ.id
        """

    if id_camera > 0:
        sql = sql.replace('$id_camera$', f''' and C.id = {str(id_camera)} ''')
    else:
        sql = sql.replace('$id_camera$', '')
        
    cur.execute(sql)
    rows = cur.fetchall()
    
    i_cam = -1
    i_zona = -1
    for row in rows:
        camera = Сamera_class()
        camera.id = row[0]
        camera.name = row[1]
        camera.url = row[2]
        if row[3] is not None:
            camera.b_video_potok = row[3]
        if row[4] is not None:
            camera.b_descript_info_write = row[4]
        
        camera_zona = Сamera_zona_class()
        camera_zona.boxes = []       # область с об-том
        camera_zona.confidences = [] # уверенность 
        camera_zona.class_ids = []   # класс об-та
        camera_zona.masks = []  
        camera_zona.camera_zona_coords = []
        camera_zona.results_detect = []
    
        camera_zona.id = row[5]
        if row[6] is not None:
            camera_zona.name = row[6]
        if row[7] is not None:
            camera_zona.usl_send_less = row[7]
        if row[8] is not None:
            camera_zona.usl_send_more = row[8]
        if row[9] is not None:
            camera_zona.usl_change_min = row[9]
        
        if row[10] is not None:
            camera_zona.usl_norm_less = row[10]
        if row[11] is not None:
            camera_zona.usl_norm_more = row[11]
        if row[12] is not None:
            camera_zona.active_st = row[12]
        if row[13] is not None:
            camera_zona.active_end = row[13]
        if row[14] is not None:
            camera_zona.id_class_yolo_coco = row[14]
            camera_zona.id_class_yolo_coco = camera_zona.id_class_yolo_coco.replace(' ', '')
            camera_zona.id_class_yolo_coco = camera_zona.id_class_yolo_coco.strip(",")
            if camera_zona.id_class_yolo_coco != '':
                camera_zona.id_class_yolo_coco_sp = list(map(int, camera_zona.id_class_yolo_coco.split(", ")))
            
        if row[15] is not None:
            camera_zona.detect_object_b_write_box = row[15]
        if row[16] is not None:
            camera_zona.detect_object_b_write_contur = row[16]
        if row[17] is not None:
            camera_zona.detect_object_b_detect_main_color = row[17]
        
        if row[18] is not None:
            camera_zona.contur_zona_color_r = row[18]
        if row[19] is not None:
            camera_zona.contur_zona_color_g = row[19]
        if row[20] is not None:
            camera_zona.contur_zona_color_b = row[20]
        
        if row[21] is not None:
            camera_zona.detect_object_box_color_r = row[21]
        else:
            camera_zona.detect_object_box_color_r = camera_zona.contur_zona_color_r
        if row[22] is not None:
            camera_zona.detect_object_box_color_g = row[22]
        else:
            camera_zona.detect_object_box_color_g = camera_zona.contur_zona_color_g    
        if row[23] is not None:
            camera_zona.detect_object_box_color_b = row[23]
        else:
            camera_zona.detect_object_box_color_b = camera_zona.contur_zona_color_b

        if row[24] is not None:
            camera_zona.detect_object_contur_color_r = row[24]
        else:
            camera_zona.detect_object_contur_color_r = camera_zona.contur_zona_color_r
        if row[25] is not None:
            camera_zona.detect_object_contur_color_g = row[25]
        else:
            camera_zona.detect_object_contur_color_g = camera_zona.contur_zona_color_g
        if row[26] is not None:
            camera_zona.detect_object_contur_color_b = row[26]
        else:
            camera_zona.detect_object_contur_color_b = camera_zona.contur_zona_color_b
        
        if row[27] is not None:
            camera_zona.confidence_min = row[27]
        else:
            camera_zona.confidence_min = 0.2
        if row[28] is not None:
            camera_zona.last_send_more_usl_dt = row[28]
        if row[29] is not None:
            camera_zona.last_send_more_usl_cnt = row[29]
        if row[30] is not None:
            camera_zona.last_send_more_norm_dt = row[30]
        if row[31] is not None:
            camera_zona.last_send_more_norm_cnt = row[31]
        if row[32] is not None:
            camera_zona.last_send_less_usl_dt = row[32]
        if row[33] is not None:
            camera_zona.last_send_less_usl_cnt = row[33]
        if row[34] is not None:
            camera_zona.last_send_less_norm_dt = row[34]
        if row[35] is not None:
            camera_zona.last_send_less_norm_cnt = row[35]
        
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
                i_zona = -1
                cameras[i_cam].camera_zonas = []
        
        cameras[i_cam].camera_zonas.append(camera_zona)
        i_zona = len(cameras[i_cam].camera_zonas) - 1 
        cameras[i_cam].camera_zonas[i_zona].camera_zona_coords = []
        cameras[i_cam].camera_zonas[i_zona].contours = []
        cameras[i_cam].camera_zonas[i_zona].results_detect = []
        

    id_camera_zona_s = ''
    for i_cam in range(len(cameras)):
        for i_zona in range(len(cameras[i_cam].camera_zonas)):
            if id_camera_zona_s != '': id_camera_zona_s += ', '
            id_camera_zona_s += str(cameras[i_cam].camera_zonas[i_zona].id)
    
    if id_camera_zona_s != '':
        sql = f"""
            select id_camera_zona,
                    x,
                    y
            from camera_zona_coord
            where id_camera_zona in ({id_camera_zona_s})
            order by id_camera_zona, i_num
                """
        cur.execute(sql)
        rows = cur.fetchall()
        
        i_cam = -1
        i_zona = -1
        
        for row in rows:
            camera_zona_coord = Сamera_zona_coord_class()
            camera_zona_coord.id_camera_zona = row[0]
            camera_zona_coord.x = row[1]
            camera_zona_coord.y = row[2]
            
            if i_cam >= 0 and i_zona >= 0:
                if cameras[i_cam].camera_zonas[i_zona].id != camera_zona_coord.id:
                    i_cam = -1 
                    i_zona = -1 
            if i_cam == -1 or i_zona == -1:
                for i1 in range(len(cameras)):
                    for i2 in range(len(cameras[i1].camera_zonas)):
                        if cameras[i1].camera_zonas[i2].id == camera_zona_coord.id_camera_zona:
                            i_cam = i1
                            i_zona = i2
            if i_cam >= 0 and i_zona >= 0:
                cameras[i_cam].camera_zonas[i_zona].camera_zona_coords.append(camera_zona_coord)
                cameras[i_cam].camera_zonas[i_zona].contours.append([camera_zona_coord.x, camera_zona_coord.y])
    
    cur.close()
    return cameras