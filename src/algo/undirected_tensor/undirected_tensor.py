from typing import Tuple, Callable

from pygraphblas import Matrix, BOOL
from pathlib import Path

from src.algo.algo_interface import CFPQAlgo
from src.graph.label_graph import LabelGraph
from src.grammar.RSA import RecursiveStateMachine


def _from_product(v: int, graph_size: int) -> Tuple[int, int]:
    return v // graph_size, v % graph_size  # state, vertex


def _to_product(state: int, v: int, graph_size: int) -> int:
    return state * graph_size + v


class UndirectedTensorSolver(CFPQAlgo):
    def __init__(self, path_to_graph: Path, path_to_grammar: Path):
        super(UndirectedTensorSolver, self).__init__(path_to_graph, path_to_grammar)
        self.graph = LabelGraph.from_txt(str(path_to_graph) + ".txt")
        self.grammar = RecursiveStateMachine.read_rsa_from_file(str(path_to_grammar))

    class EdgeQueue:

        class DisjointSetUnion:
            def __init__(self, grammar: RecursiveStateMachine, graph: LabelGraph, queue):
                product_size = grammar.states_number * graph.matrices_size
                self.graph_size = graph.matrices_size
                self.grammar = grammar
                self.queue = queue
                self.parent = [i for i in range(product_size)]
                self.rank = [0 for i in range(product_size)]
                self.initial = [[] for i in range(product_size)]
                self.final = [[] for i in range(product_size)]
                self.box = [grammar.get_box_id_from_state(_from_product(i, self.graph_size)[0]) for i in range(product_size)]
                for nonterminal in grammar.nonterminals:
                    box = grammar.get_box_from_box_id(nonterminal)
                    for v in range(graph.matrices_size):
                        prod_init = _to_product(box.initial_state, v, self.graph_size)
                        self.initial[prod_init].append(prod_init)
                        for final in box.final_states:
                            prod_final = _to_product(final, v, self.graph_size)
                            self.final[prod_final].append(prod_final)
                print()
                print(self.initial)
                print(self.final)

            def _get_root(self, v: int) -> int:
                if self.parent[v] == v:
                    return v
                self.parent[v] = self._get_root(self.parent[v])
                return self.parent[v]

            def _add_new_edges(self, u: int, v: int) -> None:
                for start in self.initial[u]:
                    for end in self.final[v]:
                        start_state, start_v = _from_product(start, self.graph_size)
                        end_v = _from_product(end, self.graph_size)[1]
                        label = self.grammar.get_box_id_from_state(start_state)
                        print("New: ", start, end, label)
                        for (start_state, end_state) in self.grammar.get_edges_by_nonterminal(label):
                            self.queue.add_edge(_to_product(start_state, start_v, self.graph_size),
                                                _to_product(end_state, end_v, self.graph_size), label)

            def unite(self, v: int, u: int) -> None:
                v = self._get_root(v)
                u = self._get_root(u)
                if u == v:
                    return
                if self.rank[v] < self.rank[u]:
                    v, u = u, v
                print(u, v)
                self._add_new_edges(u, v)
                self._add_new_edges(v, u)
                self.initial[v].extend(self.initial[u])
                self.final[v].extend(self.final[u])
                self.rank[v] = max(self.rank[v], self.rank[u] + 1)
                self.parent[u] = v

        def __init__(self, grammar: RecursiveStateMachine, graph: LabelGraph):
            self._queue = []
            self._queue_start = 0
            self.graph = graph
            self.grammar = grammar
            self.dsu = self.DisjointSetUnion(grammar, graph, self)

        def add_edge(self, start: int, end: int, label: int):
            print(_from_product(start, self.graph.matrices_size), _from_product(end, self.graph.matrices_size), label)
            self._queue.append((start, end, label))

        def go(self) -> LabelGraph:
            while self._queue_start < len(self._queue):
                start, end, label = self._queue[self._queue_start]
                self._queue_start += 1
                start_state, start_v = _from_product(start, self.graph.matrices_size)
                end_state, end_v = _from_product(end, self.graph.matrices_size)
                self.graph[label][start_v, end_v] = True
                self.dsu.unite(start, end)
            return self.graph

    def solve(self) -> LabelGraph:
        grammar_graph = self.grammar.to_label_graph()
        queue = self.EdgeQueue(self.grammar, self.graph)
        for label in self.grammar.alphabet:
            product = grammar_graph[label].kronecker(self.graph[label])
            product_size = grammar_graph.matrices_size * self.graph.matrices_size
            for u in range(product_size):
                for v in range(product_size):
                    if product.__contains__((u, v)):
                        queue.add_edge(u, v, label)
        for (start_state, end_state, nonterminal) in self.grammar.get_eps_productions():
            for v in range(self.graph.matrices_size):
                queue.add_edge(_to_product(start_state, v, self.graph.matrices_size), _to_product(end_state, v, self.graph.matrices_size), nonterminal)

        return queue.go()

