import functools

from aima3.logic import to_cnf, variables, predicate_symbols, subst, conjuncts
from aima3.utils import expr, Expr
import networkx as nx
from gmpy2 import mpq

from ddnnf import DDNNF
from translator import AIMA_to_Dimacs_Translator


class WFOMC:
    def __init__(self, formula, domainsize):
        self.aux_preds = {}
        self.fact = [None] * (domainsize + 1)
        self.n = domainsize
        self.precompute_pascal(self.n)
        self.fl = to_cnf(formula)
        self.initialized = False
        self.arity_two_symbols = [x for x in predicate_symbols(self.fl) if x[1] == 2]
        self.called_before = False

        if len(variables(self.fl)) > 2:
            raise Exception("Formula appears not to be in FO2!")

        for symbol in self.arity_two_symbols:
            old_pred_name = symbol[0]
            new_pred_name = old_pred_name + '_extra'
            x = Expr(old_pred_name, Expr('x'), Expr('x'))
            s = Expr(new_pred_name, Expr('x'))
            form = (~x | s) & (~s | x)
            self.fl = self.fl & form
            self.aux_preds[new_pred_name] = old_pred_name

        self.arity_one_symbols = [x for x in predicate_symbols(self.fl) if x[1] == 1]
        self._just_symbols = [x[0] for x in self.arity_one_symbols]
        self.m = len(self.arity_one_symbols)

        fl_new = subst({expr('x'): 1, expr('y'): 2}, self.fl & subst({expr('x'): expr('y'), expr('y'): expr('x')},
                                                                     self.fl))
        tr = AIMA_to_Dimacs_Translator()
        rscnf, self.rsmapping, rsobjmap = tr.to_dimacs_cnf(conjuncts(fl_new))
        self.rsddnnf = DDNNF()
        self.rsddnnf.from_cnf_object(rscnf, rsobjmap)

        fl_new = subst({expr('x'): 1, expr('y'): 1}, self.fl)
        tr = AIMA_to_Dimacs_Translator()
        tcnf, self.tmapping, tobjmap = tr.to_dimacs_cnf(conjuncts(fl_new))
        self.tddnnf = DDNNF()
        self.tddnnf.from_cnf_object(tcnf, tobjmap)

        indices = []
        for symbol, index in self.tmapping.items():
            if symbol.op in map(lambda x: x[0], self.arity_one_symbols):
                indices.append(index)
        self.projected_models = []
        in_indices = lambda x: x in indices or -x in indices
        for i in self.tddnnf.enumerate_models():
            s = set()
            t = []
            for x in filter(in_indices, i):
                if x > 0:
                    s.add(tobjmap[x].op)

            for (p, n) in self.arity_one_symbols:
                t.append(p in s)
            self.projected_models.append(t)

    def get_wfomc(self, weights):
        self.ijs = [(i, j) for i in range(len(self.projected_models)) for j in range(len(self.projected_models)) if
                    i < j]
        self.r = {}
        self.s = []
        self.t = []

        new_weights = weights.copy()
        for (symbol, arity) in predicate_symbols(self.fl):
            if arity == 1:
                new_weights[symbol] = (1, 1)
            if symbol in self.aux_preds:
                weights[symbol] = weights[
                    self.aux_preds[symbol]]

        for (i, j) in self.ijs:
            conditioning_list = []
            self.rsddnnf.annotate(new_weights)  # reset conditioning
            for index, symbol in enumerate(self.arity_one_symbols):
                symbol_to_add = symbol[0]
                if self.projected_models[i][index]:
                    conditioning_list.append(self.rsmapping[Expr(symbol_to_add, 1)])
                else:
                    conditioning_list.append(-self.rsmapping[Expr(symbol_to_add, 1)])
                if self.projected_models[j][index]:
                    conditioning_list.append(self.rsmapping[Expr(symbol_to_add, 2)])
                else:
                    conditioning_list.append(-self.rsmapping[Expr(symbol_to_add, 2)])
            self.rsddnnf.condition(conditioning_list)
            model_count = self.rsddnnf.get_model_count()
            self.r[(i, j)] = model_count

        for l in range(len(self.projected_models)):
            conditioning_list = []
            self.rsddnnf.annotate(new_weights)  # reset conditioning
            for index, symbol in enumerate(self.arity_one_symbols):
                symbol_to_add = symbol[0]
                if self.projected_models[l][index]:
                    conditioning_list.append(self.rsmapping[Expr(symbol_to_add, 1)])
                    conditioning_list.append(self.rsmapping[Expr(symbol_to_add, 2)])
                else:
                    conditioning_list.append(-self.rsmapping[Expr(symbol_to_add, 1)])
                    conditioning_list.append(-self.rsmapping[Expr(symbol_to_add, 2)])
            self.rsddnnf.condition(conditioning_list)
            model_count = self.rsddnnf.get_model_count()
            self.s.append(model_count)

        for projected_model in self.projected_models:
            w = 1
            for index, symbol in enumerate(self.arity_one_symbols):
                if projected_model[index]:
                    w *= weights[symbol[0]][0]
                else:
                    w *= weights[symbol[0]][1]
            self.t.append(w)

        # Find symmetric cliques using a greedy approach
        proj_model_range = list(range(len(self.projected_models)))
        self.cliques = []
        while len(proj_model_range) > 0:
            el = proj_model_range.pop()
            cur_clique = [el]
            for i in proj_model_range:
                if self._matches(i, cur_clique, el):
                    cur_clique.append(i)
            for ele in cur_clique[1:]:
                proj_model_range.remove(ele)
            self.cliques.append(cur_clique)
        self.cliques.sort(key=len)
        print("cliques", self.cliques)

        g = nx.Graph()
        g.add_nodes_from(range(len(self.cliques)))

        for i in range(len(self.cliques)):
            for j in range(len(self.cliques)):
                if i < j:
                    if self.cliques[i][0] < self.cliques[j][0]:
                        if self.r[(self.cliques[i][0], self.cliques[j][0])] != 1:
                            g.add_edge(i, j)
                    else:
                        if self.r[(self.cliques[j][0], self.cliques[i][0])] != 1:
                            g.add_edge(i, j)

        self_loops = set()

        for i in range(len(self.cliques)):
            for j in range(self.n + 1):
                if self.get_j_term(i, j) != 1:
                    self_loops.add(i)
                    break

        self.i2_ind = set()
        g_ind = set(nx.maximal_independent_set(g))

        self.i2_ind = g_ind.intersection(self_loops)
        self.i1_ind = g_ind - self.i2_ind

        self.ind = self.i1_ind.union(self.i2_ind)
        self.nonind = g.nodes - self.i1_ind - self.i2_ind
        print("I1, I2, nonind:", self.i1_ind, self.i2_ind, self.nonind)

        self.i2_ind = list(self.i2_ind)
        self.mapping = {}
        for x, y in enumerate(self.nonind):
            self.mapping[y] = x

        final = 0

        for selection in self._sums_leq(len(self.nonind), self.n):
            mu = tuple(selection)
            if sum(list(selection)) < self.n:
                mu = mu + (self.n - sum(selection),)
            coefficient = self._multinomial(mu)
            body = 1

            # Handle the nonind terms (ie, those in neither i1 nor i2)
            for i in range(len(self.cliques)):
                for j in range(len(self.cliques)):
                    if i in self.nonind and j in self.nonind:
                        if self.cliques[i][0] < self.cliques[j][0]:
                            body *= self.r[(self.cliques[i][0], self.cliques[j][0])] ** (
                                        selection[self.mapping[i]] * selection[self.mapping[j]])

            for l in self.nonind:
                body *= self.get_j_term(l, selection[self.mapping[l]])
                body *= self.t[self.cliques[l][0]] ** selection[self.mapping[l]]

            # Now deal with the i2 terms
            self.cache = {}
            mul = self.get_term(len(self.i2_ind), 0, selection)

            final += coefficient * body * mul

        self.get_j_term.cache_clear()
        self.get_d_term.cache_clear()
        return final

    def get_term(self, iv, bign, selection):
        if (iv, bign) in self.cache:
            return self.cache[(iv, bign)]

        if iv == 0:
            accum = 0
            for j in self.i1_ind:
                temp = self.t[self.cliques[j][0]]
                for i in self.nonind:
                    if self.cliques[j][0] < self.cliques[i][0]:
                        temp *= self.r[(self.cliques[j][0], self.cliques[i][0])] ** selection[self.mapping[i]]
                    else:
                        temp *= self.r[(self.cliques[i][0], self.cliques[j][0])] ** selection[self.mapping[i]]
                accum += temp
            accum = accum ** (self.n - sum(selection) - bign)
            self.cache[(iv, bign)] = accum
            return accum
        else:
            sumtoadd = 0
            s = self.i2_ind[len(self.i2_ind) - iv]
            for nval in range((self.n - sum(selection) - bign) + 1):
                smul = self.mycomb(self.n - sum(selection) - bign, nval)
                smul *= self.get_j_term(s, nval)
                smul *= self.t[self.cliques[s][0]] ** nval

                for i in self.nonind:
                    if self.cliques[s][0] < self.cliques[i][0]:
                        smul *= self.r[(self.cliques[s][0], self.cliques[i][0])] ** (selection[self.mapping[i]] * nval)
                    else:
                        smul *= self.r[(self.cliques[i][0], self.cliques[s][0])] ** (selection[self.mapping[i]] * nval)
                smul *= self.get_term(iv - 1, bign + nval, selection)
                sumtoadd += smul
            self.cache[(iv, bign)] = sumtoadd
            return sumtoadd

    @functools.lru_cache(maxsize=None)
    def _multinomial(self, lst):
        ret = 1
        tmplist = lst
        while len(tmplist) > 1:
            ret *= self.mycomb(sum(tmplist), tmplist[-1])
            tmplist = tmplist[:-1]
        return ret


    # Return all tuples of length length whose values sum up exactly to total_sum
    def _sums(self, length, total_sum):
        if length == 1:
            yield (total_sum,)
        else:
            for value in range(total_sum + 1):
                for permutation in self._sums(length - 1, total_sum - value):
                    yield (value,) + permutation

    # Return all tuples of length length whose values sum up to no greater than total_sum
    def _sums_leq(self, length, total_sum):
        if length == 0:
            yield ()
            return
        if length == 1:
            for i in range(total_sum + 1):
                yield (i,)
        else:
            for value in range(total_sum + 1):
                for permutation in self._sums_leq(length - 1, total_sum - value):
                    yield (value,) + permutation

    def _matches(self, i, cur_clique, el):
        if self.s[el] != self.s[i] or self.t[el] != self.t[i]:
            return False
        if len(cur_clique) > 1:
            o = min(cur_clique[0], cur_clique[1])
            t = max(cur_clique[0], cur_clique[1])
            val = self.r[(o, t)]
            for c in cur_clique:
                a = min(c, i)
                b = max(c, i)
                if self.r[(a, b)] != val:
                    return False
        for j in range(len(self.projected_models)):
            if i == j or j in cur_clique:
                continue
            o = min(cur_clique[0], j)
            t = max(cur_clique[0], j)
            val = self.r[(o, t)]
            a = min(i, j)
            b = max(i, j)
            if val != self.r[(a, b)]:
                return False

        return True

    @functools.lru_cache(maxsize=None)
    def get_j_term(self, l, nhat):
        if len(self.cliques[l]) == 1:
            thesum = self.s[self.cliques[l][0]] ** (int(nhat * (nhat - 1) / 2))
        else:
            i = min(self.cliques[l][0], self.cliques[l][1])
            j = max(self.cliques[l][0], self.cliques[l][1])
            r = self.r[(i,j)]
            thesum = (r ** self.mycomb(nhat, 2)) * self.get_d_term(l, 1, len(self.cliques[l]), nhat)

        return thesum

    @functools.lru_cache(maxsize=None)
    def get_d_term(self, l, cur, maxi, n):
        i = min(self.cliques[l][0], self.cliques[l][1])
        j = max(self.cliques[l][0], self.cliques[l][1])
        r = self.r[(i, j)]
        s = self.s[self.cliques[l][0]]
        if cur == maxi:
            ret = mpq(s, r) ** self.mycomb(n, 2)
        else:
            ret = 0
            for ni in range(n+1):
                mult = self.mycomb(n, ni)
                mult *= mpq(s, r) ** self.mycomb(ni, 2)
                mult *= self.get_d_term(l, cur+1, maxi, n - ni)
                ret += mult
        return ret

    def mycomb(self, a, b):
        if a < b:
            return 0
        elif b == 0:
            return 1
        else:
            return self.pt[a][b]

    def precompute_pascal(self, n):
        self.pt = []
        l = [1]
        for i in range(n+1):
            self.pt.append(l)
            newlist = []
            newlist.append(l[0])
            for i in range(len(l) - 1):
                newlist.append(l[i] + l[i + 1])
            newlist.append(l[-1])
            l = newlist