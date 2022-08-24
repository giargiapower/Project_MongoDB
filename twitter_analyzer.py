from ast import Break
import glob
import pymongo
import emojis
import pyemoji
import re

def extract_emojis(sentence):     
    return [sentence[i] for i in range(len(sentence)) if str(sentence[i].encode('unicode-escape'))[2] == '\\' ]

#estrazione hashtag
def extract_hashtags(line):
    hashtag_list = []
    for word in line.split():
        if word[0] == '#':
            hashtag_list.append(word[1:])
    return hashtag_list


#pulizia di URL e USERNAME 
def clear_line(line):
    line = line.replace('USERNAME', '')
    line = line.replace('URL', '')
    return line


#dato il nome di un file che contiene i tweet mi dice a quale sentimento fanno riferimento questi tweet in modo tale
# da poter fare l'analisi delle parole 
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

#rimuove lista di caratteri da testo 
def pulizia_testo(testo, chars_to_remove):
    for c in chars_to_remove:
        testo = testo.replace(c , " ")
    return testo





#connessione a MongoDb
client = pymongo.MongoClient("mongodb://127.0.0.1:27017")
mydb = client["db"]
col_Hash = mydb["hashtags"]
col_emoji = mydb["emoji"]
col_emoticons = mydb["emoticons"]
print("Connection Successful")

#questo counter l'ho messo per vedere a che punto sono con i caricamenti degli hashtags
counter = 0

sentimento  = ""

#path messaggi twitter , file emoji e file emoticons 
list = glob.glob("C:/Users/giann/Desktop/UNITO/MAADB_lab/Twitter_messaggi/*.txt")
lista_emoji = glob.glob("C:/Users/giann/Desktop/UNITO/MAADB_lab/Risorse_lessicali/emoji/*.txt")
lista_emoticons = glob.glob("C:/Users/giann/Desktop/UNITO/MAADB_lab/Risorse_lessicali/emoticons/*.txt")

for file in list : 
    sentimento = find_sentimento(file)
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.read()
        clear_l = clear_line(lines)
        list_hashtags = extract_hashtags(clear_l)
        counter += len(list_hashtags)
        print((counter/217428)*100 , "%")
        #pulizia hashtags trovati da testo
        clear_l = re.sub("#[A-Za-z0-9_]+","", clear_l)
        print(clear_l)  
        #carica lista hashtags su MongoDB
        for h in list_hashtags:
             x = col_Hash.find_one({ "hashtag": h})
             if x == None : 
                mydict = { "hashtag": h, "counter": 1}
                col_Hash.insert_one(mydict)
             else :
                myquery = { "hashtag": h}
                newvalues = { "$set": { "counter": x["counter"]+1 } }
                col_Hash.update_one(myquery, newvalues)


        #elaborazione emojy e emoticons (credo vadano elaborate con map/reduce quindi credo che ciascuna emoji vada 
        # salvata indipendentemente dalle altre, anche se si ripetono e poi quando vanno mostrate le word clouds si applica 
        # il map reduce quindi per ogni sentimento estraggo tutte le emoji (map) e faccio il conto delle occorrenze di
        # ciascuna emoji (reduce))
        #EMOJI
        #new_list = emojis.get(clear_l)
        new_list = extract_emojis(clear_l)
        new_list = [s for s in new_list if s != '\n']
        print(new_list)
        for file_e in lista_emoji : 
           with open(file_e, 'r', encoding='utf-8') as em:
                l = em.read()
                l = l.replace("u'\\" , "")
                l = l.replace("'", "")
                l = l.replace("\n", "")  
                for x in new_list:
                    encoded = x.encode('unicode-escape').decode('ASCII')
                    temp = encoded.replace("\\", "")
                    temp = temp.replace(" ", "")
                    temp = temp.replace("f", "F")
                    #print(temp,'\n')
                    if l.find(temp) != -1:
                        #salva elemento nel db
                       print("entrato")
                       mydict = { "emoji": x, "sentiment": sentimento}
                       col_emoji.insert_one(mydict)
        #pulizia emoji da testo
        clear_l = pulizia_testo(clear_l, new_list)
        #EMOTICONS
        for file_emot in lista_emoticons : 
            with open(file_emot, 'r', encoding='utf-8') as emot:
                l = emot.read()
                l = l.replace('"' , '')
                l = l.replace("'", "")
                l = l.replace("\n", "") 
                l = l.replace(" ", "")  
                l = l.split(",")
                for x in l:
                    if clear_l.find(x) != -1:
                        #salva elemento nel db
                        mydict = { "emoticons": x, "sentiment": sentimento}
                        col_emoticons.insert_one(mydict)   
                #pulizia emoticons da testo
                clear_l = pulizia_testo(clear_l, l)  
                  
        #TRATTAMENTO PUNTEGGIATURA E SOSTITUZIONE CON SPAZIO
        chars_to_remove = ['@', '[',',','?','!','.',';',':','\\','/','(',')','&','_','+','=','<','>','"',']',]
        clear_l = pulizia_testo(clear_l, chars_to_remove)
    print(clear_l)
    break

        


client.close()