import difflib

with open('uniqueUrl.txt', 'r') as myfile:
	urls = myfile.readlines()

for url in urls:
	print difflib.get_close_matches(url,urls,cutoff=0.9)
	break