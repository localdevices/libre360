import psycopg2
import numpy as np
from odm360 import dbase

con = psycopg2.connect('dbname=odm360 user=odm360 host=localhost password=zanzibar')
cur = con.cursor()

# DO SOMETHING
# We'll start with a clean slate
if dbase.is_table(cur, 'devices'):
    dbase.drop_table(cur, 'devices')
if dbase.is_table(cur, 'photos'):
    dbase.drop_table(cur, 'photos')
if dbase.is_table(cur, 'projects'):
    dbase.drop_table(cur, 'projects')
# print(is_table(cur, 'photos'))

# setup project and photos table
dbase.create_table_projects(cur)

dbase.create_table_photos(cur)

# now create two projects
dbase.insert_project(cur, 'Dar', 7, 5)
dbase.insert_project(cur, 'Mwanza', 7, 2)
cur.execute("SELECT * FROM projects")
print(f'Two projects should be setup, with a unique ID {cur.fetchall()}')

# first add devices, before creating photos
dbase.create_table_devices(cur)
dbase.insert_device(cur, 'some_camera1', 0)
dbase.insert_device(cur, 'another_camera1', 0)
#
cur.execute("SELECT * FROM devices")
print(f'We have inserted two devices without any status: {cur.fetchall()}')


# try adding a photo from non-existing device, should fail
print(f'Only the names of the projects, looks like: {dbase.query_projects(cur)}')

# now add photos for the given devices
dbase.insert_photo(cur, 1, '2020-09-17', 'some_camera1', '/some/test/to/DCIM12345.JPG',np.random.rand(24, 24), np.random.rand(24, 24))
dbase.insert_photo(cur, 1, '2020-09-17', 'some_camera1', '/some/test/to/DCIM67890.JPG',np.random.rand(24, 24), np.random.rand(24, 24))
dbase.insert_photo(cur, 2, '2020-09-17', 'another_camera1', '/some/test/to/DCIM12345.JPG',np.random.rand(24, 24), np.random.rand(24, 24))
dbase.insert_photo(cur, 2, '2020-09-17', 'another_camera1', '/some/test/to/DCIM12345.JPG',np.random.rand(24, 24), np.random.rand(24, 24))
cur.execute("SELECT * FROM photos")
print(f'For both projects, we have inserted 2 (total 4) photos: {cur.fetchall()}')
last_photo = dbase.query_photos(cur, 1)[0][0]
print(f'The uuid of the last photo is {last_photo}')
dbase.update_device(cur, 'some_camera1', 99, last_photo=last_photo) # last_photo is the uuid gibberish of the last photo id
cur.execute("SELECT * FROM devices")
print(f'After updating status of "some_camera1", status is {cur.fetchall()}')

dbase.delete_project(cur, project_id=1)
# all above photos for project Dar (numbered 1) should now also be removed! Check below
cur.execute("SELECT * FROM photos")
print(f'We have now deleted everything for project_id 1 (name Dar). We now only have these photos: {cur.fetchall()}')

cur.close()
con.close()
