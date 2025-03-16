INSERT INTO public.interface_forms (num_1,num_2,num_3,"name",b_act) VALUES
	 (1,NULL,NULL,'Управление',true),
	 (1,1,NULL,'Список форм',true),
	 (2,NULL,NULL,'Настройки',true),
	 (NULL,NULL,NULL,NULL,NULL),
	 (2,1,NULL,'Константы',true),
	 (2,2,NULL,'Камеры',true),
	 (3,1,NULL,'Камеры - объекты',true),
	 (3,NULL,NULL,'Результаты',true);
INSERT INTO public.interface_forms_tables (id_interface_forms,num,table_name,col_id_name,order_uslovie,row_limit,left_,top_,width_,heigth_,b_read_only) VALUES
	 (6,1,'public.camera','id','id',1000,10,10,1410,310,NULL),
	 (6,2,'public.camera_zona','id','name',1000,10,320,1410,310,NULL),
	 (6,3,'public.camera_zona_coord','id','id',1000,10,640,705,310,NULL),
	 (8,1,'public.camera','id','id',1000,10,10,705,310,true),
	 (8,2,'public.camera_zona','id','name',1000,710,10,705,310,true),
	 (2,1,'public.interface_forms','id','coalesce(num_1, 0), coalesce(num_2, 0), coalesce(num_3, 0)',1000,10,10,1410,310,NULL),
	 (2,2,'public.interface_forms_tables','id','coalesce(num, 0)',1000,10,320,705,310,NULL),
	 (8,3,'public.camera_zona_rezult','id','id desc',10000,10,320,1410,630,true),
	 (2,4,'public.interface_forms_tables_command','id','coalesce(num, 0)',1000,710,640,705,310,NULL),
	 (2,3,'public.interface_forms_tables_col_nastr','id','coalesce(ordinal_position_new, 0)',1000,710,320,705,310,NULL);
INSERT INTO public.interface_forms_tables (id_interface_forms,num,table_name,col_id_name,order_uslovie,row_limit,left_,top_,width_,heigth_,b_read_only) VALUES
	 (2,5,'public.interface_forms_tables_sviaz','id','coalesce(num, 0)',1000,10,640,705,310,NULL),
	 (5,1,'public.konstant','id','coalesce(num_1,0), coalesce(num_2,0)',1000,10,10,800,930,false);
INSERT INTO public.interface_forms_tables_col_nastr (id_interface_forms_tables,col_name,ordinal_position_new,zapros_sql_combobox) VALUES
	 (1,'id',1,NULL),
	 (1,'num_1',2,NULL),
	 (1,'num_2',3,NULL),
	 (1,'num_3',4,NULL),
	 (1,'name',5,NULL),
	 (1,'b_act',6,NULL),
	 (6,'id',1,NULL),
	 (6,'num_1',2,NULL),
	 (6,'num_2',3,NULL),
	 (6,'name',4,NULL);
INSERT INTO public.interface_forms_tables_col_nastr (id_interface_forms_tables,col_name,ordinal_position_new,zapros_sql_combobox) VALUES
	 (6,'value',5,NULL),
	 (7,'id',1,NULL),
	 (7,'name',2,NULL),
	 (7,'url',3,NULL),
	 (7,'opisanie',9,NULL),
	 (7,'b_video_potok',13,NULL),
	 (7,'b_act',14,NULL),
	 (7,'b_descript_info_write',15,NULL),
	 (8,'id',1,NULL),
	 (8,'id_camera',2,NULL);
INSERT INTO public.interface_forms_tables_col_nastr (id_interface_forms_tables,col_name,ordinal_position_new,zapros_sql_combobox) VALUES
	 (8,'name',3,NULL),
	 (8,'opisanie',4,NULL),
	 (8,'usl_send_less',5,NULL),
	 (8,'usl_send_more',6,NULL),
	 (8,'usl_change_min',7,NULL),
	 (8,'usl_norm_less',8,NULL),
	 (8,'usl_norm_more',9,NULL),
	 (8,'active_st',10,NULL),
	 (8,'active_end',11,NULL),
	 (8,'id_class_yolo_coco',12,NULL);
