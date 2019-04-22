#!/usr/bin/env python2
# -*- coding: utf8 -*-
from fractal_pallete_manager import PalleteManager
from fractal_pallete import Pallete
from fractal_calc import prepare_coord_array, prepare_statistics_arr, calculate_fractal
from draw_xy_map import draw_xy_map, xy_map_from_image, load_image, save_image, platform_dependent_path, ensure_dir
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, Boolean, Float, String, MetaData, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker
from setup import images_folder, sqlite_db_engine
import copy
#import sys

debug = False

class Fractal(object):
    def __init__(self, params, function = "v=v**n+z", value_init = "v=x+1j*y", name = "", max_step_count = 20, int_limit = 0.01, ext_limit = 100.0):
        (self.function, self.value_init, self.params, self.name) = (function, value_init, params, name)
        self.name_id = function + " - " + params + " - " + value_init
        (self.max_step_count, self.int_limit, self.ext_limit) = (max_step_count, int_limit, ext_limit)
        (self.max_step_count, self.int_limit, self.ext_limit) = (max_step_count, int_limit, ext_limit)
        (self.calculated, self.step_count_statistics, self.variation) = (False, [], 0)
        (self.min_step, self.max_step, self.border_min_step, self.border_max_step) = (0, 0, 0, 0)
        (self.x_arr, self.x_from, self.x_to, self.x_count) = ([], -2, 2, 200)
        (self.x_arr, self.y_from, self.y_to, self.y_count) = ([], -2, 2, 200)
        (self.step_count_map, self.base_image, self.base_image_path, self.base_image_name, self.base_pallete) = ([], None, "", "", None)
        self.changed = False
        self.loaded_from_db = False

    @classmethod
    def from_db(self, instance):
        fr = Fractal("")
        for attr, value in instance.__dict__.iteritems():
            #if debug:
            #    print("instance has attr", attr, value)
            if hasattr(fr, attr):
                setattr(fr, attr, value)
            #    if debug:
            #        print("fractal has attr", attr, getattr(fr, attr))
        #if debug:
        #    print("fractal step_count_statistics_str", fr.step_count_statistics_str)
        #    print("fractal variation", fr.variation)
        fr.loaded_from_db = True
        if fr.step_count_statistics_str != None:
            fr.step_count_statistics = eval(fr.step_count_statistics_str)
            #if debug:
            #    print("filled fractal statistics", fr.step_count_statistics)
        return fr

    def __repr__(self):
    	return "Fractal (function = '%s', value_init = '%s', params = '%s', calculated = '%s', statistics = '%s', variation = '%s')" % (self.function, self.value_init, self.params, self.calculated, self.step_count_statistics_str, self.variation)

    def prepare_xy_arrays(self, x_from = 0, x_to = 0, x_count = 0, y_from = 0, y_to = 0, y_count = 0):
    	if x_count > 0:
    		(self.x_from, self.x_to, self.x_count) = (x_from, x_to, x_count)
    	if y_count > 0:
    		(self.y_from, self.y_to, self.y_count) = (y_from, y_to, y_count)
    	self.x_arr = prepare_coord_array(self.x_from, self.x_to, self.x_count)
    	self.y_arr = prepare_coord_array(self.y_from, self.y_to, self.y_count)

    def perform_calculation(self, force_save_image = True):
    	self.step_count_statistics = prepare_statistics_arr(self.max_step_count)
    	self.prepare_xy_arrays()
    	(self.step_count_map, self.step_count_statistics, self.variation, self.min_step, self.max_step, self.border_min_step, self.border_max_step) = calculate_fractal(self.x_arr, self.y_arr, self.value_init, self.function, self.params, self.max_step_count, self.int_limit, self.ext_limit)
    	if debug:
    	    print(self.step_count_statistics)
    	    print(self.variation)
    	self.step_count_statistics_str = str(self.step_count_statistics)
    	self.calculated = True
    	self.changed = True
    	if force_save_image:
    	    (self.base_image_path, self.base_image_name) = self.generate_image_path()
    	    img = self.draw_image()
    	    self.save_image(img)


    def draw_image(self, pallete = None):
    	isBasePallete = False
    	if pallete is None:
    		if self.base_pallete is None:
    			pallete_manager = PalleteManager(self.max_step_count)
    			self.base_pallete = pallete_manager.get_dafault_pallete()
    		pallete = self.base_pallete
    		isBasePallete = True
    	img = draw_xy_map(self.x_count, self.y_count, pallete.pallete, self.step_count_map)
    	if isBasePallete == True:
    		self.base_image = img
    	return img

    def load_base_image(self):
    	if self.base_image_path == "":
    		(self.base_image_path, self.base_image_name) = self.generate_image_path()
    	print (self.base_image_path)
    	if self.base_image_path != "":
    	   try:
    	       self.base_image = load_image(self.base_image_path, self.base_image_name)
    	   except:
    	       self.base_image = None

    def step_count_map_from_image(self):
    	if self.base_pallete is None:
    		pallete_manager = PalleteManager(self.max_step_count)
    		self.base_pallete = pallete_manager.get_dafault_pallete()
    	if self.base_image <> None:
    	    (self.x_count, self.y_count, self.step_count_map) = xy_map_from_image(self.base_pallete.pallete, self.base_image)
    	else:
    	    (self.x_count, self.y_count, self.step_count_map) = (0, 0, [])

    def generate_image_path(self, pallete = ""):
    	#root_image_folder = "/static/images/"
    	path = images_folder(debug) + self.function + "/" + self.params + "/"
    	#URL = "/" + root_image_folder + self.function + "/" + self.params + "/"
    	path = platform_dependent_path(path)
    	#URL = platform_dependent_path(URL)
    	ensure_dir(path)
    	if pallete != "":
    		name = pallete.name#.decode()
    		#print (pallete.name)
    	else:
    		name = "base"
    	print (name)
    	name = name + ".png"
    	#if not returnURL:
    	return (path, name)
    	#else:
    	#    return URL+name

    def save_image(self, img = "", pallete = "", path = "", name = ""):
    	if path == "" or name == "":
    		(_path, _name) = self.generate_image_path(pallete)
    	if path != "":
    		_path = path
    	if name != "":
    		_name = name
    	if img != "":
    		_img = img
    	else:
    		_img = self.base_image
    	print (_name)
    	save_image(_img, _path, _name)

