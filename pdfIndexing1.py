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

class Logger(object):
	def __init__(self):
		self.terminal = sys.stdout
		self.log = open("logfile.log", "w")
	
	def write(self, message):
		self.terminal.write(message)
		self.log.write(message)  

	def flush(self):
		pass
		
sys.stdout = Logger()

def decompress(data):
    with gzip.GzipFile(fileobj=BytesIO(data)) as fh:
        try:
            unzipped = fh.read()
        except struct.error:
            return None
    return unzipped

proxies = {
  'http': 'http://202.141.80.22:3128',
  'https': 'http://202.141.80.22:3128'
}
auth = HTTPProxyAuth("suraj.jha", "jZpn5pcy")

schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
ix = create_in("pdfDir", schema)
writer = ix.writer()
sys.setrecursionlimit(200000)

# folder = '/home/sjha/development/web_crawler/search_engine/tutorial/pdfDir'
# for the_file in os.listdir(folder):
#     file_path = os.path.join(folder, the_file)
#     try:
#         if os.path.isfile(file_path):
#             os.unlink(file_path)
#         elif os.path.isdir(file_path): shutil.rmtree(file_path)
#     except Exception as e:
#         print(e)

magic_dict = {
    "\x1f\x8b\x08": "gzip",
    "\x42\x5a\x68": "bz2",
    "\x50\x4b\x03\x04": "zip"
    }

max_len = max(len(x) for x in magic_dict)

def file_type(filename):
    with open(filename) as f:
        file_start = f.read(max_len)
    for magic, filetype in magic_dict.items():
        if file_start.startswith(magic):
            return filetype
    return "no match"

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

	folder = '/home/sjha/development/web_crawler/search_engine/tutorial/pdfs'
	for the_file in os.listdir(folder):
	    file_path = os.path.join(folder, the_file)
	    try:
	        if os.path.isfile(file_path):
	            os.unlink(file_path)
	        elif os.path.isdir(file_path): shutil.rmtree(file_path)
	    except Exception as e:
	        print(e)

	try:
		source = requests.get(url.strip(), proxies = proxies, auth = auth, verify=True) # --
	except requests.exceptions.ConnectionError as e:
		print "Bad url"
		continue
			
	print "status_code = " + str(source.status_code)
	print "encoding = " + str(source.encoding)
	if("content-encoding" in source.headers):
		print "content-encoding = " + str(source.headers["content-encoding"])

	if("content-type" in source.headers):
		print "content-type = " + source.headers["content-type"]

	
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

	writer.add_document(title=title_head, path=url, content=plain_text)
	i = i + 1 
	percentage = (i / lines) * 100
	print url + " is done. percentage " + str(percentage) +" %"

writer.commit()
urls.close() 