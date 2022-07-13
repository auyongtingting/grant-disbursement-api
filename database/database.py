import psycopg2

try: 
   conn = psycopg2.connect(
      database="postgres", user='postgres', password='root', host='127.0.0.1', port= '5432'
   )
   conn.autocommit = True
   cursor = conn.cursor()
   sql = '''CREATE database grant_disbursement''';
   cursor.execute(sql)
   print("Database has been created successfully........")
   
except Exception as error:
   print(f"{error}")

conn.close()