"""se non avessi installato questo pacchetto devi lanciare il comando "pip install psycopg2" dal terminale"""

import psycopg2
import config
import glob
import re
import os
import emoji
import nltk
from collections import Counter
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('omw-1.4')



"""estrazione hashtag"""
def extract_hashtags(line):
    hashtag_list = []
    for word in line.split():
        if word[0] == '#':
            hashtag_list.append(word[1:])
    return hashtag_list

"""estrazione emoji"""
def extract_emojis(sentence):
    return [sentence[i] for i in range(len(sentence)) if str(sentence[i].encode('unicode-escape'))[2] == '\\' ]

#rimuove lista di caratteri da testo
def pulizia_testo(testo, chars_to_remove):
    for c in chars_to_remove:
        testo = testo.replace(c , " ")
    return testo


"""pulizia di URL e USERNAME"""
def clear_line(line):
    line = line.replace('USERNAME', '')
    line = line.replace('URL', '')
    return line

"""dato il nome di un file che contiene i tweet mi dice a quale sentimento fanno riferimento questi tweet in modo tale
da poter fare l'analisi delle parole"""
def find_sentimento(name):
    if name.find("anger") != -1:
        return "anger"
    elif name.find("anticipation") != -1:
        return "anticipation"
    elif name.find("disgust") != -1:
        return "disgust"
    elif name.find("fear") != -1:
        return "fear"
    elif name.find("joy") != -1:
        return "joy"
    elif name.find("sadness") != -1:
        return "sadness"
    elif name.find("surprise") != -1:
        return "surprise"
    elif name.find("trust") != -1:
        return "trust"


# crea dizionario di slang words
def crea_dict(text):
    text = text.replace("\n", " ")
    convertedDict = dict(
        (x.replace(" '", ""), y.replace(" '", "")) for x, y in (element.split("':") for element in text.split("',")))
    return convertedDict


# processa la lista di parole modificando gli acronimi e slang words nel loro significato completo
def modify_slang_acr_words(lines, slang):
    for x in slang:
        y = x + ' '
        lines = lines.replace(y, slang[x])
    return lines




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


    create_script_hashtags = ''' CREATE TABLE IF NOT EXISTS hashtags (
                            id  SERIAL PRIMARY KEY,
                            name VARCHAR(225) NOT NULL)'''
    cur.execute(create_script_hashtags)

    create_script_emoticon = ''' CREATE TABLE IF NOT EXISTS emoticon (
                                    id  SERIAL PRIMARY KEY,
                                    name     varchar(40) NOT NULL)'''

    cur.execute(create_script_emoticon)

    create_script_emoji = ''' CREATE TABLE IF NOT EXISTS emoji (
                                        id  SERIAL PRIMARY KEY,
                                        name     varchar(40) NOT NULL)'''

    cur.execute(create_script_emoji)

    create_script_dictionary = ''' CREATE TABLE IF NOT EXISTS dictionary (
                                            id  SERIAL PRIMARY KEY,
                                            word     varchar(225) NOT NULL)'''

    cur.execute(create_script_dictionary)

    # questo counter l'ho messo per vedere a che punto sono con i caricamenti degli hashtags
    counter = 0

    sentimento = ""

    # path messaggi twitter
    list = glob.glob("C:\\Users\\berna\\Desktop\\Laurea magistrale\\MAADB\\pythonProject\\Twitter messaggi\\*.txt")
    lista_emoji = glob.glob("C:\\Users\\berna\\Desktop\\Laurea magistrale\\MAADB\\pythonProject\\emoji\\*.txt")
    lista_emoticons = glob.glob("C:\\Users\\berna\\Desktop\\Laurea magistrale\\MAADB\\pythonProject\\emoticons\\*.txt")

    for file in list:
        sentimento = find_sentimento(file)
        with open(os.path.join(os.getcwd(), file), 'r', encoding='utf-8') as f:

            # HASHTAGS
            lines = f.read()
            clear_l = clear_line(lines)
            list_hashtags = extract_hashtags(clear_l)
            counter += len(list_hashtags)
            print((counter / 217428) * 100, "%")
            #print(list_hashtags)
            for record in list_hashtags:
                insert_script = 'INSERT INTO hashtags (name) VALUES (%s)'
                insert_value = record
                cur.execute(insert_script, (insert_value,))
            # pulizia hashtags trovati da testo
            clear_l = re.sub("#[A-Za-z0-9_]+", "", clear_l)

            # EMOJI
            new_list = extract_emojis(clear_l)
            new_list = [s for s in new_list if s != '\n']
            for file_e in lista_emoji:
                with open(file_e, 'r', encoding='utf-8') as em:
                    l = em.read()
                    l = l.replace("u'\\", "")
                    l = l.replace("'", "")
                    l = l.replace("\n", "")
                    for x in new_list:
                        encoded = x.encode('unicode-escape').decode('ASCII')
                        temp = encoded.replace("\\", "")
                        temp = temp.replace(" ", "")
                        temp = temp.replace("f", "F")
                for record in new_list:
                    if record != -1:
                        insert_script = 'INSERT INTO emoji (name) VALUES (%s)'
                        insert_value = record
                        cur.execute(insert_script, (insert_value,))
            # pulizia emoji da testo
            clear_l = pulizia_testo(clear_l, new_list)

            # EMOTICONS
            for file_emot in lista_emoticons:
                with open(file_emot, 'r', encoding='utf-8') as emot:
                    l = emot.read()
                    l = l.replace('"', '')
                    l = l.replace("'", "")
                    l = l.replace("\n", "")
                    l = l.replace(" ", "")
                    l = l.split(",")
                for record in l:
                    if record != -1:
                        insert_script = 'INSERT INTO emoticon (name) VALUES (%s)'
                        insert_value = record
                        cur.execute(insert_script, (insert_value,))
            # pulizia emoticons da testo
            clear_l = pulizia_testo(clear_l, l)

            # TRATTAMENTO PUNTEGGIATURA E SOSTITUZIONE CON SPAZIO
            chars_to_remove = ['@', '[', ',', '?', '!', '.', ';', ':', '\\', '/', '(', ')', '&', '_', '+', '=', '<', '>', '"', ']', ]
            clear_l = pulizia_testo(clear_l, chars_to_remove)

            # METTERE IL TESTO TUTTO IN LOWERCASE
            clear_l = clear_l.lower()

            # PROCESSAMENTO SLANG WORDS E ACRONIMI
            with open("C:\\Users\\berna\\Desktop\\Laurea magistrale\\MAADB\\pythonProject\\slang_words.txt", 'r', encoding='utf-8') as em:
                slang = em.read()
                slang = crea_dict(slang)
                clear_l = modify_slang_acr_words(clear_l, slang)

            # SENTENCE TOKENIZATION
            tokens = nltk.word_tokenize(clear_l)

            # TAGGING
            tagged = nltk.pos_tag(tokens)

            # LEMMING
            lemmatizer = WordNetLemmatizer()
            tag_list = [(lemmatizer.lemmatize(x[0]), x[1]) for x in tagged]

            # ELIMINAZIONE STOP WORDS
            tokens_without_sw = [word for word in tag_list if not word[0] in stopwords.words('english')]

            # FREQUENCY COUNTING
            list_freq = Counter([word[0] for word in tokens_without_sw])
            #print(list_freq)

            # ADDING TO DICTIONARY
            for w in list_freq:
                insert_script = 'INSERT INTO dictionary (word) VALUES (%s)'
                insert_value = w
                cur.execute(insert_script, (insert_value,))

    conn.commit()
    print("Connection Successful")


except Exception as error:
    print(error)
finally:
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()
