from ast import Break
import glob
import pymongo


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





#connessione a MongoDb
client = pymongo.MongoClient("mongodb://127.0.0.1:27017")
mydb = client["db"]
col_Hash = mydb["hashtags"]
print("Connection Successful")

#questo counter l'ho messo per vedere a che punto sono con i caricamenti degli hashtags
counter = 0

sentimento  = ""
list = glob.glob("C:/Users/giann/Desktop/UNITO/MAADB_lab/Twitter_messaggi/*.txt")
for file in list : 
    sentimento = find_sentimento(file)
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.read()
        clear_l = clear_line(lines)
        list_hashtags = extract_hashtags(clear_l)
        counter += len(list_hashtags)
        print((counter/217428)*100 , "%")
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
    


        


client.close()