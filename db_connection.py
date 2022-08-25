"""se non avessi installato questo pacchetto devi lanciare il comando "pip install psycopg2" dal terminale"""

import psycopg2
import config
import glob
import re
import os


"""estrazione hashtag"""
def extract_hashtags(line):
    hashtag_list = []
    for word in line.split():
        if word[0] == '#':
            hashtag_list.append(word[1:])
    return hashtag_list


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
                            id       int PRIMARY KEY,
                            name     varchar(40) NOT NULL)'''
    cur.execute(create_script_hashtags)

    create_script_emoticon = ''' CREATE TABLE IF NOT EXISTS emoticon (
                                    id       int PRIMARY KEY,
                                    name     varchar(40) NOT NULL)'''

    cur.execute(create_script_emoticon)

    create_script_emoji = ''' CREATE TABLE IF NOT EXISTS emoji (
                                        id       int PRIMARY KEY,
                                        name     varchar(40) NOT NULL)'''

    cur.execute(create_script_emoji)

    insert_script = 'INSERT INTO hashtags (id, name) VALUES (%s, %s)'
    insert_value = (1, 'sosweet')
    cur.execute(insert_script, insert_value)

    conn.commit()
    print("Connection Successful")


except Exception as error:
    print(error)
finally:
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()


#questo counter l'ho messo per vedere a che punto sono con i caricamenti degli hashtags
counter = 0

sentimento  = ""


#path messaggi twitter
list = glob.glob("C:\\Users\\berna\\Desktop\\Laurea magistrale\\MAADB\\pythonProject\\Twitter messaggi\\*.txt")


for file in list :
    sentimento = find_sentimento(file)
    print("sono qui")
    with open(os.path.join(os.getcwd(), file), 'r', encoding='utf-8') as f:
        lines = f.read()
        clear_l = clear_line(lines)
        list_hashtags = extract_hashtags(clear_l)
        counter += len(list_hashtags)
        print((counter/217428)*100 , "%")
        #pulizia hashtags trovati da testo
        clear_l = re.sub("#[A-Za-z0-9_]+","", clear_l)
        """print(list_hashtags)"""