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
    
    def get_answers_by_code(self, collection_name, code):
        collection = self.db[collection_name]
        query = {"data.code": code}
        projection = {"data": {"$elemMatch": {"code": code}}}
        result = self.read(collection_name, query)
        answers = []
        for doc in result:
            for data_item in doc.get("data", []):
                if data_item["code"] == code:
                    answers.append(data_item["answer"])
        return answers
    
    def get_quenum_ans_dict(self, collection_name, query_key):
        collection = self.db[collection_name]
        query = {query_key: {"$exists": True}}
        result = self.read(collection_name, query)
        questions = []
        answers = []
        lis = result[0][query_key]
        for i in lis:
            questions.append(i["question"])
            answers.append(i["answer"])
        
        return questions, answers
    
# db_client = dbmanager()
# # print(db_client.read("questions", {"data.code" : "testing again"}))
# # print(db_client.get_answers_by_code("questions", "18AI81"))
# res, ans = db_client.get_quenum_ans_dict("questions", "18AI8116-04-2024")
# print(res)  
# print(ans)  

# query = {"_id.18AI8116-04-2024": {"$exists": True}}

# Retrieve the answers
# answers = db_client.read("answers", None)

# print(answers)