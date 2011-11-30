'''
Created on Nov 29, 2011

@author: boyusun
'''
from query_helper import QueryHelper

    
if __name__ == '__main__':
    db_name = 'astro'
    coll_name = 'first_image'
    
    qhelper = QueryHelper(db_name, coll_name)
    #test nearest query 
    print "test nearest query"
    print qhelper.nearest([15, 384], 'E', 1) 
    print '--------------------------------------------------------'
    range = [14, 200, 16, 800]
    print 'test the range query:'
    print '--------------------------------------------------------'
    print "Original returns without min cover is:"
    for i in qhelper.range_query_without_min_cover(range, 'E'):
        print i
    
    print '--------------------------------------------------------'
    print "min cover for the range query area %s is:" %range
    for i in  qhelper.range_query(range, 'E'):
        print i