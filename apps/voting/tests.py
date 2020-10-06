from django.test import Client, TestCase
from snapshottest.django import TestCase as SnapshotTestCase

client = Client()

# user cannot push more votes through race condition
# cannot vote for deleted restaurants
# permissions: have to be logged in to create edit delete restaurants and vote
# cannot delete restaurant someone else created


# TODO https://docs.djangoproject.com/en/3.1/topics/testing/tools/#django.test.TransactionTestCase.fixtures
class ApiTests(TestCase, SnapshotTestCase):
    def test_restaurants(self):
        response = client.post('/voting/restaurants', {"restaurantName": "At the end of the universe"})
        response = client.post('/voting/restaurants', {"restaurantName": "Lido"})
        response = client.post('/voting/restaurants', {"restaurantName": "Spitaki"})
        self.assertMatchSnapshot(response.content, '1 create restaurant')

        response = client.put('/voting/restaurants/3', {"newName": "Lido Dzirnavas"}, content_type="application/json")
        self.assertMatchSnapshot(response.content, '2 update restaurant')

        response = client.delete('/voting/restaurants/4')
        self.assertMatchSnapshot(response.content, '3.1 delete restaurant')
        response = client.delete('/voting/restaurants/4')
        self.assertMatchSnapshot(response, '3.2 fail to delete twice')

        response = client.get('/voting/restaurants')
        self.assertMatchSnapshot(response.content, '4.1 get all restaurants')
        response = client.get('/voting/restaurants/2')
        self.assertMatchSnapshot(response.content, '4.2 get restaurant by id')


class ModelTests(TestCase):
    def test_finalizeRestaurantChoice(self):
        pass
