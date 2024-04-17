from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

class dbmanager:
    def __init__(self, myuri=f"mongodb+srv://{os.environ['mongodb_userid']}:{os.environ['mongodb_password']}@examination.nxuahuw.mongodb.net/?retryWrites=true&w=majority&appName=examination" ):
        self.client = MongoClient(myuri, ssl=True)
        self.db = self.client['evaluation']
        
    def create(self, collection_name, data):
        collection = self.db[collection_name]
        result = collection.insert_one(data)
        return result.inserted_id
    
    def read(self, collection_name, query=None):
        collection = self.db[collection_name]
        if query is None:
            cursor = collection.find()
        else:
            cursor = collection.find(query)
        return list(cursor)
    
    def update(self, collection_name, query, update_data):
        collection = self.db[collection_name]
        result = collection.update_many(query, {'$set': update_data})
        return result.modified_count
    
    def delete(self, collection_name, query):
        collection = self.db[collection_name]
        result = collection.delete_many(query)
        return result.deleted_count
    