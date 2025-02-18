"""

A GraphMemory class which manipulates and stores knowledge data in a graph-like structure using the Networkx library.

Attributes: 
-----------
graph : nx.DiGraph
    An instance of a directed graph from the Networkx library.

Methods: 
--------
add_knowledge(subject: str, relation: str, obj: str) -> None:
    Adds a knowledge triplet {subject - relation - object} to the created graph instance.
    
get_relationships(node: str) -> list:
    Fetch all
"""

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
