def images_folder(relative = False):
    if relative:
        return '../static/images/'
    else:
        return '/static/images/'

def sqlite_db_engine(relative = False):
    if relative:
        return 'sqlite:///../db/fr_un.db'
    else:
        return 'sqlite:////db/fr_un.db'
