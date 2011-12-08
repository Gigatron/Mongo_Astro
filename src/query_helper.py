'''
Created by Boyu Sun
Provide various query options to the mongoDB. 
A simple wrapper
'''


import json     
import math
import pymongo

#params may need be changed later
#ra_offset = 11
#dec_offset = 232


class Item(object):
    '''the class encapsulate the object with its bounding box'''
    def __init__(self, object, bbox):
        self.object = object
        self.bbox = bbox
        
                
class QueryHelper(object):
    

    def __init__(self, db_name, cll_name):
        self.conn = pymongo.Connection()
        self.db = self.conn[db_name]
        self.cll = self.db[cll_name]
        _config = json.load(open('first_config', 'r'))
        self.ra_offset = _config['ra_offset']/2
        self.dec_offset = _config['dec_offset']/2
         

    
    def ensure_index(self, key, min, max):
        self.cll.ensure_index([(key, pymongo.GEO2D)], min = min, max = max)
                
            
    def nearest(self, location, filter_type, num):
        '''This function returns the nearest images to the give location,
        the location could either be a point or a rectangle, return is a list
        of the desired image pahts
        @param location[0]: ra
        @param location[1]: dec
        '''
        if not (isinstance(location, list) or isinstance(location, tuple)) or not len(location) == 2:
            print "Argument location should be a 2-ary list/tuple!"
            return None
                
        matched_objects = list(self.cll.find({"loc": {"$near" : {"ra" : location[0], "dec" : location[1]}}}).limit(num))
        filter(lambda x: x['filter'] in filter_type, matched_objects)
        #filter the returned objects that isn't same with the 'filter' arg
        return [item['path'] for item in matched_objects]
        
        
    def range_query(self, range, filter_type):
        '''This function returns the approximate minimum number of images that cover the 
        range area provided in the arguments and also satisfies the filter type, return 
        is a list of the file pahts
        @param range: [ra_min, dec_min, ra_max, dec_max]
        '''

        #matched item is different from matched matched object      
        matched_objects = self.__intersect_objects(range, filter_type)  
        matched_items = [Item(object, [object['loc']['ra'] - self.ra_offset, object['loc']['dec'] - self.dec_offset, 
                                       object['loc']['ra'] + self.ra_offset, object['loc']['dec'] + self.dec_offset]) for object in matched_objects]

        min_cover_objects = self.__find_min_cover(range, matched_items)
        return [object['path'] for object in min_cover_objects]
    
    def range_query_without_min_cover(self, range, filter_type):
        '''a range query return all objects with in the given range and matching the filter_type'''
        
        #matched item is different from matched matched object
        matched_objects = self.__intersect_objects(range, filter_type)
        
        return [item['path'] for item in matched_objects]
    
    def __intersect_objects(self, range, filter_type):
        if not (type(range) == list or type(range) == tuple):
            print "Argument range is not correct, type list is required!"
            return None
        if not len(range) == 4:
            print "Incorrect range has been provided in range argument!"
            return None
        
        #here we play a trick, we expand the range to query so that we involve in more objects, meaning that objects
        #whose center point is not in the range can be included, so that there will be not uncovering area on the fringes
        filter_type_list = [c.upper() for c in filter_type]
        matched_objects = list(self.cll.find({'loc' : {'$within': {'$box' : [{'ra': range[0] - self.ra_offset, 'dec': range[1] - self.dec_offset}, 
                                                                             {'ra' : range[2] + self.ra_offset, 'dec': range[3] + self.dec_offset}]}},
                                                                             'filter' : {'$in' : filter_type_list}})) 
        return matched_objects
        
        
    def __find_min_cover(self, area_range, matched_items):
        '''Greedy find the minimum cover of images'''
        min_x = int(math.floor(area_range[0]))
        min_y = int(math.floor(area_range[1]))
        max_x = int(math.ceil(area_range[2]))
        max_y = int(math.ceil(area_range[3]))
#        print min_x, min_y, max_x, max_y
        
        uncovered_area = {}
        return_objects = []
        bbox_set = []
        for x in range(min_x, max_x):
            uncovered_area[x] = [(min_y, max_y - 1)]      #Imagine it as a square which is showed with its left-down-corner coordinates

#        shared_area = self._get_shared_area(uncovered_area, matched_items)
        next_item = self._get_largest_shared_item(uncovered_area, matched_items)
        while not next_item == None:
#            next_item = heapq.heappop(shared_area)[1]
            self._update_uncovered_area(uncovered_area, next_item.bbox)
            return_objects.append(next_item.object)
            bbox_set.append(next_item.bbox)         #for future validation
            matched_items.remove(next_item)
            next_item = self._get_largest_shared_item(uncovered_area, matched_items)
        
        self.__validate(area_range, bbox_set)
        return return_objects
            
            
    def _update_uncovered_area(self, uncovered_area, item_bbox):
        item_minx, item_miny, item_maxx, item_maxy = item_bbox
        min_x = int(max(min(uncovered_area.keys()), item_minx))
        max_x = int(min(max(uncovered_area.keys()), item_maxx - 1))
        
        for i in range(min_x, max_x + 1):
            self._set_uncovered_line(uncovered_area[i], (item_miny, item_maxy- 1))
#        print uncovered_area
                                      
    
    def _set_uncovered_line(self, uncovered_line, covering_line):
        item_miny, item_maxy = covering_line
        new_uncovered_line = []
        to_delete = []
        for min_y, max_y in uncovered_line:
            if min_y > item_maxy or max_y < item_miny:
                continue
            if min_y < item_miny:
                if max_y > item_maxy:
                    new_uncovered_line.append((min_y, item_miny - 1))
                    new_uncovered_line.append((item_maxy + 1, max_y))
                else:
                    new_uncovered_line.append((min_y, item_miny - 1))
            else:
                if max_y > item_maxy:
                    new_uncovered_line.append((item_maxy + 1, max_y))
                else:
                    pass
            to_delete.append((min_y, max_y))
        
        for item in to_delete:
            uncovered_line.remove(item)
        uncovered_line.extend(new_uncovered_line)
        
        
        
        
    def _get_largest_shared_item(self, uncovered_area, matched_items):
#        shared_area = []            #store a heap of items with its shared area
        largest_shared = 0
        largest_shared_item = None
        to_delete = []              #mark items that should be deleted
        for item in matched_items:
            item_minx, item_miny, item_maxx, item_maxy = item.bbox
            min_x = int(max(min(uncovered_area.keys()), item_minx))
            max_x = int(min(max(uncovered_area.keys()), item_maxx - 1))
            
            shared = 0
            for i in range(min_x, max_x + 1):
                shared += self._get_shared_line(uncovered_area[i], (item_miny, item_maxy - 1))
                
            if shared > 0:
                if shared > largest_shared:
                    largest_shared = shared
                    largest_shared_item = item
#                heapq.heappush(shared_area, (-shared, item))
            else:
                to_delete.append(item)
            
        for item in to_delete:
            matched_items.remove(item)
        
        return largest_shared_item
            
                
                
    def _get_shared_line(self, uncovered_line, covering_line):
        item_miny, item_maxy = covering_line
        shared = 0
        for min_y, max_y in uncovered_line:
            if min_y > item_maxy or max_y < item_miny:
                continue
            if min_y < item_miny:
                if max_y > item_maxy:
                    shared += item_maxy - item_miny + 1
                else:
                    shared += max_y - item_miny + 1
            else:
                if max_y > item_maxy:
                    shared += item_maxy - min_y + 1
                else:
                    shared += max_y - min_y + 1
        return shared
    
    def __validate(self, area_range, bbox_set):
        pass
