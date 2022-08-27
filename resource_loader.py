import glob
from tabnanny import process_tokens
import pymongo


#connessione a MongoDb
client = pymongo.MongoClient("mongodb://127.0.0.1:27017")
mydb = client["db"]
col_Res = mydb["resources"]

#path messaggi twitter , file emoji e file emoticons 
list = glob.glob("C:/Users/giann/Desktop/UNITO/MAADB_lab/Risorse_lessicali/*/*.txt")
for i in list :
    if i.find("emoji") == -1 & i.find("emoticons") == -1 :
     print(i,"\n")

