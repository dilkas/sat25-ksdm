from aima3.logic import *
from pysat.formula import CNF

# The following is a fairly direct adaptation of the very nice,
# slim wrapper to minisat provided by https://github.com/netom/satispy
# I'm not using satispy directly b/c it implements its own cnf rep.
# so I'm adapting the aima rep to communication with minisat.

def literal_name(literal):
    if literal.op == '~':
        return literal.args[0].op
    else:
        return literal.op


def prop_symbols_from_KB(kb):
    """ CTM: This is very inefficient,
    but I can't figure out why direct list iteration doesn't work """
    return prop_symbols(clauses_to_conjunct(kb.clauses))


def clauses_to_conjunct(clause_list):
    """ coerce a list of clauses into a conjunction """
    conj = Expr('&')
    conj.args = clause_list
    return conj


def prop_symbols_from_clause_list(clause_list):
    return prop_symbols(clauses_to_conjunct(clause_list))


class AIMA_to_Dimacs_Translator(object):

    def __init__(self):
        self.varname_dict = {}
        self.varobj_dict = {}

    def varname(self, vo):
        return self.varname_dict[vo]

    def varobj(self, v):
        return self.varobj_dict[v]

    def to_dimacs_cnf(self, clauses):
        """Convert AIMA cnf expression to Dimacs cnf string

        clauses: list of clauses in AIMA cnf

        In the converted Cnf there will be only numbers for
        variable names. The conversion guarantees that the
        variables will be numbered alphabetically.
        """
        self.varname_dict = {}
        self.varobj_dict = {}
        variables = prop_symbols_from_clause_list(clauses)
        ret = CNF()
        varis = dict(zip(sorted(variables, key=lambda v: v.op),
                         range(1, len(variables) + 1)))
        for var in varis:
            self.varname_dict[var] = varis[var]
            self.varobj_dict[varis[var]] = var

        for clause in clauses:
            dimacs_vlist = []
            if clause.op == '|':
                for var in clause.args:
                    if var.op == '~':
                        dimacs_vlist.append(-1*self.varname_dict[var.args[0]])
                    else:
                        dimacs_vlist.append(self.varname_dict[var])
                ret.append(dimacs_vlist)
            elif clause.op == '~':
                ret.append([-1*self.varname_dict[clause.args[0]]])
            else:
                ret.append([self.varname_dict[clause]])

        return ret, self.varname_dict, self.varobj_dict