INSERT INTO public.interface_forms_tables_col_nastr (id_interface_forms_tables,col_name,ordinal_position_new,zapros_sql_combobox) VALUES
	 (8,'b_act',13,NULL),
	 (8,'detect_object_box_color_r',14,NULL),
	 (8,'detect_object_box_color_g',15,NULL),
	 (8,'detect_object_box_color_b',16,NULL),
	 (8,'detect_object_contur_color_r',20,NULL),
	 (8,'detect_object_contur_color_g',21,NULL),
	 (8,'detect_object_contur_color_b',22,NULL),
	 (8,'detect_object_b_write_box',23,NULL),
	 (8,'detect_object_b_write_contur',24,NULL),
	 (8,'detect_object_b_detect_main_color',25,NULL);
INSERT INTO public.interface_forms_tables_col_nastr (id_interface_forms_tables,col_name,ordinal_position_new,zapros_sql_combobox) VALUES
	 (8,'confidence_min',26,NULL),
	 (8,'contur_zona_color_r',27,NULL),
	 (8,'contur_zona_color_g',28,NULL),
	 (8,'contur_zona_color_b',29,NULL),
	 (10,'id',1,NULL),
	 (10,'id_camera_zona',2,NULL),
	 (10,'i_num',3,NULL),
	 (10,'x',4,NULL),
	 (10,'y',5,NULL),
	 (12,'id',1,NULL);
INSERT INTO public.interface_forms_tables_col_nastr (id_interface_forms_tables,col_name,ordinal_position_new,zapros_sql_combobox) VALUES
	 (12,'name',2,NULL),
	 (12,'url',3,NULL),
	 (12,'opisanie',9,NULL),
	 (12,'b_video_potok',13,NULL),
	 (12,'b_act',14,NULL),
	 (12,'b_descript_info_write',15,NULL),
	 (13,'id',1,NULL),
	 (13,'id_camera',2,NULL),
	 (13,'name',3,NULL),
	 (13,'opisanie',4,NULL);
INSERT INTO public.interface_forms_tables_col_nastr (id_interface_forms_tables,col_name,ordinal_position_new,zapros_sql_combobox) VALUES
	 (13,'usl_send_less',5,NULL),
	 (13,'usl_send_more',6,NULL),
	 (13,'usl_change_min',7,NULL),
	 (13,'usl_norm_less',8,NULL),
	 (13,'usl_norm_more',9,NULL),
	 (13,'active_st',10,NULL),
	 (13,'active_end',11,NULL),
	 (13,'id_class_yolo_coco',12,NULL),
	 (13,'b_act',13,NULL),
	 (13,'detect_object_box_color_r',14,NULL);
INSERT INTO public.interface_forms_tables_col_nastr (id_interface_forms_tables,col_name,ordinal_position_new,zapros_sql_combobox) VALUES
	 (13,'detect_object_box_color_g',15,NULL),
	 (13,'detect_object_box_color_b',16,NULL),
	 (13,'detect_object_contur_color_r',20,NULL),
	 (13,'detect_object_contur_color_g',21,NULL),
	 (13,'detect_object_contur_color_b',22,NULL),
	 (13,'detect_object_b_write_box',23,NULL),
	 (13,'detect_object_b_write_contur',24,NULL),
	 (13,'detect_object_b_detect_main_color',25,NULL),
	 (13,'confidence_min',26,NULL),
	 (13,'contur_zona_color_r',27,NULL);
INSERT INTO public.interface_forms_tables_col_nastr (id_interface_forms_tables,col_name,ordinal_position_new,zapros_sql_combobox) VALUES
	 (13,'contur_zona_color_g',28,NULL),
	 (13,'contur_zona_color_b',29,NULL),
	 (14,'id',1,NULL),
	 (14,'id_camera_zona',2,NULL),
	 (14,'cnt_object',3,NULL),
	 (14,'date_time',4,NULL),
	 (14,'b_add_mess_usl_more',5,NULL),
	 (14,'b_add_mess_usl_more_norm',6,NULL),
	 (14,'b_add_mess_usl_less',7,NULL),
	 (14,'b_add_mess_usl_less_norm',8,NULL);
