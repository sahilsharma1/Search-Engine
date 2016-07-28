# -*- coding: utf-8 -*-
from __future__ import division
import requests
from pdfminer import *
from os.path import basename
import requests
import whoosh
from bs4 import BeautifulSoup,UnicodeDammit
from whoosh.index import create_in
from whoosh.fields import *
import time
import re
import os, shutil
import sys
import commands, socket

# lines = 21000

sys.setrecursionlimit(200000)

proxies = {
  'http': 'http://202.141.80.22:3128',
  'https': 'http://202.141.80.22:3128'
}
auth = HTTPProxyAuth("suraj.jha", "jZpn5pcy")

def index_my_docs(pdfDir, clean=False):
  if clean:
    clean_index(pdfDir)
  else:
    incremental_index(pdfDir)

def clean_index(pdfDir):
	
	schema = Schema(title=TEXT(stored=True), path=ID(stored=True, unique=True),time=STORED, content=TEXT)
	ix = create_in("pdfDir", schema)
	writer = ix.writer()
	sys.setrecursionlimit(200000)

	

	urls = open("uniqueUrl.txt",'r')
	i = 0

	for url in urls:
		
		time.sleep(0.01)
		exceptionWords = ["jpg","javascript","zip"]
		testUrl = url.lower()
		if any(word in testUrl for word in exceptionWords):
			continue

		# if "http" not in testUrl:
		# 	continue

		modtime = os.path.getmtime(url)
		http_count = url.count("http")
		if(http_count != 1):
			continue

		folder2 = '/home/sjha/development/web_crawler/search_engine/tutorial/pdfs'
		for the_file in os.listdir(folder2):
		    file_path = os.path.join(folder2, the_file)
		    try:
		        if os.path.isfile(file_path):
		            os.unlink(file_path)
		        elif os.path.isdir(file_path): shutil.rmtree(file_path)
		    except Exception as e:
		        print(e)

		try:
			source = requests.get(url.strip(), verify=False) # --
		except requests.exceptions.ConnectionError as e:
			print "Bad url"
			continue
		except requests.exceptions.Timeout as e:
			print "Timeout happened for this url"
			continue
		except socket.timeout as e:
			print "Socket timeout for this url."
			continue
		except requests.exceptions.ContentDecodingError as e:
			print "ContentDecodingError for this url"
			continue
				
		print source.status_code
		if(source.status_code != 200):
			continue

		if(source.headers['content-type'] == "application/pdf"):

			command = "wget --spider -S " + url + " 2>&1 | grep 'HTTP/' | awk '{print $2}'"
			print commands.getstatusoutput(command)[1]
			if (commands.getstatusoutput(command)[1] != '200'):
				continue

			os.system('wget -P /home/sjha/development/web_crawler/search_engine/tutorial/pdfs %s' % url)

			folder = "/home/sjha/development/web_crawler/search_engine/tutorial/pdfs"

			title_head = ""
			content = ""
			url = url.decode("utf-8", 'ignore')
			for the_file in os.listdir(folder):
				file_path = os.path.join(folder, the_file)
				if os.path.isfile(file_path):
					os.system('pdf2txt.py ' + file_path + ' > /home/sjha/development/web_crawler/search_engine/tutorial/pdfs/test.txt')
				title_head = os.path.splitext(the_file)[0].decode("utf-8" , 'ignore')
				# url = url.decode("utf-8" ,'ignore')
				with open('test.txt', 'r') as myfile:
					plain_text = myfile.read().decode("utf-8" ,'ignore')

		else:

			soup = BeautifulSoup(source.text,'lxml') # --
			if soup is None:
				print "Soup is none"
				continue

			url = url.decode("utf-8", 'ignore')
			plain_text = soup.get_text()        # --
			if soup.title is None:
				print "soup has no title"
				title_head = u"no tilte"
			else:
				title_head = soup.title.string      # --

		writer.add_document(title=title_head, path=url, content=plain_text, _stored_content=plain_text,time=modtime)
		i = i + 1 
		percentage = (i / lines) * 100
		print url + " is done. percentage " + str(percentage) +" %"
	writer.commit()
	urls.close() 

def incremental_index(pdfDir):
	ix = index.open_dir(pdfDir)
	# The set of all paths in the index 
	indexed_paths = set()
	# The set of all paths we need to re-index
	to_index = set()
	with ix.searcher() as searcher:
		writer = ix.writer()

      	
      	# Loop over the stored fields in the index
      	for fields in searcher.all_stored_fields():
        	indexed_path = fields['path']
        	indexed_paths.add(indexed_path)

        if not os.path.exists(indexed_path):
        	# This file was deleted since it was indexed
        	writer.delete_by_term('path', indexed_path)

        else:
          	# Check if this file was changed since it
         	# was indexed
         	indexed_time = fields['time']
         	mtime = os.path.getmtime(indexed_path)
          	if mtime > indexed_time:
          		writer.delete_by_term('path', indexed_path)
            	to_index.add(indexed_path)

    urls = open("uniqueUrltest.txt",'r')
	for url in urls:
		if url in to_index or path not in indexed_paths:
          print "\n\n"
	print url + " is going on"
	time.sleep(0.01)
	exceptionWords = ["jpg","javascript","zip"]
	testUrl = url.lower()
	if any(word in testUrl for word in exceptionWords):
		continue

	if "http" not in testUrl:
		continue


	http_count = url.count("http")
	if(http_count != 1):
		continue

	try:
		source = requests.get(url.strip(), proxies = proxies, auth = auth, verify=True, timeout=1) # --
	except requests.exceptions.ConnectionError as e:
		print "Bad url"
		continue
	except requests.exceptions.Timeout as e:
		print "Timeout happened for this url"
		continue
	except socket.timeout as e:
		print "Socket timeout for this url."
		continue
	except requests.exceptions.ContentDecodingError as e:
		print "ContentDecodingError for this url"
		continue
			
			
	print "status_code = " + str(source.status_code)
	print "encoding = " + str(source.encoding)
	if("content-encoding" in source.headers):
		print "content-encoding = " + str(source.headers["content-encoding"])

	if("content-type" in source.headers):
		print "content-type = " + source.headers["content-type"]

	
	if(source.status_code != 200):
		continue
	
	if(source.headers['content-type'] != "text/html"):
		parse_object = urlparse.urlparse(url)
		title_head = basename(parse_object.path).split(".")[0].decode("utf-8", 'ignore')
		url = url.decode("utf-8", 'ignore')
		plain_text = url.decode("utf-8", 'ignore')

	else:
		soup = BeautifulSoup(source.text,'lxml') # --
		if soup is None:
			print "Soup is none"
			continue

		url = url.decode("utf-8", 'ignore')
		plain_text = soup.get_text()        # --
		if soup.title is None:
			print "soup has no title"
			title_head = plain_text[0:150].decode("utf-8", 'ignore')
		else:
			title_head = soup.title.string      # --

	writer.add_document(title=title_head, path=url, content=plain_text)
	i = i + 1 
	percentage = (i / lines) * 100
	print url + " is done. percentage " + str(percentage) +" %"
	writer.commit()
	urls.close() 

index_my_docs("justTest (another copy)",False)