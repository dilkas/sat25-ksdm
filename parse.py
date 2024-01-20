#!/usr/bin/env python3

import csv
import os

RESULTS_DIR = 'results'
RESULTS_FILE = 'results.csv'
FIELDNAMES = ['algorithm', 'sequence', 'domain.size', 'count', 'compilation.time', 'inference.time']

sequences = {}
with open('sequences.csv', newline='') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        sequences[int(row['id'])] = [int(x) for x in row['sequence'].split(',')]

rows = []
for filename in os.listdir(RESULTS_DIR):
    data = {}
    data['sequence'], data['algorithm'] = filename.split('.')
    domains = []
    counts = []
    times = []
    with open(RESULTS_DIR + '/' + filename) as f:
        for line in f.readlines():
            if line.startswith('Compilation time:'):
                data['compilation.time'] = line.split()[2]
            elif line.startswith('The model count'):
                tokens = line.split()
                domains.append(tokens[7][:-1])
                counts.append(tokens[8].translate({ord(','): None}))
                times.append(tokens[10])
    assert len(domains) == len(counts)
    assert len(domains) == len(times)
    correct = True
    for (domain, count, time) in zip(domains, counts, times):
        sequence = sequences[int(data['sequence'][1:])]
        if correct and int(count) != sequence[int(domain)]:
            correct = False
            print('Sequence {} is incorrect:'.format(data['sequence']))
            print('Original:', sequence)
            print('Computed: ', [int(x) for x in counts])
            print()

        new_data = data.copy()
        new_data['domain.size'] = domain
        new_data['count'] = count
        new_data['inference.time'] = time
        rows.append(new_data)

with open(RESULTS_FILE, 'w', encoding='UTF8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(rows)
