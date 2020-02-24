#!/usr/bin/env python
import pprint
from module import *



print('Module Version:', drakorindo.version())

drakorindo.set_debug(True);

latest = drakorindo.browser.get_latest()
for post in latest:
    print(post.title, post.read_content())
drama = drakorindo.browser.get_rss('/category/drama-korea/feed/')
# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(latest)
