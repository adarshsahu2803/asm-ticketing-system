import requests
from typing import Dict, Any

class APIClient:
    def __init__(self):
        self.base_url = "http://localhost:8000"
    
    def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(f"{self.base_url}/tickets/", json=ticket_data)
        return response.json()
    
    def list_tickets(self) -> list:
        response = requests.get(f"{self.base_url}/tickets/")
        return response.json()
    
    def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/tickets/{ticket_id}")
        return response.json()