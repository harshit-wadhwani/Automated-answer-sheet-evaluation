from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

class dbmanager:
    def __init__(self, myuri=f"mongodb+srv://{os.environ['mongodb_userid']}:{os.environ['mongodb_password']}@examination.nxuahuw.mongodb.net/?retryWrites=true&w=majority&appName=examination" ):
        self.client = MongoClient(myuri)
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
    

db = dbmanager()
d = {'1DT20AIO21': [{'name': 'Sejal Kaur', 'subcode': '18AI81', 'ans1': 'S1201\nThey\nthe structural unit of\nare\ncell body containing\nnudeus,\nbranching extensions (dendrides),\nlong extensions (axon).\nNear extremity it spreads\ninto branches called telodents.\nAt the\nend of these branches\nare\nsynapses.'}, {'name': 'Sejal Kaur', 'subcode': '18AI81', 'ans2': 'p This is the simplest ANN\narchitect. Discovered by\nFrank Rosenblatt\nIt is based on TLU and LTU'}, {'name': 'Sejal Kaur', 'subcode': '18AI81', 'ans3': 'Connected to single layer of TLU\nand each TLU connected to all\ninputs.\nWhen all neurons are connected\nto all in previous then it is\ncalled\nfully\nconnected\nlayer.'}]}

db.create("answers", d)

