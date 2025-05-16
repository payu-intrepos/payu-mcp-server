import os

# Create a Singleton class to manage state
class PayUTokenManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PayUTokenManager, cls).__new__(cls)
            # Initialize instance attributes
            cls._instance.access_token = None
            cls._instance.token_type = None
            cls._instance.expires_at = 0
            # Configuration settings
            cls._instance.client_id = os.getenv('CLIENT_ID')
            cls._instance.client_secret = os.getenv('CLIENT_SECRET')
            cls._instance.mid = os.getenv('MERCHANT_ID')
        return cls._instance

