import re

fname='/home/cyb/Documents/cyb_medlem_v2/medlemslister/medlemmer_v12.json'

m=re.search('.+medlemmer_(\S)(\d\d)\.json', fname)
print m.group(0)
print m.group(1)
print m.group(2)
