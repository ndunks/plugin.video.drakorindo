import os, re
from subprocess import Popen, PIPE
from .main import log, get_phantomjs_path


def get_openload(url):
    PHANTOM_SCRIPT = os.path.join( os.path.dirname(os.path.realpath(__file__)), 'linker.openload.js')
    PHANTOMJS = get_phantomjs_path()

    log('get_openload: ', PHANTOMJS)

    part = re.findall('^(https?:\/\/)?(\w{,3}\.)?(oload|openload)\.(co|io|link|stream)\/(f|embed)\/(.+?)\/', url)

    if not part:
        log('Invalid URL:', url)
        return False
    part = part.pop()
    #last element must be id
    oload_id = part[-1]

    VARS = os.environ.copy()
    if VARS.get('QT_QPA_PLATFORM') == None:
        VARS['QT_QPA_PLATFORM'] = 'offscreen'

    p = Popen(
        [
            PHANTOMJS, '--load-images=no', '--ssl-protocol=any',
            '--disk-cache=true', '--max-disk-cache-size=1024',
            '--web-security=false', PHANTOM_SCRIPT
        ],
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        shell=False,
        env=VARS,
    )
    out, err = p.communicate(oload_id.encode())
    result = out.decode()
    log('RESULT', result)

    if p.returncode != 0:
        log("PHANTOMJS RETURNED ERROR:", p.returncode);
        return False
    else:
        data = {};
        for line in result.splitlines():
            log("LN: ", line)
            part = line.partition(': ')
            if len(part[2]):
                data[part[0].lower().encode('ascii')] = part[2].encode('ascii')

    if data.has_key('video'):
        data['url'] = 'https://oload.stream/stream/%s?mime=true' % data['video']

    return data
