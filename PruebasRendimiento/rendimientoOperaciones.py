#Generar usuarios virtuales
from locust import HttpUser, task

class SimpleUser(HttpUser):
 
    @task
    def create_transfer(self):
        data={
            "cuenta_origen":30,
            "cuenta_destino":8,
            "monto":1
        }
        self.client.post("/",json=data)
