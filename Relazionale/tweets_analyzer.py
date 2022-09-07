import psycopg2
import glob
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
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
        plt.savefig("C:/Users/giann/Desktop/emoji" + ".png", bbox_inches='tight')
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

    create_script = 'WITH word_sent AS (SELECT words.word, sentiments.twitter_message, SUM (word.frequency) FROM word JOIN twitter_message ON word.message = twitter_message.id ' \
                    'GROUP BY sentiments.twitter_message, words.word)' \
                    'SELECT words.word, sentiments.twitter_message FROM word JOIN twitter_message ON word.message = twitter_message.id' \
                    'WHERE words.word IN (SELECT words.word FROM word_sent)' \
                    'ORDER BY words.word, sentiments.twitter_message '

    cur.execute(create_script)
    temp = cur.fetchone()
    #print(temp)
    #mi ritorna le cose ragruppate per sentimento, prendo tutte le parole dei sentimenti e le metto su una stringa
    temp_list = []
    sens = ""
    for j in range(len(create_script)):
        for i in (create_script[j]["items"]):
            sens = i['sentiment']
            temp_list.append(i['word'])
        unique_string = (" ").join(temp_list)
        wordcloud = WordCloud(width=1000, height=500, background_color='white', max_words=1000, contour_color='#023075',
                              contour_width=3, colormap='rainbow').generate(unique_string)
        plt.figure(figsize=(15, 8))
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.savefig("C:/Users/giann/Desktop/wordcloud_" + sens + ".png", bbox_inches='tight')

        plt.close()
        #temp_list = []

    # wordcloud per emoji
    create_script = ' SELECT name, COUNT(*) FROM emoji ' \
                    'GROUP BY name '
    for j in range(30):
        for i in (create_script[j]["_id"]):
            temp_list.append(i)

    unique_string = (" ").join(temp_list)

    emoji_cloud = EmojiCloud(font_path='./Symbola.otf')
    emoji_cloud.generate(unique_string)

    # wordcloud per emoticon
    temp_list = []
    create_script = ' SELECT name, COUNT(*) FROM emoticon ' \
                    'GROUP BY name '
    cur.execute(create_script)
    temp = cur.fetchone()
    #print(temp)
    for j in range(20):
        print(temp)
        print(temp[j]["_id"])
        temp_list.append(temp[j]["_id"])
        print(temp_list)
    unique_string = (" ").join(temp_list)
    print(unique_string)
    wordcloud = WordCloud(
        regexp='(\:\w+\:|\<[\/\\]?3|[\(\)\\\D|\*\$][\-\^]?[\:\;\=]|[\:\;\=B8][\-\^]?[3DOPp\@\$\*\\\)\(\/\|])(?=\s|[\!\.\?]|$)',
        background_color='white', contour_color='#023075', contour_width=3, colormap='rainbow').generate(unique_string)
    plt.figure(figsize=(15, 8))
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.savefig("C:\\Users\\berna\\Desktop\\emoticons" + ".png", bbox_inches='tight')
    plt.close()

    print("Connection Successful")


except Exception as error:
    print(error)
finally:
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()