from cryptography.hazmat.primitives import serialization
from flask import Flask, request, jsonify
from src.dag.dag import DAG
from src.crypto.signature import Wallet, verify_signature
import json
import os
import time

app = Flask(__name__)

# Initialize the DAG, wallet storage, alias mapping, and login challenges
dag = DAG()
wallets = {}
aliases = {}
login_challenges = {}
ALIAS_FILE = "aliases.json"
CHALLENGE_EXPIRY = 300  # 5 minutes for challenge expiration

# Load and save aliases for persistence
def load_aliases():
    if os.path.exists(ALIAS_FILE):
        with open(ALIAS_FILE, 'r') as file:
            global aliases
            aliases = json.load(file)

def save_aliases():
    with open(ALIAS_FILE, 'w') as file:
        json.dump(aliases, file)

load_aliases()

@app.route('/create_wallet', methods=['POST'])
def create_wallet():
    """Create a new wallet and return its keys."""
    wallet = Wallet()
    public_key = wallet.get_public_key()
    private_key = wallet.private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    wallets[public_key] = wallet
    return jsonify({
        "public_key": public_key,
        "private_key": private_key,
        "balance": wallet.balance,
        "message": "Wallet created successfully. Keep your private key secure!"
    })

@app.route('/register_alias', methods=['POST'])
def register_alias():
    """Register an alias for a public key."""
    data = request.json
    alias = data['alias']
    public_key = data['public_key']

    if alias in aliases:
        return jsonify({"error": "Alias already exists"}), 400

    if public_key not in wallets:
        return jsonify({"error": "Invalid public key"}), 400

    aliases[alias] = public_key
    save_aliases()
    return jsonify({
        "message": f"Alias '{alias}' registered successfully.",
        "public_key": public_key
    })

@app.route('/resolve_alias', methods=['POST'])
def resolve_alias():
    """Resolve an alias to its public key."""
    data = request.json
    alias = data['alias']
    public_key = aliases.get(alias)

    if not public_key:
        return jsonify({"error": "Alias not found"}), 404

    return jsonify({"public_key": public_key})

@app.route('/send_tokens_with_alias', methods=['POST'])
def send_tokens_with_alias():
    """Transfer tokens using aliases."""
    data = request.json
    sender_alias = data['sender_alias']
    receiver_alias = data['receiver_alias']
    amount = data['amount']

    sender_public_key = aliases.get(sender_alias)
    receiver_public_key = aliases.get(receiver_alias)

    if not sender_public_key or not receiver_public_key:
        return jsonify({"error": "Invalid alias"}), 400

    sender_wallet = wallets.get(sender_public_key)
    receiver_wallet = wallets.get(receiver_public_key)

    if sender_wallet and receiver_wallet:
        if sender_wallet.balance >= amount:
            tx = dag.add_transaction(
                sender=sender_public_key,
                receiver=receiver_public_key,
                action_type="transfer",
                amount=amount,
                parent_ids=['0']  # Simplified parent logic
            )
            sender_wallet.update_balance(-amount)
            receiver_wallet.update_balance(amount)
            return jsonify({"message": "Transaction successful", "transaction": tx})
        else:
            return jsonify({"error": "Insufficient balance"}), 400

    return jsonify({"error": "Invalid sender or receiver"}), 400

@app.route('/wallet/<public_key>', methods=['GET'])
def get_wallet(public_key):
    """Retrieve wallet details."""
    wallet = wallets.get(public_key)
    if wallet:
        return jsonify({
            "balance": wallet.balance,
            "transactions": wallet.get_transaction_history()
        })
    return jsonify({"error": "Wallet not found"}), 404

# Login System
@app.route('/login_challenge', methods=['POST'])
def login_challenge():
    """Generate a login challenge for the user."""
    data = request.json
    public_key = data['public_key']

    if public_key not in wallets:
        return jsonify({"error": "Account not found"}), 404

    # Generate a random challenge
    challenge = os.urandom(16).hex()
    login_challenges[public_key] = {"challenge": challenge, "timestamp": time.time()}

    return jsonify({"challenge": challenge})

@app.route('/verify_login', methods=['POST'])
def verify_login():
    """Verify the signed login challenge."""
    data = request.json
    public_key = data.get('public_key')
    signed_challenge = data.get('signed_challenge')

    # Retrieve the challenge for the public key
    challenge_data = login_challenges.get(public_key)
    if not challenge_data:
        return jsonify({"error": "No login challenge found"}), 400

    # Check if the challenge has expired
    if time.time() - challenge_data["timestamp"] > CHALLENGE_EXPIRY:
        del login_challenges[public_key]
        return jsonify({"error": "Challenge expired"}), 400

    challenge = challenge_data["challenge"]

    # Verify the signature using the public key
    try:
        is_valid = verify_signature(public_key, challenge, signed_challenge)
        if is_valid:
            del login_challenges[public_key]  # Remove used challenge
            return jsonify({"message": "Login successful!"})
        else:
            return jsonify({"error": "Invalid signature"}), 403
    except Exception:
        return jsonify({"error": "Verification failed"}), 400

# Perform Actions
@app.route('/perform_action', methods=['POST'])
def perform_action():
    """Handle rewards for user actions or spending for marketplace items."""
    data = request.json
    public_key = data.get('public_key')
    action = data.get('action')

    # Define rewards and costs for actions
    REWARDS = {
        "create_post": 10,  # Tokens earned
        "comment": 5,  # Tokens earned
        "like": 1,  # Tokens earned
        "daily_login": 3  # Tokens earned
    }

    SPENDING = {
        "buy_item": True  # Flag for purchases
    }

    wallet = wallets.get(public_key)
    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404

    # Handle marketplace purchases
    if action in SPENDING:
        cost = data.get('cost')
        item_name = data.get('item_name')

        if not cost or not item_name:
            return jsonify({"error": "Invalid purchase request"}), 400

        # Check if the user has enough balance
        if wallet.balance >= cost:
            wallet.update_balance(-cost)
            return jsonify({
                "message": f"Successfully purchased {item_name} for {cost} tokens.",
                "balance": wallet.balance
            })
        else:
            return jsonify({"error": "Insufficient balance"}), 400

    # Handle reward-based actions
    if action in REWARDS:
        reward = REWARDS[action]
        wallet.update_balance(reward)
        return jsonify({
            "message": f"{reward} tokens rewarded for {action}.",
            "balance": wallet.balance
        })

    # Invalid action type
    return jsonify({"error": "Invalid action type"}), 400

if __name__ == '__main__':
    app.run(debug=True)
