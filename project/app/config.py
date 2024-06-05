import os

SECRET_KEY = b"afd41e94b269e053cc3f6d065a717cffde52ef5208928463ce897faed531006b"
# SECRET_KEY = os.environ.get('SECRET_KEY')

MYSQL_USER = "std_2405_lab4"
MYSQL_PASSWORD = "qwerzxcv"
MYSQL_HOST = "std-mysql.ist.mospolytech.ru"
MYSQL_DATABASE = "std_2405_lab4"
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images')

ADMIN_ROLE_ID = 2
