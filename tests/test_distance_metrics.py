import pytest
from sim.distance_metrics import manhattan_distance

manhattan_distance_test_sets = [[(20, 20), (30, 40), 30], [(-20, 20), (30, -40), 110], [(-20, -20), (-30, -40), 30]]


@pytest.mark.parametrize("n1, n2, expected_distance", manhattan_distance_test_sets)
def test_manhattan_distance(n1, n2, expected_distance):
    actual_distance = manhattan_distance(n1, n2)
    assert actual_distance == expected_distance
