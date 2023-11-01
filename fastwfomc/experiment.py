import argparse
import csv
import random
import time
from collections import defaultdict

from aima3.logic import to_cnf
from aima3.utils import expr, Expr

from wfomc_cc import WFOMCWithCC

MAX_N = 50

bijections = expr('(S1(x) | ~P(x, y)) & (S3(x) | ~P(y, x))')
times = []
ns = list(range(1, MAX_N + 1))
random.shuffle(ns)
for n in ns:
    start_time = time.time()
    counter = WFOMCWithCC(bijections, n, [('P', n)])
    counter.get_wfomc({'S1': (1, -1), 'S3': (1, -1), 'P': (1, 1)})
    entry = {'n': n, 'time': time.time() - start_time}
    times.append(entry)
with open('runtimes.csv', 'w') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=['n', 'time'])
    writer.writeheader()
    for row in times:
        writer.writerow(row)
