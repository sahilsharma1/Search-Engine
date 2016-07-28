from whoosh.qparser import QueryParser
import whoosh
from whoosh.fields import *
import whoosh.index as index
from whoosh.highlight import highlight
import urlparse
from posixpath import basename, dirname

ix = index.open_dir("justTest")


# with ix.searcher() as searcher:
# 	query = QueryParser("content", ix.schema).parse("iit")
# 	results = searcher.search(query)
# 	print results[0]["title"] 

def Search(term):
	resultText = ""
	with ix.searcher() as searcher:
		query = QueryParser("content", ix.schema).parse(term)
		corrector = searcher.corrector("content")
		# for mistyped_word in mistyped_words:
		Suggestions = corrector.suggest(term, limit=3)
		if(Suggestions):
			resultText += "<li><h2 class='suggestion_header'>Suggestions based on content</h2></li>"
			for Suggestion in Suggestions:
				resultText += "<li><h3><a href='#' class='suggestions'> " + Suggestion + "</a></h3></li>"
		resultText += "<li>"
		corrected = searcher.correct_query(query, term)
		if corrected.query != query:
			resultText += "<li><h3 class='did_you_mean'>Did You Mean: </h3><p><a class='suggestions'>" + corrected.string + "</a></p>"

		results = searcher.search(query, terms=True,limit=None)
		
		# results.fragmenter = highlight.PinpointFragmenter(autotrim=True)
		# results.formatter = highlight.UppercaseFormatter(between = "...")
		terms=term.split(" ")
		# resultText += " estimated_min_length " + str(results.estimated_min_length()) 
		if results.estimated_min_length() < 11:
			urls = open("uniqueUrltest.txt",'r')
			i = 0
			for url in urls:
				if i < 6:
					if any(word in url for word in terms):
						parse_object = urlparse.urlparse(url)
						if "." not in url and "/" == url[-1]:
							url = url[0:-2]
							title_head = basename(url).decode("utf-8", 'ignore')
						else:
							title_head = basename(parse_object.path).split(".")[0].decode("utf-8", 'ignore')
						
						resultText += "<h3><a href='"+url+"'>" + title_head + "</a></h3><p class='green'>" + url+ "</p>"
						i += 1
			urls.close()
		for result in results:
			# i=0
			# if ".pdf" in str(result["path"]) and i<3:
			# 	resultText += "<h1>" + "<a href='" + result["path"] + "'>" + result["path"] + "</a><br/></h1>" + result["path"] + "<br/><br/>" + result.highlights("content") + "<br/>"
			# 	i += 1
			# 	del results[result]
			if "title" in result:
				if "error" in result["title"].lower():
					resultText += "<h3>" + "<a href='" + result["path"] + "'>" + result["path"] + "</a></h3><p class='url'>" + result["path"] + "</p><p>" + result.highlights("content") + "</p>"
				else:
					if(result["title"] == "" ) or result["title"].isspace():
						resultText += "<h3 class='title_head'>" + "<a href='" + result["path"] + "'>" + "No Title Present" + "</a></h3><p class='url'>" + result["path"] + "</p><p>"  + result.highlights("content") + "</p>"
					else:
						resultText += "<h3 class='title_head'>" + "<a href='" + result["path"] + "'>" + result["title"] + "</a></h3><p class='url'>" + result["path"] + "</p><p>"  + result.highlights("content") + "</p>"
	if(resultText == "<li>"):
		resultText = ""
	else:	
		resultText += "</li>"
	return resultText