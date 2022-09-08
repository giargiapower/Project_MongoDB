import numpy as np
import psycopg2
import glob
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from collections import Counter
import emojis
import string
from os import path

"""estrazione emoji"""
def extract_emojis(sentence):
    return [sentence[i] for i in range(len(sentence)) if str(sentence[i].encode('unicode-escape'))[2] == '\\' ]

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
            opacity = 75 - current_emoji_probability / 0.2 * 5
        return f"hsl({hue_saturation},{opacity}%)"

    def generate(self, text):
        emoji_frequencies = Counter(emojis.iter(text))
        total_count = sum(emoji_frequencies.values())

        self.emoji_probability = {emoji: count / total_count for emoji, count in emoji_frequencies.items()}
        wc = self.word_cloud.generate_from_frequencies(emoji_frequencies)

        plt.figure(figsize=(15, 8))
        plt.imshow(wc)
        plt.axis("off")
        plt.savefig("C:\\Users\\berna\\Desktop\\emoji" + ".png", bbox_inches='tight')
        plt.close()

"""configuazione standard di connessione, user e pwd sono le mie"""

hostname = 'localhost'
database = 'postgres'
username = 'postgres'
pwd = '1234'
port_id = '5432'
conn = None
cur = None

"""connessione al db postgres e creazione delle tabella nel db relazionale"""

