from src.dag.dag import DAG
from src.crypto.signature import Wallet
from src.network.node import Node
import asyncio


def main():
    # Initialize DAG and wallets
    dag = DAG()
    alice_wallet = Wallet()
    bob_wallet = Wallet()

    # Add transactions
    tx1 = dag.add_transaction(
        sender=alice_wallet.get_public_key(),
        receiver=bob_wallet.get_public_key(),
        action_type="transfer",
        amount=50,
        parent_ids=['0']
    )
    alice_wallet.update_balance(-50)
    bob_wallet.update_balance(50)
    alice_wallet.add_transaction_to_history(tx1)
    bob_wallet.add_transaction_to_history(tx1)

    # Add a comment action
    tx2 = dag.add_transaction(
        sender=bob_wallet.get_public_key(),
        receiver=None,
        action_type="comment",
        content="This is a comment!",
        parent_ids=[tx1['id']]
    )

    # Visualize the DAG
    dag.visualize()

    # Start the P2P network (asynchronous)
    node = Node("localhost", 8765)
    asyncio.run(node.start_server())

if __name__ == "__main__":
    main()
