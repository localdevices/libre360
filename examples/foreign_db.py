import psycopg2
from odm360 import dbase
import os, time
import base64

# Open the database
print("Opening database")
db = "dbname=odm360 user=odm360 host=localhost password=zanzibar"
conn = psycopg2.connect(db)
cur = conn.cursor()
device_uuid1 = "c9f1c734-ac7a-4241-8988-2d1fb30cc0e7.local"
device_uuid2 = "d9f1c734-ac7a-4241-8988-2d1fb30cc0e7.local"

# delete all existing servers
dbase.delete_servers(cur)

# once a device comes online, make a foreign server + table
dbase.create_foreign_table(cur, device_uuid1)
# dbase.create_foreign_table(cur, device_uuid2)

# collate all photos into one view
cur.execute("select foreign_table_name from information_schema.foreign_tables")
tables = cur.fetchall()

fns = []
for n, table in enumerate(tables):
    cur.execute(f"SELECT photo_filename from {table[0]};")
    fns += cur.fetchall()

# cur.execute(sql_command)
# cur.execute("SELECT (photo_filename) from photos;")

# data = cur.fetchall()

# cur.execute(f"SELECT photo from {table[0]} where photo_filename='{fns[0][0]}'")
# photo = cur.fetchone()[0]
#
# print(f'Retrieving and storing photo took {t2 - t1} seconds')


def _generator(table, fn, chunksize=1024):
    print(table, fn)
    cur.execute(f"SELECT photo from {table} where photo_filename='{fn}'")
    photo = cur.fetchall()[0][0]
    for n in range(0, len(photo), chunksize):
        chunk = photo[n : n + chunksize]
        yield chunk


# fetch one blob
t1 = time.time()
data = b""
gen = _generator(table[0], fns[-1][0])
for i in gen:
    data += i
print("yielded entire photo")
t2 = time.time()
print(f"Retrieving and storing photo took {t2-t1} seconds")
# # now remove the server, just by using the device uuid
# dbase.delete_server(cur, device_uuid)
#
# # check if server is indeed gone
# cur.execute("SELECT foreign_server_name FROM information_schema.foreign_servers;")
# server_names = cur.fetchall()
# print(server_names)
