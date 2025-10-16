#Generar usuarios virtuales
from locust import HttpUser, task

class SimpleUser(HttpUser):
 
    @task
    def create_reporte_pdf(self):
        self.client.get("/report/pdf")

    @task
    def create_reporte_excel(self):
        self.client.get("/report/excel")
