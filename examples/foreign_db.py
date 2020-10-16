import psycopg2
from odm360 import dbase
# Open the database
print("Opening database")
db = "dbname=odm360 user=odm360 host=localhost password=zanzibar"
conn = psycopg2.connect(db)
cur = conn.cursor()
cur.execute("DROP SERVER IF EXISTS child_1 CASCADE")
cur.connection.commit()

dbase.create_foreign_table(cur, 'c9f1c734-ac7a-4241-8988-2d1fb30cc0e7.local', 1)

cur.execute("select foreign_table_name from information_schema.foreign_tables");
tables = cur.fetchall()

sql_command = """CREATE VIEW photos AS """
for n, table in enumerate(tables):
    if n > 0:
        sql_command += "UNION\n"
    sql_command += f"""SELECT * FROM {table[0]}
"""

print(sql_command)

cur.execute(sql_command)


cur.execute("SELECT (photo_filename) from photos;")

data = cur.fetchall()
print(data)