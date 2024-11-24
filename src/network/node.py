import asyncio
import websockets
import json

class Node:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connected_nodes = []

    async def start_server(self):
        """Start the WebSocket server."""
        async with websockets.serve(self.handle_connection, self.host, self.port):
            print(f"Node running at ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever

    async def handle_connection(self, websocket, path):
        """Handle incoming connections and messages."""
        async for message in websocket:
            print(f"Received: {message}")
            # Broadcast the transaction to other connected nodes
            for node in self.connected_nodes:
                await node.send(message)

    async def connect_to_node(self, uri):
        """Connect to another node."""
        websocket = await websockets.connect(uri)
        self.connected_nodes.append(websocket)
        print(f"Connected to node: {uri}")

    async def broadcast_transaction(self, transaction):
        """Broadcast a transaction to all connected nodes."""
        message = json.dumps(transaction)
        for node in self.connected_nodes:
            await node.send(message)
