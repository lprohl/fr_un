#!/usr/bin/env python2
# -*- coding: utf8 -*-

# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request, redirect, url_for
from fractal_pallete_manager import PalleteManager
from fractal_pallete import Pallete
from fractal_manager import Fractal
from setup import images_folder, sqlite_db_engine, step_count

app = Flask(__name__)
app.config["DEBUG"] = True

comments = []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("test_template.html", comments=comments)

    comments.append(request.form["comment"])
    return redirect(url_for('index'))

#def hello_world():
#    #a = 9/0
#    return 'Hello from Flask_!'


@app.route('/bye')
def bye_world():
    return 'Bye!'

@app.route('/palletes', methods=["GET", "POST"])
def palletes():
    pm = PalleteManager()
    pm.add_engine(sqlite_db_engine(False))
    pm.load_palletes()
    if request.method == "GET":
        #print (len(pm.palletes))
        #print (pm.palletes)
        pallete = Pallete(step_count(), "0x1e6b20, 0xee6e1b, 0x7997f4", "summer")
        #palletes = []
        #pm.palletes.append(pallete)
        pm.add_pallete(pallete)
        pm.save_palletes()
        return render_template("test_template.html", comments=comments, branch="/palletes", palletes=pm.palletes, palletes_count = len(pm.palletes),  title='Palletes')
        #return 'Bye!'

    if not request.form.get("comment") is None:
        comments.append(request.form.get("comment"))

    if not request.form.get("new_pallete_colors") is None and not request.form.get("new_pallete_name") is None:
        new_pallete_colors = request.form["new_pallete_colors"]
        new_pallete_name   = request.form["new_pallete_name"]
        pallete = Pallete(step_count(), new_pallete_colors, new_pallete_name)
        pm.add_pallete(pallete)
        pm.save_palletes()

    return redirect(url_for('palletes'))



@app.route('/fractal')
def fractal():
	fr = Fractal("(n,z)=(1.51, 0.7+0.05j)")
	(fr.x_count, fr.y_count) = (800,800)
	fr.perform_calculation()
	#fr.load_base_image()
	#fr.step_count_map_from_image()
	pallete = Pallete(20, "0x1e6b20, 0xee6e1c, 0x7997f4", "summer")
	img = fr.draw_image(pallete)
	fr.save_image(img, pallete)
	(path, name) = fr.generate_image_path(pallete)
	fractal_img_path = path + name
	return render_template("test_template.html", fractal_img=fractal_img_path, pallete=pallete, fractal=fr,  title='Fractal')#, path=img_path)
	#return render_template("test_template.html", path="/static/images/V=VxxN+Z/(N,Z)=(1.51, 0.7+0.05J)/summer.png")
	#return render_template("test_template.html", path="/static/images/summer.png")


if __name__ == "__main__":
    palletes()
