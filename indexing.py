# -*- coding: utf-8 -*-
from __future__ import division
import requests
from pdfminer import *
from os.path import basename
import requests , base64
import whoosh
from bs4 import BeautifulSoup,UnicodeDammit
from whoosh.index import create_in
from whoosh.fields import *
import time
import re
import os, shutil
import sys
import commands
import gzip
from io import BytesIO
from requests.auth import HTTPProxyAuth
import urlparse
from posixpath import basename, dirname
import socket

class Logger(object):
	def __init__(self):
		self.terminal = sys.stdout
		self.log = open("testlogfile.log", "w")
	
	def write(self, message):
		self.terminal.write(message)
		self.log.write(message)  

	def flush(self):
		pass
		
sys.stdout = Logger()

proxies = {
  'http': 'http://202.141.80.22:3128',
  'https': 'http://202.141.80.22:3128'
}
auth = HTTPProxyAuth("suraj.jha", "jZpn5pcy")

schema = Schema(title=TEXT(stored=True), path=ID(stored=True ,unique=True), content=TEXT(stored=True ,chars=True))
ix = create_in("justTest", schema)
writer = ix.writer()
sys.setrecursionlimit(200000)

urls = open("uniqueUrl.txt",'r')
i = 0
lines = 21000

for url in urls:
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