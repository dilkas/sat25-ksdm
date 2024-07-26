#!/usr/bin/env python3

from collections import defaultdict
import csv
import os

RESULTS_DIR = '../results/raw'
RESULTS_FILE = '../results/processed/results.csv'
FIELDNAMES = [
    'algorithm',
    'sequence',
    'domain.size',
    'count',
    'compilation.time',
    'inference.time']
TIMEOUT = 15 * 1000  # in ms

def chop_trailing_empty_strings(lst):
    # Iterate from the end to find the first non-empty string
    last_non_empty_index = len(lst)
    for i in range(len(lst) - 1, -1, -1):
        if lst[i] != '':
            last_non_empty_index = i + 1
            break
    # Slice the list to remove trailing empty strings
    return lst[:last_non_empty_index]

# sequences = {}
# with open('sequences.csv', newline='') as f:
#     reader = csv.DictReader(f, delimiter=';')
#     for row in reader:
#         sequences[int(row['id'])] = [int(x) for x in row['sequence'].split(',')]

rows = []
incorrect_count = 0
failed_count = defaultdict(lambda: 0)
for filename in os.listdir(RESULTS_DIR):
    print('Parsing', filename)
    data = {}
    data['sequence'], data['algorithm'] = filename.split('.')
    domains = []
    counts = []
    times = []
    total_times = []
    with open(RESULTS_DIR + '/' + filename) as f:
        for line in f.readlines():
            if line.startswith('Compilation time:'):  # Crane
                data['compilation.time'] = line.split()[2]
            elif line.startswith('The model count'):  # Crane
                tokens = line.split()
                domains.append(tokens[7][:-1])
                if tokens[8] == 'TIMEOUT':
                    counts.append('')
                    times.append(TIMEOUT)
                else:
                    counts.append(tokens[8].translate({ord(','): None}))
                    times.append(tokens[10])
            elif line.startswith('Domain size:'):  # ForcLift and FastWFOMC
                domains.append(line.split()[2])
            elif line.startswith('Z = '):  # ForcLift
                try:
                    counts.append(int(round(float(line.split()[4]))))
                except OverflowError:  # Record 'Infinity' as a timeout
                    counts.append('')
                except ValueError:
                    # Record 'NaN' as a compilation error
                    domains = []
                    total_times = []
                    break
            elif line.startswith('Inference took'):  # ForcLift
                times.append(line.split()[2])
            elif line.startswith('Elapsed:'):  # ForcLift and FastWFOMC
                t = float(line.split()[1]) * 1000
                total_times.append(t)
                if data['algorithm'] == 'fastwfomc':
                    times.append(t)
            elif line.startswith('WFOMC:'):  # FastWFOMC
                counts.append(line.split()[1][:-3])

    # Ignore the timeouts at the end
    counts = chop_trailing_empty_strings(counts)
    domains = domains[:len(counts)]
    times = times[:len(counts)]
    if len(total_times) != 0:
        total_times = total_times[:len(counts)]

    # If the algorithm fails to compile, output no domains
    if len(domains) == 1:
        domains = []
        total_times = []

    if len(domains) == 0:
        failed_count[data['algorithm']] += 1

    assert len(domains) == len(counts)
    assert len(domains) == len(times)
    assert len(total_times) == 0 or len(total_times) == len(domains)
    assert '' not in counts

    # Check correctness of Crane
    # if data['sequence'].isnumeric() and data['algorithm'] != 'forclift':
    #     sequence = [str(x) for x in sequences[int(
    #         data['sequence'][1:])][:len(counts) + 2]]
    #     mutual_len = min(len(counts), len(sequence))
    #     if not (counts[:mutual_len] == sequence[:mutual_len] or
    #             counts[:mutual_len] == sequence[1:mutual_len + 1] or
    #             counts[:mutual_len] == sequence[2:mutual_len + 2]):
    #         incorrect_count += 1
    #         print(
    #             'Sequence {} (algorithm {}) is incorrect:'.format(
    #                 data['sequence'],
    #                 data['algorithm']))
    #         print('Original:', [int(x) for x in sequence])
    #         print('Computed: ', [int(x) for x in counts if x != ''])
    #         print()

    for i in range(len(domains)):
        new_data = data.copy()
        new_data['domain.size'] = domains[i]
        new_data['count'] = counts[i]
        new_data['inference.time'] = times[i]
        if len(total_times) > 0:
            new_data['compilation.time'] = total_times[i] - float(times[i])
        rows.append(new_data)

# print('Correct (treating unsolved as correct): {:.0f}% ({} out of {})'.format(100 * (len(sequences) - incorrect_count) / len(sequences),
#                                                                               len(sequences) - incorrect_count, len(sequences)))
# for algorithm, count in failed_count.items():
#     print('{} solved: {:.0f}% ({} out of {})'.format(algorithm, 100 * (len(sequences) - count) / len(sequences),
# int(len(sequences) - count), len(sequences)))

with open(RESULTS_FILE, 'w', encoding='UTF8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(rows)
