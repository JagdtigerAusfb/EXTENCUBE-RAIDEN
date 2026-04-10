import kociemba
import json


def count_moves(solution_str):
    if not solution_str.strip():
        return 0
    return len(solution_str.strip().split())


def converter_movimentos(seq):
    tabela = {
        "U": "A", "U'": "B", "U2": "C",
        "R": "D", "R'": "E", "R2": "F",
        "F": "G", "F'": "H", "F2": "I",
        "D": "J", "D'": "K", "D2": "L",
        "L": "M", "L'": "N", "L2": "O",
        "B'": "P", "B": "Q", "B2": "R"
    }
    return "".join(tabela[m] for m in seq.split() if m in tabela)


def invert_moves(sequence: str) -> str:
    inverse = {
        "U": "U'", "U'": "U", "U2": "U2",
        "R": "R'", "R'": "R", "R2": "R2",
        "F": "F'", "F'": "F", "F2": "F2",
        "L": "L'", "L'": "L", "L2": "L2",
        "B": "B'", "B'": "B", "B2": "B2",
        "D": "D'", "D'": "D", "D2": "D2",
    }
    moves = sequence.split()
    inverted = [inverse[m] for m in reversed(moves)]
    return " ".join(inverted)


def solve_from_file(json_path="cube_state.json"):
    try:
        with open(json_path, "r") as f:
            data = json.load(f)

        state = data["cube_string"]

        solution = kociemba.solve(state)
        move_count = count_moves(solution)
        robot_sequence = converter_movimentos(solution)
        inverse_sequence = invert_moves(solution)
        inverted_sequence = converter_movimentos(inverse_sequence)

        return {
            "solution": solution,
            "move_count": move_count,
            "robot_sequence": robot_sequence,
            "inverted_sequence": inverted_sequence
        }

    except Exception as e:
        return {
            "error": str(e)
        }