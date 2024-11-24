import networkx as nx
import time
from src.crypto.hash import generate_hash


class DAG:
    def __init__(self):
        self.graph = nx.DiGraph()  # Directed graph for transactions
        self.create_genesis_transaction()

    def create_genesis_transaction(self):
        """Create the first (genesis) transaction in the DAG."""
        genesis_transaction = {
            'id': '0',
            'timestamp': time.time(),
            'sender': None,
            'receiver': None,
            'action_type': "genesis",
            'amount': 0,
            'content': None,
            'parents': [],
            'hash': generate_hash({})
        }
        self.graph.add_node(genesis_transaction['id'], data=genesis_transaction)

    def add_transaction(self, sender, receiver=None, action_type="transfer", amount=None, content=None, parent_ids=None):
        """
        Add a new transaction to the DAG.
        Supports various action types:
        - "transfer": Transfer of cryptocurrency.
        - "comment": Adding a comment to a transaction.
        - "like": Liking a specific transaction.
        """
        parent_ids = parent_ids or []
        new_transaction = {
            'id': str(len(self.graph)),
            'timestamp': time.time(),
            'sender': sender,
            'receiver': receiver,
            'action_type': action_type,
            'amount': amount,
            'content': content,  # For actions like comments
            'parents': parent_ids,
        }
        new_transaction['hash'] = generate_hash(new_transaction)

        # Add the transaction to the graph
        self.graph.add_node(new_transaction['id'], data=new_transaction)
        for parent_id in parent_ids:
            self.graph.add_edge(new_transaction['id'], parent_id)

        return new_transaction

    def validate_transaction(self, transaction_id):
        """
        Validate a transaction by ensuring its parents exist.
        For a transaction to be valid:
        - All its parent transactions must exist in the DAG.
        """
        if transaction_id not in self.graph:
            return False
        parents = list(self.graph.predecessors(transaction_id))
        return all(parent in self.graph for parent in parents)

    def visualize(self):
        """
        Visualize the DAG using NetworkX and Matplotlib.
        Nodes display their action type for clarity.
        """
        import matplotlib.pyplot as plt

        pos = nx.spring_layout(self.graph)  # Layout for visualization
        nx.draw(self.graph, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=10, font_weight="bold")
        labels = nx.get_node_attributes(self.graph, 'data')
        nx.draw_networkx_labels(self.graph, pos, labels={node: f"{data['data']['action_type']}" for node, data in self.graph.nodes(data=True)})
        plt.title("DAG Visualization")
        plt.show()
