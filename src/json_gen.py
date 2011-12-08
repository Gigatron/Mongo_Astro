#!/usr/bin/python

import os
import sys
import json
import re	
import argparse


m = re.compile('\d{5}(\+|\-)\d{5}\w\.')

def extractObjectFromPath(files, objects_set):
	'''check if file in the file list match the pattern given
	if true, then add new object to the object sets'''
	for f in files:		
		if m.search(f):
			print "file %s matched, creating new object..." %f
			f_name = m.search(f).group(0)
			_ra, _dec = re.findall('[+-]?\d+', f_name)
			_filter = re.search('[A-Z]', f_name).group()
			objects_set.append({'loc': {'ra':int(_ra), 'dec' : int(_dec)}, 'filter' : _filter, 'path': f})



def recordObjectFromPath(folder_path, data_file_path):
	'''providing a folder path, this function recursively walk into
	folders and extract names that can match the pattern'''
	if not os.path.exists(folder_path):
		print "please input a valid folder name..."
		return
	
	print "Scanning folder %s and extracting information..." %(folder_path)

	cur_dir = folder_path
	objects_set = []
	for path, dirs, files in os.walk(cur_dir):
		print "Entering folder %s" %path
		extractObjectFromPath(files, objects_set)
		
	saveDataFile(objects_set, data_file_path)
	

	
def recordObjectFromFile(name_file_path, data_file_path):
	'''Providing a data file, this function scans all the name and convert
	valid names into objects'''
	try:
		f = open(name_file_path, 'r')
	except IOError:
		print 'file %s not exist!' % name_file_path
	else:
		objects_set = []
		for line in f:
			line = line.rstrip()
			if m.search(line):
				print "file %s matched, creating new object..." %line
				object_name = m.search(line).group(0)
				_ra, _dec = re.findall('[+-]?\d+', object_name)
				_filter = re.search('[A-Z]', object_name).group()
				objects_set.append({'loc': {'ra':int(_ra), 'dec' : int(_dec)}, 'filter' : _filter, 'path': line})
			
		saveDataFile(objects_set, data_file_path)
		
	

def saveDataFile(objects_set, data_file_path):
	print "Starting writing objects into file %s, this may take a while..."	%data_file_path
	recorded_file = open(data_file_path, 'w')
	recorded_file.write(json.dumps(objects_set,sort_keys=True, indent=4))
	recorded_file.close()
	print "Writing finished!"
	
	
if __name__ == '__main__':
#	if len(sys.argv) < 3:
#		print "Usage: python coord_extract folder_name file_to_store"
#		sys.exit()	
#		
	parser = argparse.ArgumentParser(description = 'generate data file by providing either file path or file of name list.')
	parser.add_argument('-p', '--path', help='Locating the files by providing a root folder path')
	parser.add_argument('-f', '--file', help = 'importing the objects information from a file')
	parser.add_argument('destination_file', help = 'the path where the output file is stored')
	
	ret = parser.parse_args(sys.argv[1:])
	
	if ret.path != None:
		recordObjectFromPath(ret.path, ret.destination_file)
	elif ret.file != None:
		recordObjectFromFile(ret.file, ret.destination_file)
	else:
		print 'Error: please explicitly set the desired option'
	
	

	

