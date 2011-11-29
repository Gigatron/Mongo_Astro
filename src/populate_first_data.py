'''
Created on Nov 29, 2011
script for poplulating first image data
@author: boyusun
'''

import sys
import populate_db
import pymongo

db_name = 'astro'
cll_name = 'first_image'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Error: please give a input file(json format)"
        
    from_file = sys.argv[1]
    
    conn = pymongo.Connection()
    db = conn[db_name]
    cll = db[cll_name]
    
    populate_db.drop(db_name, cll_name)
    assert(cll_name not in db.collection_names())
    populate_db.populate(db_name, cll_name, from_file)
    assert(cll.count() > 0)
    cll.create_index([('loc', pymongo.GEO2D)], min=-90000, max = 90000)        #create index
    assert(len(cll.index_information()) > 1)
    