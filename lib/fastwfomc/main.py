import argparse
from collections import defaultdict

from aima3.logic import to_cnf
from aima3.utils import expr, Expr

from wfomc import WFOMC


def main():
    parser = argparse.ArgumentParser(description='Compute the WFOMC of a two-variable sentence.')
    parser.add_argument('domainsize', metavar='N', type=int,
                        help='domain size')
    args = parser.parse_args()
    n = args.domainsize

    four_coloured = expr(
        '~E(x, x) & ' +
        '(~E(x, y) | E(y, x)) & ' +
        '(C1(x) | C2(x) | C3(x) | C4(x)) & ' +
        '(~C1(x) | ~C2(x)) & ' +
        '(~C2(x) | ~C3(x)) & ' +
        '(~C1(x) | ~C3(x)) & ' +
        '(~C1(x) | ~C4(x)) & ' +
        '(~C2(x) | ~C4(x)) & ' +
        '(~C3(x) | ~C4(x)) & ' +
        '(~E(x,y) | (~(C1(x) & C1(y)) & ~(C2(x) & C2(y)) & ~(C3(x) & C3(y)) & ~(C4(x) & C4(y))))'
    )

    counter = WFOMC(four_coloured, n)
    print(counter.get_wfomc(defaultdict(lambda: (1, 1))))


if __name__ == "__main__":
    main()
