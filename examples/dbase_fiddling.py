import psycopg2
import numpy as np
from odm360 import dbase

con = psycopg2.connect('dbname=odm360 user=odm360 host=localhost password=zanzibar')
cur = con.cursor()
if dbase.is_table(cur, 'project_active'):
    dbase.drop_table(cur, 'project_active')
if dbase.is_table(cur, 'devices'):
    dbase.drop_table(cur, 'devices')
if dbase.is_table(cur, 'photos'):
    dbase.drop_table(cur, 'photos')
if dbase.is_table(cur, 'projects'):
    dbase.drop_table(cur, 'projects')

# dbase.create_table_projects(cur)
#
# dbase.insert_project(cur, 'Dar', 7, 5)
# dbase.insert_project(cur, 'Mwanza', 7, 2)
# projects = dbase.query_projects(cur)
# print(projects)
# project = dbase.query_projects(cur, project_id=1)
# print(project)
cur.close()
con.close()
