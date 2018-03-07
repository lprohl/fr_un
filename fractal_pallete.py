#!/usr/bin/env python2
# -*- coding: utf8 -*-
import math
from setup import palletes_folder, step_count
from draw_xy_map import draw_xy_map, save_image, load_image

debug = False

class Pallete(object):
    def __init__(self, step_count = 30, pallete_str = "0xffffff, 0x000000", name = "winter"):
        self.name = name
        self.pallete_str = pallete_str
        self.step_count = step_count
        self.fill_pallete()
        #self.img_path = self.path_name()
        if not self.image_exists():
            self.create_image(200, 30)

    def __repr__(self):
        return "Pallete('%s', '%s', '%s', '%s', '%s')" % (self.name, self.pallete_str, self.step_count, self.pallete, self.path_name())

    def fill_pallete(self, pallete_str = "", name = "", step_count = 0):
        if pallete_str == "":
        	pallete_str = self.pallete_str
        else:
        	self.pallete_str = pallete_str
        if name == "":
        	name = self.name
        else:
        	self.name = name
        if step_count == 0:
        	step_count = self.step_count
        else:
        	self.step_count = step_count

        self.pallete_arr = self.pallete_str.split(",")
        count = 0
        self.pallete = []
        while count <= step_count:
        	color_pos = 1.0 * count / step_count * (len(self.pallete_arr) - 1)
        	color_pos_int = int(math.floor(color_pos))

        	exec ("self.hexcolor_prev = " + self.pallete_arr[color_pos_int])
        	if color_pos_int < len(self.pallete_arr) - 1:
        		exec ("self.hexcolor_next = " + self.pallete_arr[color_pos_int + 1])
        	else:
        		exec ("self.hexcolor_next = " + self.pallete_arr[color_pos_int])
        	shift = math.fmod(color_pos, 1)

        	r_prev = float(( self.hexcolor_prev >> 16 ) & 0xFF)
        	r_next = float(( self.hexcolor_next >> 16 ) & 0xFF)
        	g_prev = float(( self.hexcolor_prev >> 8  ) & 0xFF)
        	g_next = float(( self.hexcolor_next >> 8  ) & 0xFF)
        	b_prev = float(( self.hexcolor_prev       ) & 0xFF)
        	b_next = float(( self.hexcolor_next       ) & 0xFF)

        	r = int(r_prev + (r_next - r_prev) * shift)
        	g = int(g_prev + (g_next - g_prev) * shift)
        	b = int(b_prev + (b_next - b_prev) * shift)

        	color = (r, g, b)
        	self.pallete.append(color)

        	count = count + 1

    def image_exists(self):
        return False

    def path_name(self):
        return "/"+palletes_folder(debug) + self.name + ".png"

    def create_image(self, width, height):
        xy_map = []
        for x in range(1, width + 1):
            xy_map.append([])
            for y in range(1, height + 1):
                xy_map[x-1].append(x * self.step_count / width + 1)
        path = palletes_folder(debug)
        name = self.name + ".png"
        if debug:
            print (xy_map)
            print (path + name)
        img = draw_xy_map(width, height, self.pallete, xy_map)
        save_image(img, path, name)

if __name__ == "__main__":
    debug = True
    p = Pallete(step_count(debug), "0x000000, 0xffffff", "night")
    print(p)
    print(len(p.pallete))
