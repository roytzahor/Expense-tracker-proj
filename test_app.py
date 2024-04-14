import unittest
from flask import Flask
from app import app
from db import *
from bson.objectid import ObjectId
from datetime import datetime

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_register(self):
        response = self.app.post('/register', data={'username': 'test', 'password': 'test'})
        self.assertEqual(response.status_code, 200)
        users_collection.delete_one({'username': 'test'})

    def test_login(self):
        response = self.app.post('/login', data={'username': 'test', 'password': 'test'})
        self.assertEqual(response.status_code, 200)

    def test_dashboard(self):
        response = self.app.get('/dashboard')
        self.assertEqual(response.status_code, 200)

    def test_get_expenses(self):
        response = self.app.get('/expenses')
        self.assertEqual(response.status_code, 200)

    def test_add_expense(self):
        response = self.app.post('/add_expense', data={'category': 'test', 'amount': '100', 'date': '2022-01-01'})
        self.assertEqual(response.status_code, 200)
        expenses_collection.delete_one({'category': 'test', 'amount': 100, 'date': datetime(2022, 1, 1)})

    def test_get_expense_data(self):
        response = self.app.get('/get_expense_data')
        self.assertEqual(response.status_code, 200)

    def test_expense_data_by_category(self):
        response = self.app.get('/expense_data_by_category')
        self.assertEqual(response.status_code, 200)

    def test_remove_expense(self):
        expense_id = expenses_collection.insert_one({'category': 'test', 'amount': 100, 'date': datetime(2022, 1, 1)}).inserted_id
        response = self.app.post(f'/remove_expense/{expense_id}')
        self.assertEqual(response.status_code, 200)

    def test_remove_account(self):
        user_id = users_collection.insert_one({'username': 'test', 'password': 'test'}).inserted_id
        response = self.app.post(f'/remove_account/{user_id}')
        self.assertEqual(response.status_code, 200)

    def test_get_recommendation(self):
        response = self.app.get('/get_recommendation')
        self.assertEqual(response.status_code, 200)

class TestDB(unittest.TestCase):
    def setUp(self):
        self.username = 'test'
        self.password = 'test'
        self.category = 'test'
        self.amount = 100
        self.date = datetime.now()

    def test_register_user(self):
        result = register_user(self.username, self.password)
        self.assertEqual(result, 'success')
        user = find_user_by_username(self.username)
        if user:
            users_collection.delete_one({'username': self.username})

    def test_find_user_by_username(self):
        users_collection.insert_one({'username': self.username, 'password': self.password})
        user = find_user_by_username(self.username)
        self.assertIsNotNone(user)
        users_collection.delete_one({'username': self.username})

    def test_get_user_id(self):
        user_id = users_collection.insert_one({'username': self.username, 'password': self.password}).inserted_id
        found_user_id = get_user_id(self.username)
        self.assertEqual(str(user_id), str(found_user_id))
        users_collection.delete_one({'_id': user_id})

    def test_add_expense_to_db(self):
        user_id = users_collection.insert_one({'username': self.username, 'password': self.password}).inserted_id
        expense_id = add_expense_to_db(str(user_id), self.category, self.amount, self.date)
        self.assertIsNotNone(expense_id)
        expenses_collection.delete_one({'_id': expense_id})
        users_collection.delete_one({'_id': user_id})

    def test_remove_expense_from_db(self):
        user_id = users_collection.insert_one({'username': self.username, 'password': self.password}).inserted_id
        expense_id = expenses_collection.insert_one({'user_id': str(user_id), 'category': self.category, 'amount': self.amount, 'date': self.date}).inserted_id
        result = remove_expense_from_db(str(expense_id))
        self.assertTrue(result)
        users_collection.delete_one({'_id': user_id})

    def test_get_current_month_expenses(self):
        user_id = users_collection.insert_one({'username': self.username, 'password': self.password}).inserted_id
        expenses_collection.insert_one({'user_id': str(user_id), 'category': self.category, 'amount': self.amount, 'date': self.date})
        expenses = get_current_month_expenses(str(user_id))
        self.assertEqual(len(expenses), 1)
        expenses_collection.delete_one({'user_id': str(user_id)})
        users_collection.delete_one({'_id': user_id})

    def test_get_monthly_expenses_by_category(self):
        user_id = users_collection.insert_one({'username': self.username, 'password': self.password}).inserted_id
        expenses_collection.insert_one({'user_id': str(user_id), 'category': self.category, 'amount': self.amount, 'date': self.date})
        expenses = get_monthly_expenses_by_category(str(user_id), self.date.year, self.date.month)
        self.assertEqual(len(expenses), 1)
        expenses_collection.delete_one({'user_id': str(user_id)})
        users_collection.delete_one({'_id': user_id})

    def test_get_average_expenses_by_category(self):
        user_id = users_collection.insert_one({'username': self.username, 'password': self.password}).inserted_id
        expenses_collection.insert_one({'user_id': str(user_id), 'category': self.category, 'amount': self.amount, 'date': self.date})
        expenses = get_average_expenses_by_category(str(user_id), self.date.year, self.date.month)
        self.assertEqual(len(expenses), 1)
        expenses_collection.delete_one({'user_id': str(user_id)})
        users_collection.delete_one({'_id': user_id})

if __name__ == '__main__':
    unittest.main()
