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
incorrect_count = 0
total_count = 0
for filename in os.listdir(RESULTS_DIR):
    total_count += 1
    # print('Parsing', filename)
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

    sequence = [str(x) for x in sequences[int(data['sequence'][1:])][:len(counts) + 1]]
    if not (counts == sequence[:-1] or counts == sequence[1:]):
        incorrect_count += 1
        print('Sequence {} (algorithm {}) is incorrect:'.format(data['sequence'], data['algorithm']))
        print('Original:', [int(x) for x in sequence])
        print('Computed: ', [int(x) for x in counts if x != ''])
        print()

    for (domain, count, time) in zip(domains, counts, times):
        new_data = data.copy()
        new_data['domain.size'] = domain
        new_data['count'] = count
        new_data['inference.time'] = time
        rows.append(new_data)

print('Correct: {:.0f}% ({} out of {})'.format(100 * (total_count - incorrect_count) / total_count,
                                               total_count - incorrect_count, total_count))

with open(RESULTS_FILE, 'w', encoding='UTF8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(rows)
