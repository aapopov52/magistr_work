-- public.interface_forms определение

-- Drop table

-- DROP TABLE public.interface_forms;

CREATE TABLE public.interface_forms (
	id serial4 NOT NULL,
	num_1 int4 NULL,
	num_2 int4 NULL,
	num_3 int4 NULL,
	"name" varchar(100) NULL,
	b_act bool NULL,
	CONSTRAINT table_interface_forms_pkey PRIMARY KEY (id)
);


-- public.interface_forms_tables определение

-- Drop table

-- DROP TABLE public.interface_forms_tables;

CREATE TABLE public.interface_forms_tables (
	id serial4 NOT NULL,
	id_interface_forms int4 NULL,
	num int4 NULL,
	table_name varchar(100) NULL,
	col_id_name varchar(100) NULL,
	order_uslovie varchar(200) NULL,
	row_limit int4 NULL,
	left_ int4 NULL,
	top_ int4 NULL,
	width_ int4 NULL,
	heigth_ int4 NULL,
	b_read_only bool NULL,
	CONSTRAINT table_interface_forms_tables_pkey PRIMARY KEY (id),
	CONSTRAINT table_interface_forms_tables__id__interface_forms FOREIGN KEY (id_interface_forms) REFERENCES public.interface_forms(id) ON DELETE CASCADE
);


-- public.interface_forms_tables_col_nastr определение

-- Drop table

-- DROP TABLE public.interface_forms_tables_col_nastr;

CREATE TABLE public.interface_forms_tables_col_nastr (
	id serial4 NOT NULL,
	id_interface_forms_tables int4 NULL,
	col_name varchar(100) NULL,
	ordinal_position_new int4 NULL,
	zapros_sql_combobox text NULL,
	CONSTRAINT table_interface_forms_tables_col_nastr_pkey PRIMARY KEY (id),
	CONSTRAINT table_interface_forms_tables_col_nastr__id__interface_forms_tab FOREIGN KEY (id_interface_forms_tables) REFERENCES public.interface_forms_tables(id) ON DELETE CASCADE
);


-- public.interface_forms_tables_command определение

-- Drop table

-- DROP TABLE public.interface_forms_tables_command;

CREATE TABLE public.interface_forms_tables_command (
	id serial4 NOT NULL,
	id_interface_forms_tables int4 NULL,
	num int4 NULL,
	"name" varchar(512) NULL,
	command text NULL,
	menu_text varchar(256) NULL,
	mess_col_id_null varchar(256) NULL,
	mess_ok varchar(256) NULL,
	mess_err varchar(256) NULL,
	b_update_child_table bool NULL,
	CONSTRAINT table_interface_forms_tables_command_pkey PRIMARY KEY (id),
	CONSTRAINT table_interface_forms_tables_command__id__interface_forms_table FOREIGN KEY (id_interface_forms_tables) REFERENCES public.interface_forms_tables(id) ON DELETE CASCADE
);


-- public.interface_forms_tables_sviaz определение

-- Drop table

-- DROP TABLE public.interface_forms_tables_sviaz;

CREATE TABLE public.interface_forms_tables_sviaz (
	id serial4 NOT NULL,
	id_interface_forms_tables int4 NULL,
	num int4 NULL,
	table_name varchar(100) NULL,
	table_col_sviaz varchar(100) NULL,
	CONSTRAINT table_interface_forms_tables_sviaz_pkey PRIMARY KEY (id),
	CONSTRAINT table_interface_forms_tables_sviaz__id__interface_forms_tables FOREIGN KEY (id_interface_forms_tables) REFERENCES public.interface_forms_tables(id) ON DELETE CASCADE
);



