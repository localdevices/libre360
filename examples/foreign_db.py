import psycopg2
from odm360 import dbase
# Open the database
print("Opening database")
db = "dbname=odm360 user=odm360 host=localhost password=zanzibar"
conn = psycopg2.connect(db)
cur = conn.cursor()
device_uuid1 = 'c9f1c734-ac7a-4241-8988-2d1fb30cc0e7.local'
device_uuid2 = 'd9f1c734-ac7a-4241-8988-2d1fb30cc0e7.local'

# delete all existing servers
dbase.delete_servers(cur)

# once a device comes online, make a foreign server + table
dbase.create_foreign_table(cur, device_uuid1)
dbase.create_foreign_table(cur, device_uuid2)

# collate all photos into one view
cur.execute("select foreign_table_name from information_schema.foreign_tables");
tables = cur.fetchall()

sql_command = """CREATE VIEW photos AS ("""
for n, table in enumerate(tables):
    if n > 0:
        sql_command += "UNION\n"
    sql_command += f"""SELECT * FROM {table[0]}
"""
sql_command += """);"""

print(sql_command)


data = []
for n, table in enumerate(tables):
    cur.execute(f"SELECT (photo_filename) from {table[0]};")
    data += cur.fetchall()

# cur.execute(sql_command)
# cur.execute("SELECT (photo_filename) from photos;")

# data = cur.fetchall()
print(data)

# # now remove the server, just by using the device uuid
# dbase.delete_server(cur, device_uuid)
#
# # check if server is indeed gone
# cur.execute("SELECT foreign_server_name FROM information_schema.foreign_servers;")
# server_names = cur.fetchall()
# print(server_names)


print('Done')