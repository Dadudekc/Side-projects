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
from agents.core.AgentBase import AgentBase

class GraphMemory(AgentBase):
    """
    Stores structured knowledge in a graph format.
    Used for deep reasoning and knowledge association.
    """

    def __init__(self):
        super().__init__(name="GraphMemory", project_name="KnowledgeGraph")
        self.graph = nx.DiGraph()

    def add_knowledge(self, subject: str, relation: str, obj: str):
        """Adds a knowledge triplet to the graph."""
        self.graph.add_edge(subject, obj, relation=relation)

    def get_relationships(self, node: str) -> list:
        """Returns relationships for a given node."""
        return list(self.graph.edges(node, data=True))

    def solve_task(self, task: str, **kwargs):
        """Solves graph-based reasoning tasks."""
        if task == "add_knowledge":
            self.add_knowledge(kwargs["subject"], kwargs["relation"], kwargs["obj"])
            return {"status": "success", "message": "Knowledge added."}
        elif task == "get_relationships":
            return {"status": "success", "relationships": self.get_relationships(kwargs["node"])}
        return {"status": "error", "message": f"Invalid task '{task}'"}

    def describe_capabilities(self) -> str:
        """Returns the capabilities of GraphMemory."""
        return "Handles structured knowledge storage and retrieval using a graph-based approach."
