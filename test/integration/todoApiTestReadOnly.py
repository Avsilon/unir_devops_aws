import os
import unittest
import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = os.environ.get("BASE_URL")
DEFAULT_TIMEOUT = 5 

@pytest.mark.api
class TestApiReadOnly(unittest.TestCase):

    def setUp(self):
        self.assertIsNotNone(BASE_URL, "URL no configurada")
        self.assertTrue(len(BASE_URL) > 8, "URL no configurada")
        
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def test_api_listtodos(self):
        """GET /todos - Listar todos los TODOs (solo lectura)."""
        print('\n---------------------------------------')
        print('Starting - production integration test List TODO (read-only)')
        url = f"{BASE_URL}/todos"
        
        try:
            response = self.session.get(url, timeout=DEFAULT_TIMEOUT)
            print(f'Response List Todo: {response.status_code}')
            
            self.assertEqual(
                response.status_code, 200,
                f"Error en la petición GET a {url}. Status: {response.status_code}"
            )
            
            todos = response.json()
            self.assertIsInstance(todos, list, "La respuesta debe ser una lista")
            print('End - production integration test List TODO (read-only)')
            
        except requests.exceptions.Timeout:
            self.fail(f"El servidor tardó más de {DEFAULT_TIMEOUT}s en responder (Timeout)")

    def test_api_gettodo_notfound(self):
        """GET /todos/{id} - Verificar que un ID inexistente devuelve 404 (solo lectura)."""
        print('\n---------------------------------------')
        print('Starting - production integration test Get TODO Not Found (read-only)')
        url = f"{BASE_URL}/todos/non-existent-id-12345"
        
        try:
            response = self.session.get(url, timeout=DEFAULT_TIMEOUT)
            print(f'Response Get Todo (not found): {response.status_code}')
            
            self.assertEqual(
                response.status_code, 404,
                f"Error: se esperaba 404 para un TODO inexistente en {url}. Status: {response.status_code}"
            )
            print('End - production integration test Get TODO Not Found (read-only)')
            
        except requests.exceptions.Timeout:
            self.fail(f"El servidor tardó más de {DEFAULT_TIMEOUT}s en responder (Timeout)")