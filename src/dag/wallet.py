from cryptography.hazmat.primitives.asymmetric import rsa


class Wallet:
    def __init__(self):
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key()
        self.balance = 0  # Track wallet balance
        self.transaction_history = []  # Store transactions

    def update_balance(self, amount):
        self.balance += amount

    def add_transaction_to_history(self, transaction):
        self.transaction_history.append(transaction)

    def get_transaction_history(self):
        return self.transaction_history
