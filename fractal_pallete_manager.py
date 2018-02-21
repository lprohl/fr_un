#!/usr/bin/env python2
# -*- coding: utf8 -*-
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey
from fractal_pallete import Pallete
from setup import images_folder, sqlite_db_engine
from sqlalchemy.orm import mapper, sessionmaker

use_relative_path = False

metadata = MetaData()
#Зададим описание таблицы для хранения палитр.
palletes_table = Table('palletes', metadata,
	Column('id', Integer, primary_key=True, autoincrement=True),
	Column('name', String(20)),
	Column('pallete_str', String(100))
	)
#Свяжем описание таблицы с существующим классом цветовой палитры
mapper(Pallete, palletes_table)

#Класс предназначен для управления списками палитр, позволяющий их добавление и удаление, сохранение в БД, восстановление из БД
class PalleteManager:
	def __init__(self, step_count = 20):
		self.step_count = step_count
		self.engines = [] #СУБД, в которых предполагается хранить копии наборов палитр
		self.palletes = []

	def __repr__(self):
		return "PalleteManager\n- step_count: '%s'\n- engines: '%s'\n- palletes'%s')" % (self.step_count, self.engines, self.palletes)

    #Добавление движка СУБД и создание в добавленной СУБД таблицы для хранения информации о палитрах (если не создана ранее)
	def add_engine(self, connection_string):
		engine = create_engine(connection_string, echo=False)
		self.engines.append(engine)
		metadata.create_all(engine)

    #Добавление палитры с проверкой на уникальность
	def add_pallete(self, pallete):
		already_in_list = False
		for plt in self.palletes:
			if plt.name == pallete.name:
				already_in_list = True
				print ("Pallete with non unique name skipped ", plt.name)
		if already_in_list != True:
			self.palletes.append(pallete)
			print("added", pallete)

    #Загрузка палитр из СУБД
	def load_palletes(self):
		Session = sessionmaker()
		for engine in self.engines:
			Session.configure(bind=engine)
			session = Session()
			for instance in session.query(Pallete).order_by(Pallete.name):
				plt = Pallete(self.step_count, str(instance.pallete_str), str(instance.name))
				self.add_pallete(plt)
				#print(self.step_count, str(instance.pallete_str), str(instance.name))

    #Сохранение палитр в СУБД
	def save_palletes(self):
		Session = sessionmaker()
		for engine in self.engines:
			Session.configure(bind=engine)
			for plt in self.palletes:
				session = Session()
				already_exists = False
				for instance in session.query(Pallete).filter_by(name=plt.name):
					already_exists = True
				if already_exists == False:
					session.add(plt)
					try:
						session.commit()
					except:
						print ("Error while saving pallete ", engine)

    #Удаление палитры из списка и СУБД
	def delete_pallete(self, pallete):
		Session = sessionmaker()
		for engine in self.engines:
			Session.configure(bind=engine)
			session = Session()
			obj=session.query(Pallete).filter_by(name=pallete.name).one()
			session.delete(obj)
			session.commit()
		for plt in self.palletes:
			if plt.name == pallete.name:
				self.palletes.remove(plt)

    #Удаление всех палитр
	def remove_all_palletes(self):
		for engine in self.engines:
			palletes_table.drop(engine)

    #Получение палитры по умолчанию
	def get_dafault_pallete(self):
		plt = Pallete(self.step_count, "0xffffff, 0x000000", "winter")
		self.add_pallete(plt)
		return plt


if __name__ == "__main__":
	use_relative_path = True
	pallete_manager = PalleteManager(20)
	pallete_manager.add_engine(sqlite_db_engine(use_relative_path))
	#pallete_manager.add_engine('sqlite:///pallete.db')

	#pallete_manager.remove_all_palletes()
	#pallete_manager.add_engine('mysql://user:pass@host/db')
	#pallete_manager.add_engine('mysql://user29177_frun:porohshock111@31.41.43.1:3306/user29177_FractalUniverse')#?port=3306
	pallete_manager.load_palletes()
	print(len(pallete_manager.palletes))
	plt = Pallete(20, "0x000000, 0xffffff", "night2")
	pallete_manager.add_pallete(plt)
	#plt = Pallete(20, "0xff0000, 0x0000ff", "red-blue")
	pallete_manager.add_pallete(plt)
	#pallete_manager.save_palletes()
	##pallete_manager.delete_pallete(plt)


