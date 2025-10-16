# locustfile.py
from locust import HttpUser, task

class SimpleUser(HttpUser):
    
    @task
    def ingresar_usuario(self):
        data = {
            "name": "fabian",
            "email": "fabian@gmail.com",
            "password": "fabian123"
        }
        # Aquí apuntamos al endpoint correcto de Flask
        self.client.post("/", json=data)
