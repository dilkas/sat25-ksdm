#!/usr/bin/env python3

import csv
import glob
import json
import time
import urllib.request

sequences = []
for filename in glob.glob('data/sequences/a*.mln'):
    id = filename.split('/')[2].split('.')[0][1:].zfill(6)
    print()
    print(id)
    print()
    with urllib.request.urlopen('https://oeis.org/search?fmt=json&q=id:A{}'.format(id)) as url:
        txt = json.load(url)
        print(txt)
        sequence = txt['results'][0]['data']
        sequences.append({'id': id, 'sequence': sequence})
    time.sleep(1)

with open('sequences.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'sequence'], delimiter=';')
    writer.writeheader()
    writer.writerows(sequences)
