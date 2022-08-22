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





#connessione a MongoDb
client = pymongo.MongoClient("mongodb://127.0.0.1:27017")
mydb = client["db"]
col_Hash = mydb["hashtags"]
print("Connection Successful")

list = glob.glob("C:/Users/giann/Desktop/UNITO/MAADB_lab/Twitter_messaggi/*.txt")
for file in list : 
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.read()
        clear_l = clear_line(lines)
        list_hashtags = extract_hashtags(clear_l)
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


        



client.close()