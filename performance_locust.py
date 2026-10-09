"""Optional local UI/API load smoke test. Start SecureVault first, then run Locust.
Run: pip install locust && locust -f performance_locust.py --host http://127.0.0.1:5000
Use the Locust web page at http://localhost:8089. Create a demo user before running authenticated requests.
"""
from locust import HttpUser, task, between
class SecureVaultUser(HttpUser):
    wait_time = between(1, 3)
    @task(3)
    def visit_login(self): self.client.get('/login')
    @task(2)
    def visit_register(self): self.client.get('/register')
