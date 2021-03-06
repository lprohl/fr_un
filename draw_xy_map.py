#!/usr/bin/env python2
from PIL import Image, ImageDraw
from PIL import ImageFont
import sys
import os
import platform
from setup import images_folder

debug = False

def draw_xy_map(x_count, y_count, pallete, xy_map):
	color = pallete[0]
	img = Image.new('RGB', (x_count, y_count), color)
	imgDrawer = ImageDraw.Draw(img)
	x_index = 0
	while x_index < x_count:
		y_index = 0
		while y_index < y_count:
			try:
				step = xy_map[x_index][y_index]
				color = pallete[step - 1]
				imgDrawer.point((x_index, y_index), color)
				y_index = y_index + 1
			except:
				if debug:
				    print(x_index, y_index, sys.exc_info())
				raise
		x_index = x_index + 1
	return img

def xy_map_from_image(pallete, img):
	(x_count, y_count) = img.size
	xy_map = []
	x_index = 0
	while x_index < x_count:
		y_index = 0
		xy_map.append([])
		while y_index < y_count:
			color = img.getpixel((x_index, y_index))
			try:
				step = pallete.index(color)
			except ValueError:
				step = 0
			xy_map[x_index].append(step)
			y_index = y_index + 1
		x_index = x_index + 1
		#print x_index
	return (x_count, y_count, xy_map)

def ensure_dir(folder):
	if folder:
		d = os.path.dirname(folder)
		if not os.path.isdir(d): #exists(d):
			os.makedirs(d)

def platform_dependent_path(path):
    path = path.replace("x", "X").replace("y", "Y").replace("z", "Z").replace("v", "V").replace("n", "N").replace("j", "J").replace("*", "x")
    if debug:
	    print ("platform: " + platform.system())
    if platform.system() == "Windows":
        if debug:
            print ("path script:" + path)
            print ("Windows")
        path = path.replace("/", "\\")
        if debug:
            print ("path platform:" + path)
        return path
    else:
        return path

def save_image(img, folder, file_name):
	ensure_dir(folder)
	if debug:
	    print (folder + file_name)
	img.save(folder + file_name)

def load_image(folder, file_name):
	img = Image.open(folder + file_name)
	#img = Image.new('RGB', (1, 1), (0,0,0))
	#print(folder + file_name)
	#img.load(folder + file_name)
	return img

if __name__ == "__main__":
	debug = True
	path = images_folder(debug)

	xy_map = []
	for x in range(1, 11):
		xy_map.append([])
		for y in range(1, 11):
			xy_map[x-1].append(x+y)
	print(xy_map)
	pallete = [];
	for c in range(1, 21):
		color = (c*10, c*10, c*10)
		pallete.append(color)

	img = draw_xy_map(10, 10, pallete, xy_map)
	save_image(img, path, "fractal_draw_test.png")

	img1 = load_image(path, "fractal_draw_test.png")

	(x_count, y_count, xy_map1) = xy_map_from_image(pallete, img1)
	pallete1 = [];
	for c in range(1, 21):
		color = (255-c*10, c*10, 255-c*10)
		pallete1.append(color)

	img2 = draw_xy_map(x_count, y_count, pallete1, xy_map1)

	save_image(img2, "", "fractal_draw_test2.png")
	#print(xy_map1)
	#print(dir(pallete))

	#print(pallete.index((90,90,9)))
	#print(dir(img))
	#print(img.size)
	#print(img.getpixel((5,5)))

