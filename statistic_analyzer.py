from itertools import count
from tkinter import Y
from typing import List
import pymongo
from pymongo import MongoClient
import matplotlib.pyplot as plt
from wordcloud import WordCloud , STOPWORDS
from collections import Counter
import emojis
import string
from os import path

class EmojiCloud:
    def __init__(self, font_path='Symbola.otf'):
        self.font_path = font_path
        self.word_cloud = self.initialize_wordcloud()
        self.emoji_probability = None

        
    def initialize_wordcloud(self):
        return WordCloud(font_path=self.font_path,
                               width=2000,
                               height=1000,
                               background_color='white',
                               random_state=42,
                               collocations=False,
                               contour_color='#023075',contour_width=3 ,colormap='rainbow')
    def color_func(self, word, font_size, position, orientation, random_state=None,
                   **kwargs):
        hue_saturation = '42, 88%'

        current_emoji_probability = self.emoji_probability[word]
        if current_emoji_probability >= 0.10:
            opacity = 50
        else:
            opacity = 75 - current_emoji_probability/0.2 * 5
        return f"hsl({hue_saturation},{opacity}%)"

    def generate(self, text):
        emoji_frequencies = Counter(emojis.iter(text))
        total_count = sum(emoji_frequencies.values())
        
        self.emoji_probability = {emoji: count/total_count for emoji, count in emoji_frequencies.items()}
        wc = self.word_cloud.generate_from_frequencies(emoji_frequencies)
        
        plt.figure(figsize=(15,8))
        plt.imshow(wc)
        plt.axis("off")
        plt.savefig("C:/Users/giann/Desktop/emoji"+".png", bbox_inches='tight')
        plt.close()





client = pymongo.MongoClient("mongodb://127.0.0.1:27017")
mydb = client["db"]
collection = mydb["twitter"]
emoji = mydb["emoji"]
emoticon = mydb["emoticons"]
# Visualizzare per ogni sentimento una word cloud con le parole maggiormente presenti nei tweet
#pipeline =[{"$match" : {"frequency" : {"$gt" : 30}}} , {"$group" : {"_id" : "$sentiment" ,  "projects": { "$addToSet": {"id" : "$sentiment" , "word" : "$word" , "frequency" : "$frequency" }}}}]
pipeline = [{ "$match": { "frequency": { "$gt": 30 } } }, { "$sort" : { "frequency" : -1 } } ,
  { "$group": { "_id": "$sentiment" , "items" : {"$push" : {"sentiment" : "$sentiment" , "word" : "$word" , "frequency" : "$frequency"}}}} , 
  {"$project":{"items":{"$slice":["$items", 50]}}}]
lista = list(collection.aggregate(pipeline))
temp_list = []
sens = ""
for j in range(len(lista)):
    for i in (lista[j]["items"]) :
        sens = i['sentiment']
        temp_list.append(i['word'])
    unique_string=(" ").join(temp_list)
    wordcloud = WordCloud(width = 1000, height = 500, background_color='white', max_words=1000, contour_color='#023075',contour_width=3,colormap='rainbow').generate(unique_string)
    plt.figure(figsize=(15,8))
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.savefig("C:/Users/giann/Desktop/wordcloud_"+sens+".png", bbox_inches='tight')
   
    plt.close()
    temp_list = []

#wordcloud per emoji
pipeline = [{ "$group": { "_id": "$emoji", "count": { "$sum": 1 }}}, {"$sort":{"count":-1}}]
em = list(emoji.aggregate(pipeline))
for j in range(30):
    for i in (em[j]["_id"]) :
        temp_list.append(i)

unique_string=(" ").join(temp_list)

emoji_cloud = EmojiCloud(font_path='./Symbola.otf')
emoji_cloud.generate(unique_string)

#wordcloud per emoticon
temp_list = []
pipeline = [{ "$group": { "_id": "$emoticons", "count": { "$sum": 1 }}}, {"$sort":{"count":-1}}]
em = list(emoticon.aggregate(pipeline))
for j in range(20):
   # print(em[j]["_id"])
    temp_list.append(em[j]["_id"])

unique_string=(" ").join(temp_list)
#print(unique_string)
#:\) :< :-\) :-\( :\( =\( :\* \^-\^ \[ \.-\. :\[ :3 :c \^\.\^ 8\) =\) :> :] =3 =]
wordcloud = WordCloud(regexp = '(\:\w+\:|\<[\/\\]?3|[\(\)\\\D|\*\$][\-\^]?[\:\;\=]|[\:\;\=B8][\-\^]?[3DOPp\@\$\*\\\)\(\/\|])(?=\s|[\!\.\?]|$)', background_color='white',contour_color='#023075',contour_width=3,colormap='rainbow').generate(unique_string)
plt.figure(figsize=(15,8))
plt.imshow(wordcloud)
plt.axis("off")
plt.savefig("C:/Users/giann/Desktop/emoticons"+".png", bbox_inches='tight')
plt.close()



# istogrammi 
sentiment_rs = collection.aggregate([{"$match" : {"source" : "resources"}} , {"$group" : {"_id":"$sentiment", "count":{"$sum":1}}}])
sentiment_tw = list(collection.aggregate([{"$match" : {"source" : "twitter"}} , {"$group" : {"_id":"$sentiment" }}]))
list_rs = []
list_tw = []
statistics = [] 
for i in list(sentiment_rs):
    n_tot = i["count"]
   # print(n_tot)
    word_rs = list(collection.aggregate([{"$match" : {"source" : "resources", "sentiment" : i['_id']}}, {"$project" : {"_id" : 0 ,"word": 1}}]))
    for k in word_rs : 
        list_rs.append(k["word"])
    for j in sentiment_tw:
       # print(j)
        word_tw = list(collection.aggregate([{"$match" : {"source" : "twitter", "sentiment" : j['_id']}}, {"$project" : {"_id" : 0 ,"word": 1}}]))
        for k in word_tw : 
            list_tw.append(k["word"])
        intersection = [x for x in list_rs if x in list_tw]
        #print(intersection)
        n_intersection = len(intersection)
        statistics.append([j['_id'], n_intersection/n_tot])
        list_tw = []

    x = [row[0] for row in statistics]
    y = [row[1] for row in statistics]
    plt.bar(x,y, align='center') # A bar chart
    plt.ylim([0, 1])
    plt.xlabel('Twitter')
    plt.ylabel('perc_presence_lex_res')
    plt.savefig("C:/Users/giann/Desktop/statistica"+ "_"+i['_id'] + ".png")
    plt.close()
    list_rs= []
    statistics = []
    

#raccolta parole non presenti nelle risorse lessicali
for i in list(sentiment_rs):
    word_rs = list(collection.aggregate([{"$match" : {"source" : "resources", "sentiment" : i['_id']}}, {"$project" : {"_id" : 0 ,"word": 1}}]))
    for k in word_rs : 
        list_rs.append(k["word"])
for j in sentiment_tw:
    word_tw = list(collection.aggregate([{"$match" : {"source" : "twitter", "sentiment" : j['_id']}}, {"$project" : {"_id" : 0 ,"word": 1}}]))
    for k in word_tw : 
        list_tw.append(k["word"])
    intersection = [x for x in list_tw if x not in list_rs]
    with open(r'C:/Users/giann/Desktop/new_resources.txt', 'w') as fp:
        fp.write(j['_id'] + ":" + "\n")
        fp.write('\n'.join(intersection))





client.close()
