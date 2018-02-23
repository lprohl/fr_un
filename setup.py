def images_folder(debug = False):
    if not debug:
        return 'static/images/'
    else:
        return '../static/images_debug/'

def palletes_folder(debug = False):
    if not debug:
        return 'static/images/palletes/'
    else:
        return '../static/images_debug/palletes/'


def sqlite_db_engine(debug = False):
    if not debug:
        return 'sqlite:///db/fr_un.db' #working /home/[user]/db
    else:
        return 'sqlite:///../db/fr_un_debug.db'

def step_count(debug = False):
    if not debug:
        return 20
    else:
        return 20
