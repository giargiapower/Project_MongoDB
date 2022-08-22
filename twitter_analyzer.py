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
print(col_Hash)
print("Connection Successful")
for x in col_Hash.find({},{ "hashtag": "school"}):
            print(x)

list = glob.glob("C:/Users/giann/Desktop/UNITO/MAADB_lab/Twitter_messaggi/*.txt")
for file in list : 
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.read()
        clear_l = clear_line(lines)
        list_hashtags = extract_hashtags(clear_l)
        
        #carica lista hashtags su MongoDB
        



client.close()