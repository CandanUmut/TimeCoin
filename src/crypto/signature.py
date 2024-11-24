from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
import base64

class Wallet:
    def __init__(self):
        """Initialize a Wallet with a new RSA key pair."""
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key()
        self.balance = 0  # Initialize wallet balance
        self.transaction_history = []  # Track transaction history

    def update_balance(self, amount):
        """Update the wallet's balance."""
        self.balance += amount

    def add_transaction_to_history(self, transaction):
        """Add a transaction to the wallet's history."""
        self.transaction_history.append(transaction)

    def get_transaction_history(self):
        """Retrieve the transaction history."""
        return self.transaction_history

    def get_public_key(self):
        """Serialize the public key as a Base64 string for JSON compatibility."""
        public_key_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return base64.b64encode(public_key_bytes).decode('utf-8')

    def sign_data(self, data):
        """Sign data with the private key."""
        return base64.b64encode(
            self.private_key.sign(
                data.encode(),
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
        ).decode('utf-8')


# Standalone function for signature verification
def verify_signature(public_key_pem, challenge, signed_challenge_b64):
    """Verify the signed challenge using the public key."""
    try:
        # Load the public key
        public_key = serialization.load_pem_public_key(base64.b64decode(public_key_pem))

        # Decode the signed challenge
        signed_challenge = base64.b64decode(signed_challenge_b64)

        # Verify the signature
        public_key.verify(
            signed_challenge,
            challenge.encode(),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        print(f"Verification error: {e}")
        return False
