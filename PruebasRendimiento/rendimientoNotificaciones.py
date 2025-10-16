#Generar usuarios virtuales
from locust import HttpUser, task

class SimpleUser(HttpUser):
 
    @task
    def create_notificacion(self):
        data={
                "email": "usuario@ejemplo.com",
                "subject": "Notificación de prueba de transferencia",
                "data": {
                    "title": "Transferencia realizada",
                    "mensaje": "Se ha completado una transferencia entre cuentas exitosamente.",
                    "cuenta_origen": "123456",
                    "cuenta_destino": "654321",
                    "monto": 250000,        
                    "fecha": "2025-10-08 10:30:00"
                }
            }
            
        self.client.post("/",json=data)
