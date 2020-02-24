# encoding=utf8
from __future__ import unicode_literals
from xml.etree import ElementTree
import re
import os
from drakorindo import log
from drakorindo.userdata import STORAGE_PATH
from drakorindo.model import post
from drakorindo.fscache import FSCache

try:
    import xbmc
except Exception as e:
    pass

try:
    import http.client as http
except Exception as e:
    import httplib as http

DRAKORINDO_CONNECTION = None

CACHE = FSCache(os.path.join(STORAGE_PATH,'cache'), hours=1)

RSS_XML_NS = {'content': 'http://purl.org/rss/1.0/modules/content/'}

def get_posts(url):
    '''
    :rtype : post[]
    '''
    try:
        return read_posts(get(url))
    except Exception as e:
        log('ERROR', e)
        return None


def read_posts(raw_str):
    '''
    :rtype : post[]
    '''
    feed = ElementTree.fromstring(raw_str)
    posts = {}
    for item in feed.findall('./channel/item'):
        new = {}
        for k in ['title', 'guid', 'link', 'category', 'description']:
            new[k] = ElementTree.tostring(item.find(k), 'utf-8',
                                          'text').strip()

        content = (item.find('content')
                   or item.find('content:encoded', RSS_XML_NS))

        new['content'] = ElementTree.tostring(content, 'utf-8', 'text').strip()
        new['id'] = re.findall('p=([0-9]+)', new['guid'])[0]
        posts[ new['id'] ] = post(new)

    return posts


@CACHE
def get(url, retry=False):
    global DRAKORINDO_CONNECTION

    if not DRAKORINDO_CONNECTION:
        try:
            log('CONNECTING drakorindo.co')
            DRAKORINDO_CONNECTION = http.HTTPConnection('drakorindo.co')
            log('\tConnected')
        except Exception as e:
            log('FAILED %s' % e.message)
            raise e

    try:
        log('GET %s' % url)
        DRAKORINDO_CONNECTION.request("GET", url)
        r = DRAKORINDO_CONNECTION.getresponse()
        log('\tOK: %d %s' % (r.status, r.reason))
        return r.read()

    except http.RemoteDisconnected as e:
        log('\tDISCONNECTED')
        DRAKORINDO_CONNECTION = None
        if retry:
            raise e
        else:
            log('\tRetrying..')
            return get(url, True)
