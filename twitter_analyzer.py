import glob


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





#connettiti a MongoDb

list = glob.glob("C:/Users/giann/Desktop/UNITO/MAADB_lab/Twitter_messaggi/*.txt")
for file in list : 
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.read()
        clear_l = clear_line(lines)
        list_hashtags = extract_hashtags(clear_l)
        #carica lista hashtags su MongoDB
        #chiedere se anche per hashtags e emoticonos bisogna usare tecnica map.reduce
