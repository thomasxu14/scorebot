# -*- coding: utf-8 -*-
"""
Created on Sun Jun 10 23:11:58 2018

@author: Maths
"""

## WARNING
## This program will delete all the db.json database
## creates a back up first

from tinydb import TinyDB, Query
from tinydb.operations import *
from shutil import copyfile
copyfile("db.json", "dbbackup.json")

db = TinyDB('db.json')
users = db.table("users")
comments = db.table("comments")
results = db.table("results")
comments.purge()
users.purge()
results.purge()
