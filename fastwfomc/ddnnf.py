import itertools
import subprocess
import tempfile

class Node():
    def __init__(self, label=None, weight=1, children=[], decision=None):
        self.label = label
        self.children = children
        self.weight = weight


class DDNNF():
    def __init__(self):
        self.varobjmap = None
        self.treenodes = []
        self.totalVariables = None

    def rootnode(self):
        return self.treenodes[-1]

    def from_cnf_object(self, input_cnf, varobjmap):
        self.varobjmap = varobjmap
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
            input_cnf.to_fp(tf)
            tf.flush()
            with tempfile.NamedTemporaryFile(mode='r', delete=False) as tfout:
                subprocess.check_output(['./bin/dsharp', '-smoothNNF', '-Fnnf', tfout.name, tf.name],
                                        universal_newlines=True)
                self._parse(tfout.readlines())

    def _parse(self, treetext):
        '''Parses the d-DNNF to a tree-like object'''
        nodelen = 0
        for node in treetext:
            node = node.split()
            if node[0] == 'c':
                continue
            elif node[0] == 'nnf':
                self.totalVariables = int(node[3])
            elif node[0] == 'L':
                self.treenodes.append(Node(label=int(node[1])))
                nodelen += 1
            elif node[0] == 'A':
                if node[1] == '0':
                    self.treenodes.append(Node(label='T ' + str(nodelen)))
                else:
                    andnode = Node(label='A ' + str(nodelen))
                    andnode.children = list(map(lambda x: self.treenodes[int(x)], node[2:]))
                    self.treenodes.append(andnode)
                nodelen += 1
            elif node[0] == 'O':
                if node[2] == '0':
                    self.treenodes.append(Node(label='F ' + str(nodelen)))
                else:
                    ornode = Node(label='O ' + str(nodelen), decision=int(node[1]))
                    ornode.children = list(map(lambda x: self.treenodes[int(x)], node[3:]))
                    self.treenodes.append(ornode)
                nodelen += 1

    def get_model_count(self):
        return self._get_model_count(self.rootnode())

    def _get_model_count(self, node):
        ''' note that we assume a smooth d-DNNF here '''
        if str(node.label)[0] == 'A':
            result = 1
            for child in node.children:
                result *= self._get_model_count(child)
        elif str(node.label)[0] == 'O':
            result = self._get_model_count(node.children[0]) + self._get_model_count(node.children[1])
        else:
            if isinstance(node.label, str):
                if node.label[0] == 'F':
                    result = 0
                elif node.label[0] == 'T':
                    result = 1
            else:
                result = node.weight
        return result

    def annotate(self, weights):
        self._annotate(self.rootnode(), weights)

    def _annotate(self, node, weights):
        if isinstance(node.label, int):
            if node.label > 0:
                if len(self.varobjmap[node.label].args) == 2 and self.varobjmap[node.label].args[0] == self.varobjmap[node.label].args[1]:
                    node.weight = 1
                else:
                    node.weight = weights[self.varobjmap[node.label].op][0]
            else:
                if len(self.varobjmap[-node.label].args) == 2 and self.varobjmap[-node.label].args[0] == self.varobjmap[-node.label].args[1]:
                    node.weight = 1
                else:
                    node.weight = weights[self.varobjmap[-node.label].op][1]
        for child in node.children:
            self._annotate(child, weights)

    def condition(self, nodes):
        for node in self.treenodes:
            if isinstance(node.label, int) and -node.label in nodes:
                node.weight = 0

    def enumerate_models(self):
        return self._enumerate_models(self.rootnode())

    def _enumerate_models(self, node):
        if str(node.label)[0] == 'A':
            result = set()
            child_models = map(self._enumerate_models, node.children)
            product = itertools.product(*map(self._enumerate_models, node.children))
            for i in product:
                tr = frozenset()
                tr = tr.union(*i)
                result.add(tr)
        elif str(node.label)[0] == 'O':
            result = self._enumerate_models(node.children[0]).union(self._enumerate_models(node.children[1]))
        else:
            if isinstance(node.label, str):
                if node.label[0] == 'F':
                    result = set()
                elif node.label[0] == 'T':
                    result = {{}}
            else:
                result = {frozenset([node.label])}
        return result