import glob
from tabnanny import process_tokens
import pymongo


def estrai_sentimento(file):
    file = file.split("\\")
    return file[1].lower()


#connessione a MongoDb
client = pymongo.MongoClient("mongodb://127.0.0.1:27017")
mydb = client["db"]
col_Res = mydb["resources"]

#path messaggi twitter , file emoji e file emoticons 
list = glob.glob("C:/Users/giann/Desktop/UNITO/MAADB_lab/Risorse_lessicali/*/*.txt")
for file in list :
    if file.find("emoji") == -1 & file.find("emoticons") == -1 :
        with open(file, 'r', encoding='utf-8') as f:
            sentimento = estrai_sentimento(file)
            lines = f.read()
            words = lines.split()
            for w in words:
                #non vengono caricate le parole con _ come richiesto da requisiti
                if w.find("_") == -1 :
                    mydict = { "word": w, "sentiment" : sentimento}
                    col_Res.insert(mydict)
            
