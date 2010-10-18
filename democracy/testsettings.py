from settings_ch import *

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'dev.db'

DATABASES = {
    'default' : {
        'ENGINE' : 'django.db.backends.sqlite3',
        'NAME' : 'dev.db',
    }
}

LANGUAGE_CODE = 'en-us'

LOG_FILE_NAME = os.path.join(PROJECT_PATH, "democracy_log.txt")

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s %(levelname)s %(message)s',
    filename = LOG_FILE_NAME,
)
