import itertools

from flint import fmpz_poly
from aima3.logic import predicate_symbols
from gmpy2 import mpz

from wfomc import WFOMC


class WFOMCWithCC:
    def __init__(self, formula, domainsize, ccs=[]):
        self.formula = formula
        self.domainsize = domainsize
        self.ccs = ccs # We assume these are all binary predicates for now...

    def get_wfomc(self, weights):
        self.weights = weights
        self.constrained_predicates = list(map(lambda x: x[0], self.ccs))
        self.cardinalities = list(map(lambda x: x[1], self.ccs))
        self.predicates = list(map(lambda x: x[0], predicate_symbols(self.formula)))
        t = []
        for predicate in self.constrained_predicates:
            t.append(range((self.domainsize ** self._get_arity(predicate)) + 1))
        self.d = list(itertools.product(*t))

        sum = 0
        wmc_poly = self._wmc()

        # Calculate the degree of the coefficient we need to extract
        accum = 1
        degree = 0
        for (predicate, cardinality) in self.ccs:
            degree += cardinality*accum
            accum *= self.domainsize**self._get_arity(predicate) + 1
        return wmc_poly[degree]

    def _check_cardinality(self, n):
        for p, predicate in enumerate(self.predicates):
            if predicate in dict(self.ccs):
                if n[p] != dict(self.ccs)[predicate]:
                    return False
        return True

    def _get_arity(self, symbol):
        for i in predicate_symbols(self.formula):
            if symbol == i[0]:
                return i[1]

    def _wmc(self):
        xs = []
        ys = []
        obj = WFOMC(self.formula, self.domainsize)

        for xi in range(1, len(self.d) + 2):
            xs.append(xi)
            weights = self.weights
            accum = 1
            for constrained_predicate in self.constrained_predicates:
                # we need to set the positive weights of the constrained predicates as xi, xi**(m_1+1), xi**((m_1+1)(m_2+1)), ...
                weights[constrained_predicate] = (xi ** accum, weights[constrained_predicate][1])
                accum *= self.domainsize**self._get_arity(constrained_predicate) + 1
            yi = obj.get_wfomc(weights)
            ys.append(int(yi))
        poly = fmpz_poly().interpolate(xs, ys)
        return poly.coeffs()