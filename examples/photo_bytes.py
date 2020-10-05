import picamera
import io
import time
import psycopg2
from odm360 import dbase

# This script tests how fast full resolution photos can be captured and stored 
# by taking ten consecutive photos and monitoring the time it takes to store them.
# First results indicate a 1.2 to 1.3 seconds per photo, suggesting we cannot handle
# faster capturing than once every 3 seconds.

# Open the database
print('Opening database')
db = 'dbname=odm360 user=odm360 host=localhost password=zanzibar'
conn = psycopg2.connect(db)
cur = conn.cursor()

# make some fake project information
project_id = 1
survey_run = 'something'
device_name = '192.168.178.9'


# start up the camera, set resolution and do preview
print('Starting picam')
camera = picamera.PiCamera()
camera.resolution = (4056, 3040)
camera.start_preview()
# Camera warm-up time
time.sleep(2)

# now take 10 photos, each time storing one in the database
for n in range(10):
    tic = time.time()
    print('Preparing bytesio object')
    with io.BytesIO() as my_stream:
        print('Capturing photo....')
        camera.capture(my_stream, 'jpeg')
        print('Photo captured...rewinding byte stream...')
        my_stream.seek(0)
        fn = f'yeeee_{n}.jpg'
        print('Inserting into database...')
        #data = my_stream.read()
        dbase.insert_photo(cur, project_id, survey_run, device_name, fn, my_stream.read(), thumb=None)
    toc = time.time()
    print(f'Photo taking and storing {fn} took {toc-tic} seconds')
    print('Flushing bytesio')
    # my_stream.close()
# now insert it into our database
#sql_command = f"""
#        INSERT INTO photos_child
#        (
#        project_id
#        ,survey_run
#        ,device_name
#        ,photo_filename
#        ,photo
#        ) VALUES
#        (
#        '{project_id}'
#        ,'{survey_run}'
#        ,'{device_name}'
#        ,'{fn}'
#        ,{photo}
#        );"""
#
#cur.execute(sql_command)
#cur.connection.commit()


