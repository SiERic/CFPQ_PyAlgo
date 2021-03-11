import pytest
from src.utils.useful_paths import LOCAL_CFPQ_DATA
from src.grammar.RSA import RecursiveStateMachine


def read_grammar(name="matching_pairs") -> RecursiveStateMachine:
    path_to_grammar = LOCAL_CFPQ_DATA.joinpath('undirected_tensor/grammars/').joinpath(name)
    return RecursiveStateMachine.read_rsa_from_file(path_to_grammar)


@pytest.mark.CI
def test_input():
    """ just test that there's no errors while converting """
    read_grammar("matching_pairs")
    read_grammar("matching_pairs_2types")


@pytest.mark.CI
def test_to_label_graph():
    grammar = read_grammar()
    label_graph = grammar.to_label_graph()
    assert label_graph["a"].__contains__((0, 1))
    assert label_graph["S"].__contains__((1, 2))
    assert label_graph["b"].__contains__((1, 3))
    assert label_graph["b"].__contains__((2, 3))
    assert not label_graph["a"].__contains__((0, 2))


@pytest.mark.CI
def test_get_box_id_from_state():
    grammar = read_grammar()
    assert grammar.get_box_id_from_state(0) == "S"
    assert grammar.get_box_id_from_state(3) == "S"


@pytest.mark.CI
def test_get_box_from_box_id():
    grammar = read_grammar()
    box = grammar.get_box_from_box_id("S")
    assert box.states == [0, 1, 2, 3]
    assert box.edges["b"] == [(1, 3), (2, 3)]


@pytest.mark.CI
def test_get_edges_by_nonterminal():
    grammar = read_grammar()
    assert grammar.get_edges_by_nonterminal("S") == [(1, 2)]


@pytest.mark.CI
def test_get_box_id_from_state_big_grammar():
    grammar = read_grammar("matching_pairs_2types")
    assert grammar.get_box_id_from_state(0) == "S"
    assert grammar.get_box_id_from_state(3) == "S"
    assert grammar.get_box_id_from_state(4) == "T"
    assert grammar.get_box_id_from_state(7) == "T"


@pytest.mark.CI
def test_get_eps_productions():
    grammar1 = read_grammar()
    assert grammar1.get_eps_productions() == []

    grammar2 = read_grammar("dyck1_1")
    assert grammar2.get_eps_productions() == [(0, 4, "S")]
