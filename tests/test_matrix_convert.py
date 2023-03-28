import tsplib95
from solvers.convert import convert_distance_matrix_to_string, render_tsplib_file

def test_matrix_conversion_to_string():
    matrix = [
        [0, 1, 2, 4, 5, 6],
        [1, 0, 3, 8, 9, 10],
        [2, 3, 0, 3, 4, 5],
        [4, 8, 3, 0, 8, 9],
        [5, 9, 4, 8, 0, 4],
        [6, 10, 5, 9, 4, 0],
    ]
    matrix_str = " 0 1 2 4 5 6\n 1 0 3 8 9 10\n 2 3 0 3 4 5\n 4 8 3 0 8 9\n 5 9 4 8 0 4\n 6 10 5 9 4 0\n"
    assert convert_distance_matrix_to_string(matrix) == matrix_str
