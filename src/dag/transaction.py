import time


class Transaction:
    def __init__(self, sender, receiver, action_type, content=None, parent_ids=None):
        """
        A transaction can represent:
        - Transfer (e.g., cryptocurrency)
        - Action (e.g., comment, like)
        """
        self.sender = sender
        self.receiver = receiver
        self.action_type = action_type  # e.g., 'transfer', 'comment', 'like'
        self.content = content  # For actions like comments
        self.parent_ids = parent_ids or []
        self.timestamp = time.time()
        self.hash = None  # Will be calculated later
