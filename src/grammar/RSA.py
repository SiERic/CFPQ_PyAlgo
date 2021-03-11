from typing import List, Dict, Tuple

from src.graph.label_graph import LabelGraph


class RecursiveStateMachine:
    """
    Class for Recursive State Machine (RSM) -- ans equivalent for Context-free Grammar

    (Σ, M, B) -- Alphabet, Nonterminals (boxes labels), Boxes
    Each box is a Finite State Machine (Automaton), but labels on edges can include nonterminals
    For simplicity all states are numbered sequentially in [0..states_number)
    """

    class Box:
        """
        RSM box -- Finite Deterministic State Machine

        (Σ, M, Q, q_0, F, δ) -- Alphabet, Nonterminals, States, Initial state, Final states, Transition function

        There cannot be any eps-arcs except eps-productions (eps-arc from initial to final state)
        """

        def __init__(self, alphabet: List[str], nonterminals: List[str], states: List[int], initial_state: int,
                     final_states: List[int], edges: Dict[str, List[Tuple[int, int]]]):
            self.alphabet = alphabet
            self.nonterminals = nonterminals
            self.states = states
            self.initial_state = initial_state
            self.final_states = final_states
            self.edges = edges

        @staticmethod
        def read_box_from_file(fin, alphabet: List[str], nonterminals: List[str], states_number: int):
            states = list(map(int, fin.readline().split()))
            initial_state = int(fin.readline())
            final_states = list(map(int, fin.readline().split()))
            edge_number = int(fin.readline())
            edges = dict([(i, []) for i in alphabet + nonterminals + ["eps"]])
            for i in range(edge_number):
                v, to, label = fin.readline().split()
                assert (0 <= int(v) < states_number)
                assert (0 <= int(to) < states_number)
                assert (label in alphabet + nonterminals + ["eps"])
                if label == "eps":
                    assert (int(v) == initial_state and int(to) in final_states)
                edges[label].append((int(v), int(to)))
            return RecursiveStateMachine.Box(alphabet, nonterminals, states, initial_state, final_states, edges)

    def __init__(self, alphabet: List[str], nonterminals: List[str], states_number: int, boxes: Dict[str, Box]):
        self.alphabet = alphabet
        self.nonterminals = nonterminals
        self.states_number = states_number
        self._boxes = boxes

        self._state_to_box = [" " for i in range(states_number)]
        self._label_to_edges = dict([(i, []) for i in alphabet + nonterminals + ["eps"]])
        for nonterminal, box in boxes.items():
            for state in box.states:
                self._state_to_box[state] = nonterminal
            for label, edges in box.edges.items():
                self._label_to_edges[label] += edges

    def to_label_graph(self) -> LabelGraph:
        graph = LabelGraph(self.states_number)
        for box in self._boxes.values():
            for label, edges in box.edges.items():
                for (v, to) in edges:
                    graph[label][v, to] = True
        return graph

    def get_box_id_from_state(self, state: int) -> str:
        return self._state_to_box[state]

    def get_box_from_box_id(self, nonterminal: str) -> Box:
        return self._boxes[nonterminal]

    def get_edges_by_nonterminal(self, nonterminal: str) -> List[Tuple[int, int]]:
        return self._label_to_edges[nonterminal]

    def get_eps_productions(self) -> List[Tuple[int, int, str]]:
        ans = []
        for nonterminal, box in self._boxes.items():
            for (v, to) in box.edges.get("eps", []):
                ans.append((v, to, nonterminal))
        return ans

    @staticmethod
    def read_rsa_from_file(filename: str):
        fin = open(filename, "r")
        alphabet = list(fin.readline().split())
        nonterminals = list(fin.readline().split())
        states_number = int(fin.readline())
        boxes = dict()
        for i in nonterminals:
            boxes[i] = RecursiveStateMachine.Box.read_box_from_file(fin, alphabet, nonterminals, states_number)
        fin.close()
        return RecursiveStateMachine(alphabet, nonterminals, states_number, boxes)
