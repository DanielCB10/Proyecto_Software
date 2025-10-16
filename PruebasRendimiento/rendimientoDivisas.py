# locustfile.py
from locust import HttpUser, task

class SimpleUser(HttpUser):
    
    @task
    def convertir_divisa(self):
        data = {
            "from": "USD",
            "to": "COP",
            "amount": 300
        }
        # Aquí apuntamos al endpoint correcto de Flask
        self.client.post("/convert", json=data)
