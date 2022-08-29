import pymongo
from pymongo import MongoClient

client = pymongo.MongoClient("mongodb://127.0.0.1:27017")
mydb = client["db"]
collection = mydb["twitter"]

# Visualizzare per ogni sentimento una word cloud con le parole maggiormente presenti nei tweet
pipeline = [{"$match" : {"frequency" : {"$gt" : 30}}}]
with collection.aggregate(pipeline) as cursor:
    for operation in cursor:
        print(operation)


client.close()
