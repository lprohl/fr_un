#!/usr/bin/env python2
# -*- coding: utf8 -*-
from fractal_pallete_manager import PalleteManager
from fractal_pallete import Pallete
from fractal_calc import prepare_coord_array, prepare_statistics_arr, calculate_fractal
from fractal_draw import draw_fractal, fractal_arr_from_image, load_image, save_image, platform_dependent_path, ensure_dir
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, Float, String, MetaData, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker


class Fractal:
	def __init__(self, params, function = "v=v**n+z", value_init = "v=x+1j*y", name = "", max_step_count = 20, int_limit = 0.01, ext_limit = 100):
		(self.function, self.value_init, self.params, self.name) = (function, value_init, params, name)
		(self.max_step_count, self.int_limit, self.ext_limit) = (max_step_count, int_limit, ext_limit)
		(self.calculated, self.step_count_statistics) = (False, [])
		(self.min_step, self.max_step, self.border_min_step, self.border_max_step) = (0, 0, 0, 0)
		(self.x_arr, self.x_from, self.x_to, self.x_count) = ([], -2, 2, 200)
		(self.x_arr, self.y_from, self.y_to, self.y_count) = ([], -2, 2, 200)
		(self.step_count_map, self.base_image, self.base_image_path, self.base_image_name, self.base_pallete) = ([], None, "", "", None)

	def __repr__(self):
		return "Fractal (function = '%s', value_init = '%s', params = '%s', calculated = '%s', statistics = '%s')" % (self.function, self.value_init, self.params, self.calculated, self.step_count_statistics)

	def prepare_xy_arrays(self, x_from = 0, x_to = 0, x_count = 0, y_from = 0, y_to = 0, y_count = 0):
		if x_count > 0:
			(self.x_from, self.x_to, self.x_count) = (x_from, x_to, x_count)
		if y_count > 0:
			(self.y_from, self.y_to, self.y_count) = (y_from, y_to, y_count)
		self.x_arr = prepare_coord_array(self.x_from, self.x_to, self.x_count)
		self.y_arr = prepare_coord_array(self.y_from, self.y_to, self.y_count)

	def perform_calculation(self):
		self.step_count_statistics = prepare_statistics_arr(self.max_step_count)
		self.prepare_xy_arrays()
		(self.step_count_map, self.step_count_statistics, self.min_step, self.max_step, self.border_min_step, self.border_max_step) = calculate_fractal(self.x_arr, self.y_arr, self.value_init, self.function, self.params, self.max_step_count, self.int_limit, self.ext_limit)

	def draw_image(self, pallete = None):
		isBasePallete = False
		if pallete is None:
			if self.base_pallete is None:
				pallete_manager = PalleteManager(self.max_step_count)
				self.base_pallete = pallete_manager.get_dafault_pallete()
			pallete = self.base_pallete
			isBasePallete = True
		img = draw_fractal(self.x_count, self.y_count, pallete.pallete, self.step_count_map)
		if isBasePallete == True:
			self.base_image = img
		return img

	def load_base_image(self):
		if self.base_image_path == "":
			(self.base_image_path, self.base_image_name) = self.generate_image_path()
		print (self.base_image_path)
		if self.base_image_path != "":
			self.base_image = load_image(self.base_image_path, self.base_image_name)

	def step_count_map_from_image(self):
		if self.base_pallete is None:
			pallete_manager = PalleteManager(self.max_step_count)
			self.base_pallete = pallete_manager.get_dafault_pallete()
		(self.x_count, self.y_count, self.step_count_map) = fractal_arr_from_image(self.base_pallete.pallete, self.base_image)

	def generate_image_path(self, pallete = "", returnURL = False):
		root_image_folder = "static/images/"
		path = root_image_folder + self.function + "/" + self.params + "/"
		URL = root_image_folder + self.function + "/" + self.params + "/"
		path = platform_dependent_path(path)
		URL = platform_dependent_path(self.function + "/" + self.params + "/")
		ensure_dir(path)
		if pallete != "":
			name = pallete.name#.decode()
			#print (pallete.name)
		else:
			name = "base"
		print (name)
		name = name + ".png"
		if not returnURL:
		    return (path, name)
		else:
		    return URL+name

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
	Column('max_step_count', Integer),
	Column('int_limit', Float),
	Column('ext_limit', Float),
	Column('calculated', Integer),
	Column('step_count_statistics', String(100)),
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
#mapper(Fractal, fractal_table)


class FractalManager:
	def __init__(self):
		self.fractals = []
		self.pallete_manager = PalleteManager()
		self.engines = []
		self.ftp_folders = []
	def __repr__(self):
			return "FractalManager ('%s')" % self.fractals
	#def add_engine(self):

#загружаем из БД список рассчитанных фракталов (параметры, статистика итогов расчета)
#по выбранным загружаем файлы с изображениями
#по отсутствующим изображениям инициируем перерасчет
#добавляем новый фрактал, сохраняем в списке фракталов без отметки о расчете
#инициируем расчет, сохраняем статистику параметры расчета, опционно сохраняем изображение в стандартной палитре
#по выбранному фракталу получаем изображение в интересующей палитре, интересующего разрешения (если есть файл, то из файла, если его нет, то без него).
if __name__ =="__main__":
	fr = Fractal("(n,z)=(1.51, 0.7+0.05j)")
	(fr.x_count, fr.y_count) = (800,800)
	fr.perform_calculation()
	#fr.load_base_image()
	#fr.step_count_map_from_image()
	pallete = Pallete(20, "0x1e6b20, 0xee6e1b, 0x7997f4", "summer")
	img = fr.draw_image(pallete)
	fr.save_image(img, pallete)

