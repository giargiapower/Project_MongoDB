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
                               collocations=False)
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
pipeline =[{"$match" : {"frequency" : {"$gt" : 30}}} , {"$group" : {"_id" : "$sentiment" ,  "projects": { "$addToSet": {"id" : "$sentiment" , "word" : "$word" , "frequency" : "$frequency" }}}}]
lista = list(collection.aggregate(pipeline))
temp_list = []
sens = ""
for j in range(len(list)):
    for i in (lista[j]["projects"]) :
        sens = i['id']
        temp_list.append(i['word'])
    unique_string=(" ").join(temp_list)
    wordcloud = WordCloud(width = 1000, height = 500).generate(unique_string)
    plt.figure(figsize=(15,8))
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.savefig("C:/Users/giann/Desktop/prova"+sens+".png", bbox_inches='tight')
   
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
    print(em[j]["_id"])
    temp_list.append(em[j]["_id"])

unique_string=(" ").join(temp_list)
print(unique_string)
wordcloud = WordCloud(regexp = '(\:\w+\:|\<[\/\\]?3|[\(\)\\\D|\*\$][\-\^]?[\:\;\=]|[\:\;\=B8][\-\^]?[3DOPp\@\$\*\\\)\(\/\|])(?=\s|[\!\.\?]|$)').generate(unique_string)
plt.figure(figsize=(15,8))
plt.imshow(wordcloud)
plt.axis("off")
plt.savefig("C:/Users/giann/Desktop/emoticons"+".png", bbox_inches='tight')
plt.close()



client.close()
