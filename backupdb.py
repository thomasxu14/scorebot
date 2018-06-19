# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 23:07:03 2018

@author: Maths
"""

## Creates back up of the database db.json

from shutil import copyfile
copyfile("db.json", "dbbackup.json")