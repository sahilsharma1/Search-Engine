from flask import Flask, render_template , jsonify , request
from search import Search
import enchant
import config
import MySQLdb
from flask import send_file
import urlparse
from posixpath import basename, dirname

app = Flask(__name__,static_folder='/home/sjha/development/web_crawler/search_engine/tutorial/templates')

d = enchant.Dict("en_US")

@app.route('/')
def helloWorld():
	return render_template('index.html')

@app.route('/search',methods=['GET','POST'])
def search():
	suggestions = []
	term = request.args.get('term').lower()
	if(not(d.check(term))):
		suggestions = d.suggest(term)

	database = MySQLdb.connect(config.settings['host'],config.settings['user'],\
		config.settings['password'],config.settings['database_name'] )

	cursor = database.cursor()

	suggestions = []

 	suggestions.append(term)
   	if(len(suggestions)):
	   	for suggestion in suggestions:
	   		sql = """INSERT INTO search_terms(search_term) 
	   				SELECT * FROM (SELECT %s) AS tmp
	   				WHERE NOT EXISTS (
    				   SELECT search_term FROM search_terms WHERE search_term = %s) 
					LIMIT 1;"""
			try:
		   		cursor.execute(sql,(str(suggestion),str(suggestion)))
		   		database.commit()
			except:
		   		database.rollback()

	database.close()

	terms = term.split(" ")
	
	searchResult = ""
	# urls = open("uniqueUrl (copy).txt","r").readlines()
	# for url in urls:
	# 	if any(word in url for word in terms):
	# 		parse_object = urlparse.urlparse(url)
	# 		title_head = basename(parse_object.path).split(".")[0].decode("utf-8", 'ignore')
	# 		if(title_head == " "):
	# 			title_head = str(url)
	# 		searchResult += "<a href='"+url+"'>" + title_head + "</a> <br><span>" + url+ "</span><br><br>"
	
	searchResult += Search(term)

	if(searchResult):
		return searchResult
	else:
		searchResult += "<h2>Sorry No result found for " +term +".Please Try again.</h2>"
		return searchResult
	# else:
	# 	suggestions = d.suggest(term)
	# 	searchResult += "<h2>Did you mean ..</h2>"
	# 	for suggestion in suggestions:
	# 		searchResult += "<a href='#' class='suggestions'>" +suggestion+ "</a> <br>"
	# 	return searchResult


@app.route('/updateAutoCompleteDB',methods=['GET','POST'])
def updateAutoCompleteDB():
	database = MySQLdb.connect(config.settings['host'],config.settings['user'],\
		config.settings['password'],config.settings['database_name'] )

	cursor = database.cursor()
	sql = "SELECT DISTINCT search_term FROM `search_terms` WHERE 1 ORDER BY time_of_search DESC"
	search_term = []
	resultText = ""
	try:
   		cursor.execute(sql)
   		numrows = cursor.rowcount
   		results = cursor.fetchall()
   		for row in results:
   			search_term.append(row[0])
   		resultText = ",".join(search_term)
   	except:
   		resultText += cursor._last_executed + " Did not bring"
   	database.close()
   	return resultText

@app.route('/get_terms',methods=['GET','POST'])
def get_terms():
	time = request.args.get('time')
	database = MySQLdb.connect(config.settings['host'],config.settings['user'],\
		config.settings['password'],config.settings['database_name'] )

	cursor = database.cursor()
	sql = "SELECT DISTINCT search_term FROM `search_terms` WHERE time_of_search > NOW() - INTERVAL "+time+" HOUR ORDER BY time_of_search DESC"
	resultText = ""
	try:
   		cursor.execute(sql)
   		numrows = cursor.rowcount
   		results = cursor.fetchall()
   		for row in results:
   			resultText += "<a href='#' class='suggestions'>"+row[0]+"</a><br>"
   	except:
   		resultText += cursor._last_executed + " Did not bring"
   	database.close()
   	return resultText

@app.route('/get_image',methods=['GET','POST'])
def get_image():
    if request.args.get('type') == '1':
       filename = '/home/sjha/development/web_crawler/search_engine/tutorial/templates/voice.jpg'
    else:
       filename = 'error.gif'
    return send_file(filename, mimetype='image/jpg')

@app.route('/get_css',methods=['GET','POST'])
def get_css():
    if request.args.get('type') == '1':
       filename = '/home/sjha/development/web_crawler/search_engine/tutorial/templates/w3.css'
    elif request.args.get('type') == '2':
       filename = '/home/sjha/development/web_crawler/search_engine/tutorial/templates/font-awesome.min.css'
    elif request.args.get('type') == '3':
       filename = '/home/sjha/development/web_crawler/search_engine/tutorial/templates/main.css'
    elif request.args.get('type') == '4':
       filename = '/home/sjha/development/web_crawler/search_engine/tutorial/templates/jquery-ui.css'
    return send_file(filename, mimetype='text/css')

@app.route('/get_js',methods=['GET','POST'])
def get_js():
    if request.args.get('type') == '1':
       filename = '/home/sjha/development/web_crawler/search_engine/tutorial/templates/jquery.min.js'
    elif request.args.get('type') == '2':
       filename = '/home/sjha/development/web_crawler/search_engine/tutorial/templates/jquery-1.10.2.js'
    elif request.args.get('type') == '3':
       filename = '/home/sjha/development/web_crawler/search_engine/tutorial/templates/jquery-ui.js'
    return send_file(filename, mimetype='text/javascript')

@app.route('/images/ui-bg_flat_75_ffffff_40x100.png',methods=['GET','POST'])
def png():
	filename = "/home/sjha/development/web_crawler/search_engine/tutorial/templates/images/ui-bg_flat_75_ffffff_40x100.png"
	return send_file(filename,mimetype='image/png')

@app.route('/images/ui-bg_glass_75_dadada_1x400.png',methods=['GET','POST'])
def png2():
	filename = "/home/sjha/development/web_crawler/search_engine/tutorial/templates/images/ui-bg_glass_75_dadada_1x400.png"
	return send_file(filename,mimetype='image/png')

@app.route('/form_search',methods=['GET','POST'])
def form_search():
	term = request.args.get('term')
	terms=term.split(" ")
	if "form" in terms:
		terms.remove("form")
	resultText = ""
	urls = open("uniqueUrltest.txt",'r')
	i = 0
	for url in urls:
		if(i < 16 and (".pdf" in url or ".doc" in url)):
			if any(word in url for word in terms):
				parse_object = urlparse.urlparse(url)
				if "." not in parse_object.path:
					title_head = parse_object.path
				else:
					title_head = basename(parse_object.path).split(".")[0].decode("utf-8", 'ignore')
				
				resultText += "<h3><a href='"+url+"'>" + title_head + "</a></h3><p class='green'>" + url+ "</p>"
				i += 1
	urls.close()
	return resultText

if __name__ == '__main__':
	app.run(debug=True)
