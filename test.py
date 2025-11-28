class APIClient:
    DEFAULT_CONFIG = {
        'timeout': 30,
        'retries': 3,
        'base_url': 'https://api.example.com'
    }
    
    def __init__(self, **kwargs):
        self.config = {**self.DEFAULT_CONFIG, **kwargs}
    
    def make_request(self):
        print(f"Request avec timeout de {self.config['timeout']}s")


client1 = APIClient(timeout=60)  # Spécifique à cette instance
print(client1.timeout)