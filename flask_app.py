
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request, redirect, url_for
from fractal_pallete_manager import PalleteManager
from fractal_pallete import Pallete
from fractal_manager import Fractal

app = Flask(__name__)
app.config["DEBUG"] = True

comments = []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("test_template.html", comments=comments)

    comments.append(request.form["contents"])
    return redirect(url_for('index'))

#def hello_world():
#    #a = 9/0
#    return 'Hello from Flask_!'

@app.route('/bye')
def bye_world():
    return 'Bye!'

@app.route('/palletes')
def palletes():
    pm = PalleteManager()
    pm.add_engine('sqlite:///pallete.db')
    pm.load_palletes()
    return render_template("test_template.html", palletes=pm.palletes, title='Palletes')
    #pallete = Pallete(20, "0x1e6b20, 0xee6e1b, 0x7997f4", "summer")
    #palletes = []
    #palletes.append(pallete)
    #return 'Bye!'


@app.route('/fractal')
def fractal():
	fr = Fractal("(n,z)=(1.51, 0.7+0.05j)")
	(fr.x_count, fr.y_count) = (800,800)
	fr.perform_calculation()
	#fr.load_base_image()
	#fr.step_count_map_from_image()
	pallete = Pallete(20, "0x1e6b20, 0xee6e1b, 0x7997f4", "summer")
	img = fr.draw_image(pallete)
	fr.save_image(img, pallete)
	img_path = fr.generate_image_path(pallete, True)
	return render_template("test_template.html", path=img_path)


