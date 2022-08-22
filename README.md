# progetto MAADB

note informative : 

- ogni volta che si runna il codice .py lui vede se è presente il database "db" e il documento "hashtags" e se ci sono salva tutti gli hashtags facendo anche il conto delle occorrenze uguali. se si vuole runnare più volte il codice bisogna eliminare il documento o i risultati delle occorrenze saranno sballati. usare il comando :
  
  - col_Hash.delete_many({}) per eliminare tutto il documento
