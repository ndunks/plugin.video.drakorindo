
import os
import sys
import pickle

try:
    import xbmc
except Exception as e:
    pass

STORAGE_PATH = '/tmp/drakorindo'
if 'plugin://' in sys.argv[0]:
    STORAGE_PATH = xbmc.translatePath('special://temp/drakorindo')

DATA = {}
DATA_PATH = os.path.join(STORAGE_PATH, 'data.pickle')

if os.path.exists(DATA_PATH):
    with open(DATA_PATH, 'r') as f:
        DATA = pickle.load(f)
        f.close()


def get(*args):
    return DATA.get(*args)


def save(key, val):
    DATA[key] = val
    save_data()


def save_data():
    with open(DATA_PATH, 'wp') as f:
        pickle.dump(DATA, f)
        f.close()


def get_search_history():
    return DATA.get('search_history', [])


def add_search_history(txt):
    if not DATA.has_key('search_history'):
        DATA['search_history'] = []
    elif txt in DATA['search_history']:
        return

    DATA['search_history'].append(txt)
    if len(DATA['search_history']) > 5:
        DATA['search_history'].pop(0)

    save_data()


def clear_search_history():
    DATA['search_history'] = []
    save_data()


def get_recent():
    return DATA.get('recent', [])


def add_recent(recent):
    if not DATA.has_key('recent'):
        DATA['recent'] = []
    elif recent in DATA['recent']:
        return

    if len(DATA['recent']) > 5:
        DATA['recent'].pop(0)

    DATA['recent'].append(recent)
    save_data()


def clear_recent():
    DATA['recent'] = []
    save_data()


def clear():
    DATA = {}
    os.remove(DATA_PATH)
