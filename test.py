from DriveFlaskApp import app
from unittest import TestCase
import unittest

class TestIntegrations(TestCase):
    def setUp(self):
        self.tester = app.test_client(self)

    def test_start_page(self):
        response = self.tester.get('/')
        self.assertEqual(response.status_code, 302)

    def test_routes_page(self):
        response = self.tester.get('/routes')
        self.assertEqual(response.status_code, 200)

    def test_buy_tickets(self):
        response = self.tester.get('/buy_tickets/10')
        self.assertEqual(response.status_code, 401)

    def test_unknown_page(self):
        response = self.tester.get('/aaaaa')
        self.assertEqual(response.status_code, 404)

    def test_login_page(self):
        response = self.tester.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()


