import sys

support_list = ('Android-2.8.29', 'Android-2.8.30', 'Android-2.8.31', 'Android-2.8.32')


def prolog_filename(line):
    items = line.split(';;;')
    platver = items[4] + '-' + items[3]
    return platver not in support_list


readfile = sys.argv[1]
writefile = sys.argv[2]G
not_support = False
with open(readfile, 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open(writefile, 'w', encoding='utf-8') as fw:
    for line in lines:
        if line.startswith('fileName'):
            not_support = prolog_filename(line)
            if not not_support:
                fw.write(line)
        elif not_support:
            continue
        else:
            fw.write(line)


