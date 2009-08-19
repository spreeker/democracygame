
from settings import *

DEBUG = True


REALM = 'd.preeker.net'

DEMOCRACY_API_SERVER = "http://d.preeker.net/"

# loggin setup:
# (see: http://simonwillison.net/2008/May/22/debugging/ )
# and python docs

LOG_FILE_NAME = os.path.join(PROJECT_PATH, "thirdparty_log.txt")

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s %(levelname)s %(message)s',
    filename = LOG_FILE_NAME,
)


CACHE_BACKEND = 'dummy:///'
