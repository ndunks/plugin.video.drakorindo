import re
from xml.etree import ElementTree
from .helper import strip_tags

match_episode = re.compile('episode\s+([0-9]+)', re.IGNORECASE)
match_links = re.compile(
    '([0-9]+\s?p)\s*:.*?(oload|drive|upload|mirrorcreator)', re.IGNORECASE)
match_urls = re.compile('<a.*?href="(.*?)".*?>(.*?)</', re.IGNORECASE)

class post(object):

    id          = None
    content     = None
    title       = None
    guid        = None
    link        = None
    category    = None
    description = None

    def __init__(self, values):
        for k in values.keys():
            if hasattr(self, k):
                self.__setattr__(k, values[k])

    def read_content(self):
        
        root = ElementTree.fromstring('<root>' + self.content + '</root>')
        content = []
        episodes = {}

        current_episode = None
        els = []
        # Separate  lines
        for el in root.iter():
            html = ElementTree.tostring(el, encoding='utf-8', method='html')

            for x in html.encode('utf-8').strip().split('<br'):

                for y in x.splitlines():
                    els.append(y)

        for html in els:

            match = match_episode.search(html)
            #print(html)
            if match:
                #print('||||||| episode', match.group(1))
                current_episode = match.group(1).encode('ascii')
            elif not current_episode:
                content.append(strip_tags(html).strip())
            else:

                match = match_links.search(html)
                if match:
                    #print(html)
                    quality = match.group(1).encode('ascii').lower()
                    match = match_urls.findall(html.encode('ascii'))
                    if match:
                        if not episodes.has_key(current_episode):
                            episodes[current_episode] = {}
                        if not episodes[current_episode].has_key(quality):
                            episodes[current_episode][quality] = {}
                        for m in match:
                            episodes[current_episode][quality][m[1].title()] = m[0]
                        #print('LINK', quality, match)

                #print(content[-1])

            #print("-" * 80)

        return (content, episodes)