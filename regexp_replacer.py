#!/usr/bin/env python
import txt_mixin

from optparse import OptionParser

usage = 'usage: %prog [options] regexp replacement inputfile'
parser = OptionParser(usage)


## parser.add_option("-r", "--runlatex", dest="runlatex", \
##                   help="Run LaTeX after presentation is converted to tex.", \
##                   default=1, type="int")

## parser.add_option("-s", "--sectiond", dest="sections", \
##                   help="Indices of the sections of the document that you want converted to LaTeX.", \
##                   default='', type="string")

## parser.add_option("-o", "--output", dest="output", \
##                   help="Desired output path or filename.", \
##                   default='', type="string")

                  
(options, args) = parser.parse_args()

print('options='+str(options))
print('args='+str(args))

pat = args[0]
replacement = args[1]
pathin = args[2]

myfile = txt_mixin.txt_file_with_list(pathin)
myfile.replaceallre(pat, replacement)
myfile.save(pathin)
