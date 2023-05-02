from pymongo import MongoClient

client = MongoClient('localhost', 27017, username='', password='')
db = client.mtbs