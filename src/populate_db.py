'''
Created on Nov 28, 2011
toolbox for populating/dropping a given db and colelctions
@author: boyusun
'''
import pymongo
import json
import argparse
import sys

my_db_name = 'astro'

def getDatabase(db_name):
    return pymongo.Connection()[db_name]

def populate(db_name, collection_name, from_file):
    images = json.load(open(from_file))
    
    db = getDatabase(db_name)
    collection = db[collection_name]
    collection.insert(images)
    

def drop(db_name, collection_name):
    db = getDatabase(db_name)
    db.drop_collection(collection_name)
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="used to populate the database with data, for this version only json file is permitted", prog='populate_db')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('-p', '--populate', help = 'populate db with the data stored in json format file')
    parser.add_argument('-d', '--drop', action = 'store_true', help = 'drop the given collection')
    parser.add_argument('db_name', help = 'name of the db where the operation is done')
    parser.add_argument('collection_name', help = 'name of the collection to populate/drop')
    
    
    ret = parser.parse_args(sys.argv[1:])
    if ret.drop == True:
        drop(ret.db_name, ret.collection_name)
    elif ret.populate != None:
        populate(ret.db_name, ret.collection_name, ret.populate)
    else:
        print "Error: please specify your operation(populate/drop)"