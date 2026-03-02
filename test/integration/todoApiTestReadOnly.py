"""
Tests de integración de SOLO LECTURA para el entorno de producción.
Solo se ejecutan operaciones GET para proteger la integridad de los datos.
"""
import os
import unittest

import pytest
import requests

BASE_URL = os.environ.get("BASE_URL")
DEFAULT_TIMEOUT = 2  # in secs


@pytest.mark.api
class TestApiReadOnly(unittest.TestCase):

    def setUp(self):
        self.assertIsNotNone(BASE_URL, "URL no configurada")
        self.assertTrue(len(BASE_URL) > 8, "URL no configurada")

    def test_api_listtodos(self):
        """GET /todos - Listar todos los TODOs (solo lectura)."""
        print('---------------------------------------')
        print('Starting - production integration test List TODO (read-only)')
        url = BASE_URL + "/todos"
        response = requests.get(url, timeout=DEFAULT_TIMEOUT)
        print('Response List Todo: ' + str(response.status_code))
        self.assertEqual(
            response.status_code, 200,
            f"Error en la petición GET a {url}"
        )
        # Verificar que la respuesta es una lista JSON válida
        todos = response.json()
        self.assertIsInstance(todos, list, "La respuesta debe ser una lista")
        print('End - production integration test List TODO (read-only)')

    def test_api_gettodo_notfound(self):
        """GET /todos/{id} - Verificar que un ID inexistente devuelve 404 (solo lectura)."""
        print('---------------------------------------')
        print('Starting - production integration test Get TODO Not Found (read-only)')
        url = BASE_URL + "/todos/non-existent-id-12345"
        response = requests.get(url, timeout=DEFAULT_TIMEOUT)
        print('Response Get Todo (not found): ' + str(response.status_code))
        # Un ID inexistente debe devolver 404
        self.assertEqual(
            response.status_code, 404,
            f"Error: se esperaba 404 para un TODO inexistente en {url}"
        )
        print('End - production integration test Get TODO Not Found (read-only)')
