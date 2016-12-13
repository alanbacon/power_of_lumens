import re

## read photopic curve data

filename = 'photopic_curve.dat'

with open(filename, 'rt') as fID:
    raw_text = fID.read()
    
# split by either newline or three spaces

split_text = re.split('(?: ){3}\n?', raw_text)

table = []
current_nm = None
offset = -1
for s in split_text:
    nm_mo = re.search('(\d+) *nm', s)
    val_mo = re.search('(\d+\.\d+)', s)
    if nm_mo:
        current_nm = int(nm_mo.group(1))
        offset = -1
    elif val_mo:
        offset += 1
        nm = current_nm + offset
        table.append([nm, val_mo.group(1)])

for e in table:
    print(str(e[0]) + ' ' + str(e[1]))

save_filename = 'photopic_curve.csv'

with open(save_filename, 'wt') as fID:
    for e in table:
        fID.write( str(e[0]) + ', ' + str(e[1]) + '\n')