INSERT INTO public.interface_forms_tables_col_nastr (id_interface_forms_tables,col_name,ordinal_position_new,zapros_sql_combobox) VALUES
	 (14,'folder_name',9,NULL),
	 (14,'file_name',10,NULL);
INSERT INTO public.interface_forms_tables_command (id_interface_forms_tables,num,"name",command,menu_text,mess_col_id_null,mess_ok,mess_err,b_update_child_table) VALUES
	 (2,1,'Дополнить interface_forms_tables_col_nastr','insert into public.interface_forms_tables_col_nastr(id_interface_forms_tables, col_name, ordinal_position_new)
SELECT 
{col_id},
t2.column_name, 
t2.ordinal_position
FROM public.interface_forms_tables t1
join information_schema.columns t2 on t2.table_schema || ''.'' || t2.table_name = t1.table_name 
WHERE t1.id = {col_id} and 
	t2.column_name not in (select tc1.col_name
	from public.interface_forms_tables_col_nastr tc1
	left join public.interface_forms_tables tc2 on tc2.id = tc1.id_interface_forms_tables
	where tc2.id = {col_id} )
ORDER BY t2.ordinal_position;','Дополнить информацию по колонкам таблицы','Необходимо выбрать таблицу.','Команда выполнена: {sql}.','Ошибка запуска {sql}.',true),
	 (8,1,'Дополнить interface_forms_tables_col_nastr','insert into public.interface_forms_tables_col_nastr(id_interface_forms_tables, col_name, ordinal_position_new)
SELECT 
{col_id},
t2.column_name, 
t2.ordinal_position
FROM public.interface_forms_tables t1
join information_schema.columns t2 on t2.table_schema || ''.'' || t2.table_name = t1.table_name 
WHERE t1.id = {col_id} and 
	t2.column_name not in (select tc1.col_name
	from public.interface_forms_tables_col_nastr tc1
	left join public.interface_forms_tables tc2 on tc2.id = tc1.id_interface_forms_tables
	where tc2.id = {col_id} )
ORDER BY t2.ordinal_position;','Дополнить информацию по колонкам таблицы','Необходимо выбрать таблицу.','Команда выполнена: {sql}.','Ошибка запуска {sql}.',true),
	 (13,1,'Дополнить interface_forms_tables_col_nastr','insert into public.interface_forms_tables_col_nastr(id_interface_forms_tables, col_name, ordinal_position_new)
SELECT 
{col_id},
t2.column_name, 
t2.ordinal_position
FROM public.interface_forms_tables t1
join information_schema.columns t2 on t2.table_schema || ''.'' || t2.table_name = t1.table_name 
WHERE t1.id = {col_id} and 
	t2.column_name not in (select tc1.col_name
	from public.interface_forms_tables_col_nastr tc1
	left join public.interface_forms_tables tc2 on tc2.id = tc1.id_interface_forms_tables
	where tc2.id = {col_id} )
ORDER BY t2.ordinal_position;','Дополнить информацию по колонкам таблицы','Необходимо выбрать таблицу.','Команда выполнена: {sql}.','Ошибка запуска {sql}.',true);
INSERT INTO public.interface_forms_tables_sviaz (id_interface_forms_tables,num,table_name,table_col_sviaz) VALUES
	 (1,1,'public.interface_forms_tables','id_interface_forms'),
	 (2,1,'public.interface_forms_tables_sviaz','id_interface_forms_tables'),
	 (2,2,'public.interface_forms_tables_command','id_interface_forms_tables'),
	 (2,3,'public.interface_forms_tables_col_nastr','id_interface_forms_tables'),
	 (7,1,'public.camera_zona','id_camera'),
	 (8,1,'public.camera_zona_coord','id_camera_zona'),
	 (12,1,'public.camera_zona','id_camera'),
	 (13,1,'public.camera_zona_rezult','id_camera_zona');
