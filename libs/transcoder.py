import pydotplus


def transcode_to_graphviz(infrastructure):
    graph_infra = pydotplus.Graph()

    for instance in infrastructure.instances:
        graph_infra.add_node(pydotplus.Node(instance.name))

    return graph_infra
