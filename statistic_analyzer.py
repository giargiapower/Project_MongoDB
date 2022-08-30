import pymongo
from pymongo import MongoClient
import matplotlib.pyplot as plt
from wordcloud import WordCloud

client = pymongo.MongoClient("mongodb://127.0.0.1:27017")
mydb = client["db"]
collection = mydb["twitter"]

# Visualizzare per ogni sentimento una word cloud con le parole maggiormente presenti nei tweet
#pipeline = [{"$match" : {"frequency" : {"$gt" : 30}}} , {"$group" : {"_id" : "$sentiment" ,  "data": { "$push": "$$ROOT" }}}]
#with collection.aggregate(pipeline) as cursor:
#    for operation in cursor:
#        print(operation)
pipeline =[{"$match" : {"frequency" : {"$gt" : 30}}} , {"$group" : {"_id" : "$sentiment" ,  "projects": { "$addToSet": {"id" : "$sentiment" , "word" : "$word" , "frequency" : "$frequency" }}}}]
list = list(collection.aggregate(pipeline))

temp_list = []
for j in range(len(list)):
    for i in (list[j]["projects"]) :
        #print(i['word'], " " , i["frequency"])
        temp_list.append(i['word'])
    unique_string=(" ").join(temp_list)
    wordcloud = WordCloud(width = 1000, height = 500).generate(unique_string)
    plt.figure(figsize=(15,8))
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.savefig("C:/Users/giann/Desktop/prova"+".png", bbox_inches='tight')
    plt.close()
    temp_list = []
    break

client.close()
