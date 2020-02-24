#!/usr/bin/env python
# encoding=utf8
from __future__ import unicode_literals
import io
import pprint
from module import *

print('Module Version:', drakorindo.version())

drakorindo.set_debug(True)
f = io.open('feed2.xml', 'r', encoding='utf-8')
raw_feed = f.read()
f.close()

pp = pprint.PrettyPrinter(indent=2)

for (id, item) in drakorindo.browser.read_posts(raw_feed).items():

    pp.pprint(item)
    (content, episodes) = item.read_content()
    print( item.title )
    # for (episode, qualities) in episodes.items():
    # 	print('Espisode %s:' % episode )
    # 	for (quality, links) in qualities.items():
    # 		print('\t%s: %s' % (quality, ', '.join(links.keys()) ))

    #print 360 openload
    for (episode, qualities) in episodes.items():

        if qualities.has_key('360p'):
            links = qualities.get('360p')
            openload_url = links.get('Openload', None) or links.get(
                'Oload', None)
            if openload_url:
                print('Episode %s 360p openload' % episode)
            else:
                print('No openload')
        else:
            print('No 360P', qualities)
    print('-' * 80)