#Определим привязки к таблице БД
metadata = MetaData()
fractal_table = Table('fractals', metadata,
	Column('id', Integer, primary_key=True, autoincrement=True),
	Column('function', String(100)),
	Column('value_init', String(100)),
	Column('params', String(100)),
	Column('name', String(100)),
	Column('name_id', String(200)),
	Column('max_step_count', Integer),
	Column('int_limit', Float),
	Column('ext_limit', Float),
	Column('step_count_statistics_str', String(300)),
	Column('calculated', Boolean),
	Column('variation', Float),
	Column('min_step', Integer),
	Column('max_step', Integer),
	Column('border_min_step', Integer),
	Column('border_max_step', Integer),
	Column('x_from', Float),
	Column('x_to', Float),
	Column('x_count', Integer),
	Column('y_from', Float),
	Column('y_to', Float),
	Column('y_count', Integer),
	Column('base_image_path', String(100))
	)
mapper(Fractal, fractal_table)


class FractalManager:
	def __init__(self):
		self.fractals = []
		self.pallete_manager = PalleteManager()
		self.engines = []
		self.ftp_folders = []
	def __repr__(self):
			return "FractalManager ('%s')" % self.fractals
	#def add_engine(self):

    #Добавление движка СУБД и создание в добавленной СУБД таблицы для хранения информации о палитрах (если не создана ранее)
	def add_engine(self, connection_string):
		engine = create_engine(connection_string, echo=False)
		self.engines.append(engine)
		metadata.create_all(engine)

    #Добавление фрактала с проверкой на уникальность
	def add_fractal(self, fractal, force_replace = False, from_db = False):
		already_in_list = False
		fr_found_in_list = ""
		for fr in self.fractals:
			if (fr.name_id == fractal.name_id):
				already_in_list = True
				fr_found_in_list = fr
				if debug:
				    print ("already in list", fr.name_id)
		if already_in_list != True:
			self.fractals.append(fractal)
			if debug:
			    if from_db == True:
			        print("loaded from db", fractal)
			    else:
			        print("added", fractal)
		elif force_replace != False:
			self.fractals.remove(fr_found_in_list)
			self.fractals.append(fractal)
			if debug:
			    print ("Fractal is replaced.", fr.name_id)


    #Загрузка фракталов из СУБД
	def load_fractals(self):
		#if debug:
		#    print ("## loading fractals from DB.")
		Session = sessionmaker()
		for engine in self.engines:
			Session.configure(bind=engine)
			session = Session()
			for instance in session.query(Fractal).order_by(Fractal.name_id):
				fr = Fractal.from_db(instance)
				#if debug:
				#    print ("  loaded instance ", instance)
				#    print ("  into fractal ", fr)
				self.add_fractal(fr)

    #Сохранение палитр в СУБД
	def save_fractals(self, force_replace = False):
		Session = sessionmaker()
		for engine in self.engines:
			Session.configure(bind=engine)
			for fr in self.fractals:
				session = Session()
				already_exists = False
				for instance in session.query(Fractal).filter_by(name_id=fr.name_id):
					already_exists = True
					if debug:
					    print("already exists in db '%s'", fr)
					if (force_replace == True) and (fr.changed == True):
					    session.delete(instance)
					    session.commit()
					    print("removing previous instance in db '%s'", instance)
				if (already_exists == False) or (force_replace == True and fr.changed == True):
					if debug:
					    print("Saving fractal '%s'", fr)
					session.add(fr)
					try:
						session.commit()
					except Exception as ex:
						print ("Error while saving fractal ", engine, ex.message)

    #Удаление палитры из списка и СУБД
	def delete_fractal(self, fractal):
		if not isinstance(fractal, Fractal):
		    fractal_name_id = fractal
		else:
		    fractal_name_id = fractal.name_id
		Session = sessionmaker()
		if debug:
		    print ("deleting " + fractal)
		for engine in self.engines:
			Session.configure(bind=engine)
			session = Session()
			obj=session.query(Pallete).filter_by(name_id=fractal_name_id).one()
			session.delete(obj)
			session.commit()
		for fr in self.fractals:
			if fr.name_id == fractal_name_id:
				self.fractals.remove(fr)

    #Удаление всех фракталов
	def remove_all_fractals(self):
		for engine in self.engines:
			tractals_table.drop(engine)

    #Получение фрактала по умолчанию
	def get_dafault_fractal(self):
		fr = Fractal("(n,z)=(1.51, 0.7+0.05j)")
		self.add_fractal(fr)
		return fr

