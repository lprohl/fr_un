#!/usr/bin/env python2
# -*- coding: utf8 -*-
### Общие библиотеки ###
from __future__ import print_function
import scipy
import scipy.stats
from scipy.stats import tstd
from make_safe_exec_str import remove_dangerous_symbols_exec

### Функция для подготовки списков координат ###
def prepare_coord_array(form_coord, to_coord, point_count):
	# Определяем величину шага
	if point_count == 1:
		step = 0
	else:
		step = (to_coord - form_coord + 0.0) / (point_count - 1)
	# Заполняем список
	arr = []
	count = 0
	while count < point_count:
		coord = form_coord + step * count
		count = count + 1
		arr.append(coord)
		#print(arr[len(arr)-1], end='')
	return arr

### Функция для подготовки списка статистики ###
def prepare_statistics_arr(max_step_count):
	 i = 0
	 st = []
	 while i <= max_step_count:
	 	st.append(0)
	 	i = i + 1
	 return st

### Функция для расчета фрактала ###
# На вход подаем:
# - два массива стартовых значений x и y;
# - cтроковое значение переменной v для инициирования начального значения;
# - функцию расчета в виде строки;
# - максимальное количество шагов.
def calculate_fractal(x_arr, y_arr, value_init, function, params, max_step_count, int_limit, ext_limit):
	#обезопашиваем запускаемые участки кода
	value_init = remove_dangerous_symbols_exec(value_init)
	params = remove_dangerous_symbols_exec(params)
	function = remove_dangerous_symbols_exec(function)

	# Осуществляем расчет для каждой точки x, y.
	step_count_map = [] # результат расчета помещаем в список
	# Собираем статистику по минимальному, максимальному количеству шагов, распределению количества шагов
	min_step = max_step_count
	max_step = 0
	border_min_step = max_step_count
	border_max_step = 0
	step_count_statistics = prepare_statistics_arr(max_step_count)
	# Инициируем переменные, используемые при расчете
	x_count = len(x_arr)
	y_count = len(y_arr)
	x_index = 0
	v = 0
	exec (params.strip())

	for x in x_arr:

		step_count_map.append([])
		y_index = 0
		for y in y_arr:
			# Инициируем начальное значение переменной v
			exec (value_init.strip())
			# Выполняем расчет максимального количества шагов для данной точки до выхода значения функции за пределы области
			step = 0
			while ((abs(v) > int_limit) and (abs(v) < ext_limit)):
				if step >= max_step_count:
					break;
				exec (function.strip())
				step = step + 1
			step_count_map[x_index].append(step)

			# Собираем статистику:
			# - максимального и минимального значения по изображению
			if step < min_step:
				min_step = step
			if step > max_step:
				max_step = step
			# - максимального и минимального значения на границе
			if x_index == 0 or y_index == 0 or x_index == x_count-1 or y_index == y_count - 1:
				if step < border_min_step:
					border_min_step = step
				if step > border_max_step:
					border_max_step = step
			# Распределения количества шагов по точкам фрактала
			step_count_statistics[step] = step_count_statistics[step] + 1

			y_index = y_index + 1

		percent = round(100.0 * (x_index + 1) / x_count, 2)
		print("\r Calc " + str(percent) + "%             ", end='')

		x_index = x_index + 1
	print("")
	return (step_count_map, step_count_statistics, min_step, max_step, border_min_step, border_max_step)

#### Код для самотестирования модуля
if __name__ == "__main__":
	#А### Зададим параметры расчета ###
	#А.1# Диапазон изменения значений координат - область расчета
	(x_from, x_to, x_count) = (-2, 2, 200)
	(y_from, y_to, y_count) = (-2, 2, 200)
	#А.2# Функция, инициация начального значения, постоянные параметры расчета
	(function, value_init, params) = ("v=v**n+z", "v=x+1j*y", "(n,z)=(1.7, 0.5+0.05j)")
	#А.3# Внутенняя, внешняя граница области, максимальное количество шагов расчета
	(int_limit, ext_limit, max_step_count) = (0.01, 100, 30)
	#Б### Подготовим служебные переменные - списки значений координат ###
	x_arr = prepare_coord_array(x_from, x_to, x_count)
	y_arr = prepare_coord_array(y_from, y_to, y_count)
	#В### Выполним расчет ###
	(step_count_map, step_count_statistics, min_step, max_step, border_min_step, border_max_step) = calculate_fractal(x_arr, y_arr, value_init, function, params, max_step_count, int_limit, ext_limit)
	#Г### Выведем на консоль статистику ###
	print(step_count_statistics)
	print(scipy.stats.tstd(step_count_statistics))
	print(scipy.stats.variation(step_count_statistics))
	#print(dir(prepare_coord_array))
	#print(prepare_coord_array.func_code)
	#print(dir([]))
	#print(dir(""))

