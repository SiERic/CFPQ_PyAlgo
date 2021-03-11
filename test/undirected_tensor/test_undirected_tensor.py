import pytest
from src.utils.useful_paths import LOCAL_CFPQ_DATA
from src.algo.undirected_tensor.undirected_tensor import UndirectedTensorSolver


def read_solver(grammar_name, graph_name) -> UndirectedTensorSolver:
    path_to_graph = LOCAL_CFPQ_DATA.joinpath('undirected_tensor/graphs/').joinpath(graph_name)
    path_to_grammar = LOCAL_CFPQ_DATA.joinpath('undirected_tensor/grammars/').joinpath(grammar_name)
    return UndirectedTensorSolver(path_to_graph, path_to_grammar)


@pytest.mark.CI
def test():
    solver = read_solver("matching_pairs", "ab_bamboo")
    closure = solver.solve()
    # print()
    # for label in closure.matrices:
    #     print("Label: " + label)
    #     print(closure[label])
    assert closure["S"].nvals == 8
    assert closure["S"][0, 4]
    assert closure["S"][1, 3]


@pytest.mark.CI
def test_eps():
    solver = read_solver("dyck1_1", "ab_bamboo")
    closure = solver.solve()
    assert closure["S"].nvals == 9
    assert closure["S"][0, 4]
    assert closure["S"][1, 3]


@pytest.mark.CI
def test_dyck1():
    solver = read_solver("dyck1_1", "ab_bamboo_dyck")
    closure = solver.solve()
    assert closure["S"].nvals == 11
    assert closure["S"][0, 2]
    assert closure["S"][0, 4]
    assert not closure["S"].__contains__((1, 3))
