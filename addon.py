#!/usr/bin/env python
import sys
import xbmcgui
import xbmcplugin
from drakorindo import log, browser, set_debug, linker, userdata, check_missing

try:
    from urllib.parse import parse_qsl
except Exception as e:
    #py2.7
    from urlparse import parse_qsl
    from urllib import urlencode, quote_plus

TITLE_PADDING = ' ' * 7

def die(msg):
    xbmcgui.Dialog().notification('Drakorindo', msg,
                                  xbmcgui.NOTIFICATION_ERROR)

def show_info(msg):
    xbmcgui.Dialog().notification('Drakorindo', msg, xbmcgui.NOTIFICATION_INFO)


def make_url(**kwargs):
    return KODI_URL + '?' + urlencode(kwargs)


def list_text(txt, isFolder=False, menu=[]):
    list_item = xbmcgui.ListItem(txt)
    if menu:
        log('menu', menu)
        list_item.addContextMenuItems(menu)

    url = make_url(page='nothing', text=txt)
    return (url, list_item, isFolder)


def list_feed(path_url, title):

    listing = []
    posts = browser.get_posts(path_url)

    if not posts:
        listing.append(list_text('Tidak ada ' + title))
    else:
        listing.append(list_text(title))

    for (ID, P) in posts.items():
        list_item = xbmcgui.ListItem(TITLE_PADDING + P.title)
        url = make_url(page='post', path=path_url, id=P.id)
        listing.append((url, list_item, True))

    return listing


def home(**args):

    listing = []

    # search history
    CARI_TEXT = "PENCARIAN.."
    search_history = userdata.get_search_history()
    if search_history:
        CARI_TEXT = TITLE_PADDING + "PENCARIAN BARU.."
        menu = [(
            'Hapus Pencarian Terakhir',
            'PlayMedia(%s)' % make_url(page='clear', data='search_history'),
        )]
        item = list_text('TERAKHIR DICARI', menu=menu)
        listing.append(item)

        for query in search_history:
            list_item = xbmcgui.ListItem(TITLE_PADDING + query)
            url = make_url(page='cari', query=query)
            listing.append((url, list_item, True))

    # Add cari
    list_item = xbmcgui.ListItem(CARI_TEXT)
    url = make_url(page='cari')
    listing.append((url, list_item, True))

    # Recent played
    recents = userdata.get_recent()
    if recents:
        menu = [(
            'Hapus Terakhir Dilihat',
            'PlayMedia(%s)' % make_url(page='clear', data='recent'),
        )]
        listing.append(list_text('TERAKHIR DILIHAT', menu=menu))

        for (title, path, id) in recents:
            url = make_url(page='post', path=path, id=id)
            list_item = xbmcgui.ListItem(TITLE_PADDING + title)
            listing.append((url, list_item, True))

    listing += list_feed('/category/drama-korea/feed/', 'DRAMA ONGOING')
    listing += list_feed('/feed/', 'LATEST UPDATE')

    xbmcplugin.addDirectoryItems(KODI_HANDLE, listing, len(listing))
    xbmcplugin.addSortMethod(KODI_HANDLE, xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.endOfDirectory(KODI_HANDLE)


def post(path, id):
    log('load post', path, 'id', id)
    posts = browser.get_posts(path)
    if not posts.has_key(id):
        die('Post not found')

    post = posts.get(id)
    (content, episodes) = post.read_content()

    if not len(episodes):
        show_info('Belum ada episode')
        return
    listing = []

    movies_found = 0

    for (episode, qualities) in episodes.items():

        for (quality, links) in qualities.items():
            openload_url = links.get('Openload', None) or links.get(
                'Oload', None)
            if openload_url:
                url = '%s?page=play&path=%s&id=%s&url=%s&server=%s&quality=%s' % (
                    KODI_URL, path, id, openload_url, 'Openload', quality)
                list_item = xbmcgui.ListItem('EPISODE %s - %s' % (episode,
                                                                  quality))
                list_item.setProperty('IsPlayable', 'true')
                listing.append((url, list_item, False))
                movies_found += 1

    xbmcplugin.addDirectoryItems(KODI_HANDLE, listing, len(listing))
    xbmcplugin.addSortMethod(KODI_HANDLE,
                             xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)

    xbmcplugin.endOfDirectory(KODI_HANDLE)
    if movies_found:
        userdata.add_recent((post.title, path, id))


def play(path, id, url, server, quality):
    log('Playing %s' % url)
    info = linker.get_openload(url)
    if not info:
        die('Cannot play video')
    log(info)
    video_url = info.get('url', None)
    if not video_url:
        log('Linker FAIL get video url', info)
        die('Cannot get video url')

    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=video_url)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(KODI_HANDLE, True, listitem=play_item)


def cari(query=None):
    if not query:
        query = xbmcgui.Dialog().input('Masukan Pencarian').strip()
        log('User input', query)

    if not len(query):
        log('No query, fallback')
        return
    url = '/search/%s/feed/' % quote_plus(query)

    listing = list_feed(url, 'HASIL PENCARIAN: %s ' % query)

    xbmcplugin.addDirectoryItems(KODI_HANDLE, listing, len(listing))
    xbmcplugin.addSortMethod(KODI_HANDLE, xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.endOfDirectory(KODI_HANDLE)
    userdata.add_search_history(query)

def clear(data=None):
    import xbmc
    if data == 'recent':
        userdata.clear_recent()
    elif data == 'search_history':
        userdata.clear_search_history()
    show_info('Ok, sudah dibersihkan')
    #xbmc.executebuiltin('PlayMedia(%s)' % make_url(page='home',reload='yes'))
    xbmc.executebuiltin('Container.Refresh()')
    # Crashed!
    # xbmcplugin.setResolvedUrl(KODI_HANDLE, True, None)


if __name__ == '__main__':

    #set_debug(True)
    if not userdata.get('not_first_run', False):
        missing = check_missing()
        if not missing == None:
            die(missing)
        else:
            userdata.save('not_first_run', 1)

    # Get the plugin url in plugin:// notation.
    KODI_URL = sys.argv[0]
    # Get the plugin handle as an integer number.
    KODI_HANDLE = int(sys.argv[1])
    log('HANDLE', KODI_HANDLE, 'args', sys.argv)

    REQUEST = dict(parse_qsl(sys.argv[2][1:]))
    log('REQ', REQUEST)
    PAGE = REQUEST.get('page', 'home')

    if PAGE == 'nothing':
        exit()

    # Filtering page, prevent malicous call
    if not PAGE in ('home', 'post', 'play', 'cari', 'clear'):
        xbmcgui.Dialog().notification('Drakorindo',
                                      'Page not found: %s' % PAGE,
                                      xbmcgui.NOTIFICATION_ERROR)
        exit(1)
    else:
        log('Load Page %s' % PAGE)
        #remove page attr to clean pass other attr
        REQUEST.pop('page',None)
        locals()[PAGE](**REQUEST)
