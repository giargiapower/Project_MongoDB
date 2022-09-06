import psycopg2
import glob





def estrai_sentimento(file):
    file = file.split("\\")
    print(file)
    return file[8].lower()


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

    # path messaggi twitter , file emoji e file emoticons
    list = glob.glob("C:\\Users\\berna\\Desktop\\Laurea magistrale\\MAADB\\pythonProject\\Risorse lessicali\\*\\*.txt")
    for file in list:
        if file.find("emoji") == -1 & file.find("emoticons") == -1:
            with open(file, 'r', encoding='utf-8') as f:
                sentimento = estrai_sentimento(file)
                insert_script = 'SELECT * FROM sentiment WHERE sentiments = %s '
                cur.execute(insert_script, (sentimento,))
                temp = cur.fetchone()
                if temp == None:
                    insert_script = 'INSERT INTO sentiment (sentiments) VALUES (%s)'
                    insert_value = (sentimento)
                    cur.execute(insert_script, (insert_value,) )
                    conn.commit()
                #print(sentimento)
                lines = f.read()
                words = lines.split()
                for w in words:
                    if w.find("_") == -1:
                        insert_script = 'SELECT * FROM lexical_resource WHERE words = %s AND sentiments = %s '
                        cur.execute(insert_script, (w, sentimento,))
                        temp = cur.fetchone()
                        if temp == None:
                            insert_script = 'INSERT INTO lexical_resource (words, sentiments) VALUES (%s, %s)'
                            insert_value = (w, sentimento)
                            cur.execute(insert_script, (insert_value),)
                            conn.commit()
    print("Connection Successful")


except Exception as error:
    print(error)
finally:
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()