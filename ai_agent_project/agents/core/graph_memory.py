import networkx as nx

class GraphMemory:
    """
    🧠 Stores structured knowledge in a graph format.
    Used for deep reasoning and knowledge association.
    """

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_knowledge(self, subject: str, relation: str, obj: str):
        """Adds a knowledge triplet to the graph."""
        self.graph.add_edge(subject, obj, relation=relation)

    def get_relationships(self, node: str) -> list:
        """Returns relationships for a given node."""
        return list(self.graph.edges(node, data=True))
