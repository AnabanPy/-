import requests
from typing import Dict, List


class APIClient:
    BASE_URL = "http://178.57.217.79:8080/api/v1"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def get_health(self) -> Dict:
        response = self.session.get(f"{self.BASE_URL}/core/health")
        response.raise_for_status()
        return response.json()

    def get_organizations(self) -> List[Dict]:
        response = self.session.get(f"{self.BASE_URL}/core/organizations")
        response.raise_for_status()
        return response.json()

    def get_waste_types(self) -> List[Dict]:
        response = self.session.get(f"{self.BASE_URL}/core/waste-types")
        response.raise_for_status()
        return response.json()

    def get_batches(self) -> List[Dict]:
        response = self.session.get(f"{self.BASE_URL}/accounting/batches")
        response.raise_for_status()
        return response.json()

    def get_batch_by_code(self, code: str) -> Dict:
        """Проверка существования партии по коду"""
        batches = self.get_batches()
        for batch in batches:
            if batch.get('code') == code:
                return batch
        return None

    def create_batch(self, data: Dict) -> Dict:
        response = self.session.post(f"{self.BASE_URL}/accounting/batches", json=data)
        response.raise_for_status()
        return response.json()

    def classify_batch(self, batch_id: int, data: Dict) -> Dict:
        response = self.session.patch(f"{self.BASE_URL}/accounting/batches/{batch_id}/classify", json=data)
        response.raise_for_status()
        return response.json()

    def get_dashboard(self) -> Dict:
        response = self.session.get(f"{self.BASE_URL}/reporting/dashboard")
        response.raise_for_status()
        return response.json()

    def get_summary_by_hazard(self) -> List[Dict]:
        response = self.session.get(f"{self.BASE_URL}/reporting/summary/by-hazard")
        response.raise_for_status()
        return response.json()