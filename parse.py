#!/usr/bin/env python3

import csv
import os

RESULTS_DIR = 'results'
RESULTS_FILE = 'results.csv'
FIELDNAMES = ['algorithm', 'sequence', 'domain.size', 'count', 'compilation.time', 'inference.time']
TIMEOUT = 3600000

sequences = {}
with open('sequences.csv', newline='') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        sequences[int(row['id'])] = [int(x) for x in row['sequence'].split(',')]

rows = []
for filename in os.listdir(RESULTS_DIR):
    print('Parsing', filename)
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
                if tokens[8] == 'TIMEOUT':
                    counts.append('')
                    times.append(TIMEOUT)
                else:
                    counts.append(tokens[8].translate({ord(','): None}))
                    times.append(tokens[10])
    assert len(domains) == len(counts)
    assert len(domains) == len(times)

    correct = True
    for (domain, count, time) in zip(domains, counts, times):
        sequence = sequences[int(data['sequence'][1:])]
        if count == '' or correct and int(count) != sequence[int(domain)]:
            correct = False
            print('Sequence {} (algorithm {}) is incorrect:'.format(data['sequence'], data['algorithm']))
            print('Original:', sequence)
            print('Computed: ', [int(x) for x in counts if x != ''])
            print()
        new_data = data.copy()
        new_data['domain.size'] = domain
        new_data['count'] = count
        new_data['inference.time'] = time
        rows.append(new_data)
    if correct:
        print('Sequence {} (algorithm {}) is CORRECT'.format(data['sequence'], data['algorithm']))

with open(RESULTS_FILE, 'w', encoding='UTF8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(rows)