try:
    conn = psycopg2.connect(
            host = hostname,
            dbname = database,
            user = username,
            password = pwd,
            port = port_id)

    cur = conn.cursor()

    temp_list = []

    # Visualizzare per ogni sentimento una word cloud con le parole maggiormente presenti nei tweet

    create_script = 'WITH word_sent AS (SELECT word.words AS word, twitter_message.sentiments AS sentiments, SUM (word.frequency) AS frequency FROM word JOIN twitter_message ON word.message = twitter_message.id ' \
                    'GROUP BY twitter_message.sentiments, word.words)' \
                    'SELECT word, sentiments, frequency FROM word_sent ' \
                    'ORDER BY sentiments, frequency DESC '

    cur.execute(create_script)
    temp = cur.fetchall()
    sentimento = np.unique([x[1] for x in temp[:]])
    #print(temp[1][0])
    #print(np.unique([x[1] for x in temp[:]]))
    for i in sentimento:
        temp_list = [x for x in temp[:] if x[1] == i]
        unique_string = ""
        for j in range(50):
            unique_string = unique_string + (temp_list[j][0]) + (" ")
            #print(temp_list[j][0])
        print(unique_string)

        word = WordCloud(width=1000, height=500, background_color='white', max_words=1000,
                              contour_color='#023075',
                              contour_width=3, colormap='rainbow').generate(unique_string)
        plt.figure(figsize=(15, 8))
        plt.imshow(word)
        plt.axis("off")
        plt.savefig("C:\\Users\\berna\\Desktop\\wordcloud_" + i + ".png", bbox_inches='tight')

        plt.close()


    # wordcloud per emoji
    temp_list = []
    create_script = ' SELECT array_agg(name), COUNT(*) FROM emoji GROUP BY name ORDER BY COUNT(*) DESC '

    cur.execute(create_script)
    temp = cur.fetchall()
    #print(temp)
    print(temp[0][0][0])
    #for i  in range(len(temp)):
     #   for j in temp[i]:
      #      print(j[i])
    for j in range(30):
        temp_list.append(str(temp[j][0][0]))

    unique_string = (" ").join(temp_list)
    print(unique_string)

    emoji_cloud = EmojiCloud(font_path='./Symbola.otf')
    emoji_cloud.generate(unique_string)

    # wordcloud per emoticon
    temp_list = []
    create_script = ' SELECT name, COUNT(*) FROM emoticon ' \
                    'GROUP BY name ORDER BY COUNT(*) '
    cur.execute(create_script)
    temp = cur.fetchall()
    #print(temp[2][0][1:-1])
    for j in range(40):
        #print(temp[j][0][:])
        temp_list.append(str(temp[j][0][:]))
    unique_string = (" ").join(temp_list)
    wordcloud = WordCloud(
        regexp='(\:\w+\:|\<[\/\\]?3|[\(\)\\\D|\*\$][\-\^]?[\:\;\=]|[\:\;\=B8][\-\^]?[3DOPp\@\$\*\\\)\(\/\|])(?=\s|[\!\.\?]|$)',
        background_color='white', contour_color='#023075', contour_width=3, colormap='rainbow').generate(unique_string)
    plt.figure(figsize=(15, 8))
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.savefig("C:\\Users\\berna\\Desktop\\emoticons" + ".png", bbox_inches='tight')
    plt.close()

    # istogrammi  prendo tutte le risorse lessicali ordinare per sentimento e contarle. Prendo tutte i sentimenti di twitter e gli raggruppo
    # ciclo ogni sentimento delle risorse lessicali e prendo tutte le parole di quel sentimento tra le risorse lessicali, le metto in una lista
    # ciclo per ogni sentimento di twitter prendo tutte le parole di twitter del sentimento selezionato, le metto in una lista
    # prendo le parole presenti nella lista delle risorse lessicali presenti anche nelle risorse twitter

    create_script_rs = 'SELECT lexical_resource.words, lexical_resource.sentiments ' \
                       'FROM sentiment join lexical_resource on sentiment.sentiments = lexical_resource.sentiments  '
    cur.execute(create_script_rs)
    temp_rs = cur.fetchall()
    #print(temp_rs)

    #fare il conteggio


       
    create_script_tw = 'SELECT word.words, twitter_message.sentiments FROM word join  twitter_message on word.message = twitter_message.id '
    cur.execute(create_script_tw)
    temp_tw = cur.fetchall()
    #print(temp_tw)
    statistics = []

    x_tw = []

    sentimento_rs = np.unique([x[1] for x in temp_rs[:]])
    sentimento_tw = np.unique([x[1] for x in temp_tw[:]])
    #print(sentimento_tw)

    for i in sentimento_rs:
        temp_list_rs = [p for p in temp_rs[:] if p[1] == i]
        counter = len(temp_list_rs)
        for j in sentimento_tw:
            temp_list_tw = [r for r in temp_tw[:] if r[1] == j]
            #print(temp_list_tw)
            #print(temp_list_tw)
            #inter = [j for j in temp_list_rs if j in temp_list_tw]
            inter = list(set(temp_list_rs).intersection(temp_list_tw))
            #print(intesection)
            p_x = len(inter)/counter
            print(p_x)
            statistics.append(p_x)
            x_tw.append(j)
            #inter = []
            #temp_list_tw = []


        print("entrato")
        plt.bar(x_tw, statistics, align='center')  # A bar chart
        plt.ylim([0, 1])
        plt.xlabel('Twitter')
        plt.ylabel('perc_presence_lex_res')
        plt.savefig("C:\\Users\\berna\\Desktop\\statistica" + "_" + i + ".png")
        plt.close()
        x_tw = []
        list_rs = []
        statistics = []
        inter = []
        temp_list_tw = []
        temp_list_rs = []



    # raccolta parole non presenti nelle risorse lessicali
    """for i in list(sentiment_rs):
        word_rs = list(collection.aggregate(#prendo le risorse lessicali
            [{"$match": {"source": "resources", "sentiment": i['_id']}}, {"$project": {"_id": 0, "word": 1}}]))
        for k in word_rs:
            list_rs.append(k["word"])
    for j in sentiment_tw:
        word_tw = list(collection.aggregate(#prendo le risorse di twitter
            [{"$match": {"source": "twitter", "sentiment": j['_id']}}, {"$project": {"_id": 0, "word": 1}}]))
        for k in word_tw:
            list_tw.append(k["word"])
        intersection = [x for x in list_tw if x not in list_rs]
        with open(r'C:/Users/giann/Desktop/new_resources.txt', 'w') as fp:
            fp.write(j['_id'] + ":" + "\n")
            fp.write('\n'.join(intersection))"""

    print("Connection Successful")


except Exception as error:
    print(error)
finally:
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()