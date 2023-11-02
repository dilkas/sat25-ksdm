import argparse
import json
from collections import defaultdict

from aima3.logic import to_cnf
from aima3.utils import expr, Expr

from wfomc_cc import WFOMCWithCC


def main():
    parser = argparse.ArgumentParser(
        description='Compute the WFOMC of a two-variable sentence.')
    parser.add_argument('instance', metavar='I', type=str,
                        help='WFOMC instance (in a custom JSON format)')
    parser.add_argument('domainsize', metavar='N',
                        type=int, help='domain size')

    args = parser.parse_args()
    with open(args.instance) as f:
        instance = json.load(f)
    counter = WFOMCWithCC(instance['formula'],
                          args.domainsize, instance['cardinalities'])
    print(counter.get_wfomc(
        instance['weights'] if instance['weights'] else defaultdict(lambda: (1, 1))))


if __name__ == "__main__":
    main()
