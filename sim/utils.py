import json


def make_tuples_out_of_child_elements(items: list) -> list:
    """Transforms a repeatedly nested list of lists into one with tuples on the lowest level."""
    new_list = []
    for item in items:
        try:
            content_type = item[0]
        except TypeError:
            return items
        if isinstance(content_type, list):
            new_list.append(make_tuples_out_of_child_elements(item))
        else:
            new_list.append(tuple(item))
    return new_list


def load_graph_data_from_json(filename: str) -> dict:
    with open(filename) as f:
        converted_data = {}
        for key, list_of_lists in json.load(f).items():
            converted_data[key] = make_tuples_out_of_child_elements(list_of_lists)
    return converted_data
