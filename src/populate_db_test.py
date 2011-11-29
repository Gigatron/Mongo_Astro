'''
Created on Nov 28, 2011
test for populate/drop db collection data
@author: boyusun
'''
import unittest
import pymongo
import populate_db
from astro_query import QueryHelper

import_file = 'sample_objects_10000.json'
db_name = 'astro'
cll_name = 'first_image'

class TestSampleData(unittest.TestCase):

    def setUp(self):
        self.conn = pymongo.Connection()
        self.db = self.conn.astro
        self.first_image_cll = self.db.first_image
        
    def testDrop(self):
        populate_db.drop(db_name, cll_name)
        self.assertFalse(self.db.last_status()['err'])
        self.assertEqual(self.first_image_cll.count(), 0)
    
    def testPopulate(self):
        populate_db.drop(db_name, cll_name)
        populate_db.populate(db_name, cll_name, import_file)
        self.assertFalse(self.db.last_status()['err'])
        self.assertEqual(self.first_image_cll.count(), 10000)
        
    def test2DQuery(self):
        self.first_image_cll.ensure_index([('loc', pymongo.GEO2D)], min=-90000, max = 90000)     #make sure index does exist
        nearest_image =  self.first_image_cll.find({"loc": {"$near" : {"ra" : 15, "dec" : 384}}}).limit(1)[0]
        self.assertEqual(nearest_image['loc'], {'ra': 15, 'dec': 384})
#        print nearest_image
        range_query = self.first_image_cll.find({"loc": {"$within" : {"$box" : [{"ra": 14, "dec": 307}, {"ra": 16, "dec": 460}]}}})     #need an area bigger than 0
#        print self.first_image_cll.find({"loc": {"$within" : {"$box" : [{"ra": 14, "dec": 307}, {"ra": 16, "dec": 460}]}}}).explain()     #need an area bigger than 0
#        range_query = self.first_image_cll.find({"loc": {"$within" : {"$box" : [[14, 37], [16, 460]]}}})     #here the order is wrong(put ra before dec in list)
#        print range_query.count()
#        print range_query[0]
        locs = [x['loc'] for x in range_query]
        self.assertEqual(locs, [{u'dec': 384, u'ra': 15}, {u'dec': 460, u'ra': 15}, {u'dec': 307, u'ra': 15}])
        
    def testQueryHelper(self):
        qh = QueryHelper(db_name, cll_name)
        qh.ensure_index('loc', -90000, 90000)
        self.assertEqual(qh.nearest([15, 384], 'E', 1) , [u'00015+00384E.jpeg'])
        range = [14, 200, 16, 800]
        print 'test the min cover:'
        print "min cover for the range query area %s is:" %range
        print qh.range_query(range, 'E')
        print "Original returns without min cover is:"
        print qh.range_query_without_min_cover(range, 'E')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    
    
    
    
    
    