#!/usr/bin/env python

from module import *


print('Module Version:', drakorindo.version())
print('Phantom Bin:', drakorindo.linker.PHANTOMJS)

drakorindo.set_debug(True);

result = drakorindo.linker.get_openload('https://oload.stream/f/ooRKzGulbms/f/ccc/%5Bdrakorindo.co%5D_Return.E01.ID.360p.mp4')

print(result)