#загружаем из БД список рассчитанных фракталов (параметры, статистика итогов расчета)
#по выбранным загружаем файлы с изображениями
#по отсутствующим изображениям инициируем перерасчет
#добавляем новый фрактал, сохраняем в списке фракталов без отметки о расчете
#инициируем расчет, сохраняем статистику параметры расчета, опционно сохраняем изображение в стандартной палитре
#по выбранному фракталу получаем изображение в интересующей палитре, интересующего разрешения (если есть файл, то из файла, если его нет, то без него).
if __name__ =="__main__":
    debug = True
    fractal_manager = FractalManager()
    path = sqlite_db_engine(debug)
    print(path)
    fractal_manager.add_engine(path)
    fractal_manager.load_fractals()
    for fr in fractal_manager.fractals:
        if fr.base_image_path != "":
            print("base_image_path", fr.base_image_path)
        fr.load_base_image()
        # Если есть базовое изображение то на его основе можем быстро преобразовать в произвольную палитру
        if fr.base_image != None:
            fr.step_count_map_from_image()
            pallete = Pallete(20, "0xffffff, 0xee6e1b, 0x000000", "test_plt1")
            img = fr.draw_image(pallete)
            fr.save_image(img, pallete)


	#def __init__(self, params, function = "v=v**n+z", value_init = "v=x+1j*y", name = "", max_step_count = 20, int_limit = 0.01, ext_limit = 100.0):

    print("#####  Calculating Mondelbrot set ######")
    print("#####  Modelbrot set. Variable value of constant parameter ""z"", fixed initial zero value of cyclic variable ""v""")
    fr = Fractal("n=2", "v=v**n+z", "(z,v)=(x+1j*y,0)")
    (fr.x_arr, fr.x_from, fr.x_to) = ([], -2.5, 1.5)
    (fr.x_count, fr.y_count) = (200,200)

    fr.perform_calculation()
    fractal_manager.add_fractal(fr, True)
    fractal_manager.save_fractals(True)
    #fr.load_base_image()
    #fr.step_count_map_from_image()
    base_img = fr.draw_image()
    fr.save_image(base_img)

    pallete = Pallete(20, "0x1e6b20, 0xee6e1b, 0x7997f4", "summer")
    img = fr.draw_image(pallete)
    fr.save_image(img, pallete)


    #print("#####  Calculating Julia set ######")
    #print("#####  Julia set. Fixed value of constant parameter ""z"" related to the point on Mondelbrot set, Variable initial zero value of cyclic variable ""v""")
    #fr = Fractal("(n,z)=(2, 0.7+0.05j)", "v=v**n+z", "v=x+1j*y") #
    ##fr = Fractal("(n,z)=(1.51, 0.7+0.05j)")
    #(fr.x_count, fr.y_count) = (800,800)
    #fr.perform_calculation()
    #fractal_manager.add_fractal(fr)
    #fractal_manager.save_fractals()
    ##fr.load_base_image()
    ##fr.step_count_map_from_image()
    #pallete = Pallete(20, "0x1e6b20, 0xee6e1b, 0x7997f4", "summer")
    #img = fr.draw_image(pallete)
    #fr.save_image(img, pallete)

