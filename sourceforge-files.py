#!/usr/bin/python


import sys
import os
from os.path import join
import getopt


cmd = sys.argv[0]

def help():
    print('Usage:')
    print('%s -f HTML_FILE_PATH'%cmd)
    print('%s -p PROJECT_NAME -d RELATIVE_DIRECTORY'%cmd)

def getText(el):
    if el.text:
        return el.text.strip()
    else:
        return ''

try:
    (options, arguments) = getopt.gnu_getopt(
        sys.argv[1:],
        'hf:p:d:',
        [],
    )
except getopt.GetoptError:
    help()
    sys.exit(1)


inFilePath = None
projectName = None
relDir = ''


for (opt, opt_arg) in options:
    if opt in ('-h',):
        help()
        sys.exit(0)
    elif opt in ('-f',):
        inFilePath = opt_arg
    elif opt in ('-p',):
        projectName = opt_arg
    elif opt in ('-d',):
        relDir = opt_arg


if inFilePath:
    if projectName:
        print('Both file path and project name is given')
        help()
        sys.exit(1)
    html_text = open(inFilePath).read()
elif projectName:
    import urllib2
    url = 'http://sourceforge.net/projects/%s/files/%s'%(projectName, relDir)
    response = urllib2.urlopen(url)
    html_text = response.read()
else:
    help()
    sys.exit(1)


import lxml.html

html = lxml.html.fromstring(html_text)
table = html.find('.//table[@id=\'files_list\']')
#print(dir(table))




data = []

for tr in table.findall('.//tbody/tr'):## [@headers=\'files_downloads_h]\']
    #print(item.tag, text, item.label, item.base, item.tail)
    a = tr.find('.//th/a')
    if a is None:
        continue
    row = {
        'filename': getText(a),
    }
    attrs = {
        'files_downloads_h': 'downloads',
        'files_date_h': 'date',
        'files_size_h': 'size',
    }
    for td in tr.findall('.//td'):
        header = td.get('headers')
        try:
            attr = attrs[header]
        except KeyError:
            continue
        if attr == 'date':
            value = getText(td.find('.//abbr'))
        else:
            value = getText(td)
        if attr == 'downloads':
            el = td.find('.//a/img')
            if el is not None:
                row['weekly_downloads'] = el.get('title').replace(' weekly downloads', '')
        row[attr] = value
    data.append(row)

data.sort(
    key=lambda row: row['date'],
    reverse=True,
)

total_downloads = 0

print('\t'.join([
    '#Weekly',
    '   Date   ',
    '   File   ',
]))

for row in data:
    if not row['filename']:
        continue
    parts = []
    downloads = None
    w_downloads = None
    try:
        downloads = int(row['downloads'])
    except (KeyError, ValueError):
        pass
    try:
        w_downloads = int(row['weekly_downloads'])
    except KeyError:
        pass
    
    if downloads is None:
        downloads = w_downloads
    else:
        if w_downloads is not None:
            assert downloads == w_downloads ## FIXME

    if downloads is None:
        downloads_str = '  -'
    else:
        downloads_str = '%3s'%downloads
        total_downloads += downloads
    parts += [
        downloads_str,
        row['date'],
        row['filename'],
    ]
    print('\t'.join(parts))

if total_downloads > 0:
    print('%3d\tTotal'%(
        total_downloads,
    ))

