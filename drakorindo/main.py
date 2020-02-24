from __future__ import print_function
import sys
import collections
import subprocess
import drakorindo.userdata as userdata

try:
    import xbmc
except Exception as e:
    pass


reload(sys)
sys.setdefaultencoding('utf8')

DRAKORINDO_MODULE_VERSION = '0.0.1'
DEBUG_MODE = False
ON_KODI = 'plugin://' in sys.argv[0]

def check_missing():
    if not get_phantomjs_path():
        return 'PhantomJS not installed'
    else:
        return None

def get_phantomjs_path():
    PHANTOMJS = userdata.get('phantomjs', None)
    if not PHANTOMJS:
        proc = subprocess.Popen(
            ['which phantomjs'], shell=True, stdout=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        PHANTOMJS = stdout.decode().strip()
        if not PHANTOMJS:
            log('No phantomjs Found')
            PHANTOMJS = None
        else:
            userdata.save('phantomjs', PHANTOMJS)

    return PHANTOMJS


def log(*args):
    if not DEBUG_MODE:
        return
    if ON_KODI:
        log_str = None
        if isinstance(args, collections.Iterable):
            d = []
            for i in args:
                d.append(str(i))
            log_str = ' '.join(d)
        else:
            log_str = args
        xbmc.log('\033[92mDRAKOR:\033[0m %s' % log_str)
    else:
        print(*args)



def version():
    return DRAKORINDO_MODULE_VERSION


def set_debug(tf):
    global DEBUG_MODE
    DEBUG_MODE = tf
    log('Drakorindo Debug Mode ON')
    log('Drakor indo loaded:', sys.argv)
    log('Python ', sys.version_info)