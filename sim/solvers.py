from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from typing import List, Callable


TSP_Solver = Callable[[List[List[int]]], List[int]]


def ortools_solver(matrix: List[List[int]]) -> List[int]:
    """Solves tsp problem defined with a cost matrix.
    Returns list of matrix's row indices that represents node order that forms an approx. minimal Hamiltonian cycle.
    Based on: https://developers.google.com/optimization/routing/tsp.
    """

    def extract_path(manager, routing, solution):
        index = routing.Start(0)
        optimal_route = []
        while not routing.IsEnd(index):
            optimal_route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        return optimal_route

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return matrix[from_node][to_node]

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(matrix), 1, 0)

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)
    return extract_path(manager, routing, solution)
