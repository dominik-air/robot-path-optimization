import pytest
from sim.utils import make_tuples_out_of_child_elements

make_tuples_out_of_child_elements_test_sets = [
    ([[[1, 2], [3, 4]], [[5, 6], [8, 9]]], [[(1, 2), (3, 4)], [(5, 6), (8, 9)]]),
    ([[1, 2], [3, 4]], [(1, 2), (3, 4)]),
    ([1, 2], [1, 2]),
]


@pytest.mark.parametrize("input_list, expected_list", make_tuples_out_of_child_elements_test_sets)
def test_make_tuples_out_of_child_elements(input_list, expected_list):
    test_list = make_tuples_out_of_child_elements(input_list)
    assert test_list == expected_list
