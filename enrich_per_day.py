import MySQLdb
import urllib
import urllib2
import json
import re

def get_data_to_enrich(db_name,start,end):
	pids=[]
	syn_res = {}
	titles_res ={}
	db = MySQLdb.connect("","","",db_name,use_unicode=True,charset="utf8")
	cursor = db.cursor()
	
	
	cursor.execute("select programme_info.pid, title, long_synopsis, medium_synopsis, short_synopsis from programme_info, epg where epg.start_time <= %s and epg.start_time >= %s and programme_info.pid = epg.pid;",(end,start))
	data = cursor.fetchall()
	for d in data:
		#if d[0] not in pids:
		print d[0]
		titles_res[d[0]]=d[1]
		long_synopsis = d[2]
		medium_synopsis = d[3]
		short_synopsis = d[4]
		if long_synopsis !='':
			syn_res[d[0]] = long_synopsis
		elif medium_synopsis!='':
			syn_res[d[0]] = medium_synopsis
		else:
			syn_res[d[0]] = short_synopsis
	res = [titles_res,syn_res]
	db.close()
	return res

def get_credits_to_enrich(db_name):		
	crids=[]
	crid_pid_role={}
	crid_res={}
	db = MySQLdb.connect("","","",db_name,use_unicode=True,charset="utf8")
	cursor = db.cursor()
	cursor.execute("Select distinct credits_annotations.credit_id from credits_annotations, programme_credits where credits_annotations.`credit_id` = programme_credits.`credit_id`;")
	data1 = cursor.fetchall()
	for d in data1:
		crids.append(d[0])
	cursor.execute("select programme_credits.credit_id, credit_name, programme_credits.pid, programme_credits.role from credits, programme_credits WHERE programme_credits.credit_id = credits.credit_id LIMIT 10;")
	data = cursor.fetchall()
	for d in data:
		if d[0] not in crids:
			crid_res[d[0]]=d[1]
			crid_pid_role[d[0]]={}
			crid_pid_role[d[0]][d[2]]=d[3]
	res=[crid_res,crid_pid_role]
	return res
	
def get_credit_enrichment(credits,db_name):
	db = MySQLdb.connect("","","",db_name,use_unicode=True,charset="utf8")
	cursor = db.cursor()
	credit_name = credits['name']
	credit_name = re.sub('\'', '\\\'',credit_name)
	birthdate = credits['birthdate']
	gender = credits['gender']
	credit_annotations = credits['categories']
	credit_annotations = list(set(credit_annotations))
	for category in credit_annotations:	
		credit_annotation_name = 'categories'
		credit_annotation_URIs = ''#credits['categories_uris']
		credit_annotation_value = category
		credit_annotation_value=re.sub('Category:','',credit_annotation_value)
		print category
		print credit_annotation_value
		'''
		if credit_name != credit_annotation_value :
			names = credit_name.split()
			names[0] = re.sub('\'', '\\\'', names[0] )	
			query = "SELECT credit_id FROM credits WHERE credit_name LIKE '%%%s" %names[0]
			for n in range (1,len(names)):
				names[0] = re.sub('\'', '\\\'', names[0] )	
				query += "%' AND credit_name LIKE '%"+ names[n]
			query +="%'"
			#print query

			cursor.execute(query)
			cdata = cursor.fetchall()
			credit_id=''

			for row in cdata :
				credit_id = (row[0])
			#print '%s %s %s %s' %(credit_id,credit_name,credit_annotation_value,credit_annotation_URIs[0])
			if credit_id!='':
				try:
					cursor.execute("INSERT INTO credits_annotations(credit_id,annotation_name,annotation_value,annotation_URIs) VALUES (%s,%s,%s,%s)",(credit_id,credit_annotation_name,credit_annotation_value,credit_annotation_URIs[0]))
					db.commit()	
				except:
					db.rollback()
				try:
					cursor.execute("UPDATE credits SET birthdate=%s, gender=%s WHERE credit_id=", (birthdate,gender,credit_id))
					db.commit()
				except:
					db.rollback()
		'''
	db.close()
		

def get_synopsis_enrichment(data,db_name):
	db = MySQLdb.connect("","","",db_name,use_unicode=True,charset="utf8")
	cursor = db.cursor()
	Synopsis_concepts = data['synopsis_enrichments_concepts']
	pid = data['pid']
	#print Synopsis_concepts
	
	for i in range(0,len(Synopsis_concepts)):
		programme_annotation_name = 'Synopsis concept'	 
		programme_annotation_value = Synopsis_concepts[i]['category']
		programme_annotation_value=re.sub('Category:','',programme_annotation_value)
		#print programme_annotation_value
		programme_annotation_URIs = Synopsis_concepts[i]['category_URIs']		
		
		try:
			cursor.execute("INSERT INTO programme_annotations(pid,annotation_name,annotation_value) VALUES (%s,%s,%s)",(pid,programme_annotation_name,programme_annotation_value))
			db.commit()	
		except:
			db.rollback()
	
	db.close()
	
def get_title_enrichment(data,db_name):
	db = MySQLdb.connect("","","",db_name,use_unicode=True,charset="utf8")
	cursor = db.cursor()
	DB_Categories = data['DBpedia categories']
	pid = data['pid']
	#print 'db: ' + str(DB_Categories)
	for i in range(0,len(DB_Categories)):
		programme_annotation_name = 'DB Category'
		programme_annotation_value = DB_Categories[i]['category']
		programme_annotation_value = re.sub('Category:','',programme_annotation_value)
		programme_annotation_URIs = DB_Categories[i]['category_URIs']
		try:
			cursor.execute("INSERT INTO programme_annotations(pid,annotation_name,annotation_value,annotation_URIs) VALUES (%s,%s,%s,%s)",(pid,programme_annotation_name,programme_annotation_value,programme_annotation_URIs))
			db.commit()
		except:
			db.rollback()
	date = data['releaseDate']
	if date!='':
		try:
			cursor.execute("UPDATE programme_info SET Release_Date = %s",date)
			db.commit()	
		except:
			db.rollback()

	reviews = data['reviews']
	if len(reviews)>0:
		for i in range(0,len(reviews)):
			programme_annotation_name = 'Rotten Tomatoes Review'
			programme_annotation_value = reviews[i]['review']
			programme_annotation_analysis = get_sentiment(reviews[i]['review'])
			programme_annotation_URIs = reviews[i]['publication']
			try:
				cursor.execute("INSERT INTO programme_annotations(pid,annotation_name,annotation_value,annotation_URIs,annotation_analysis) VALUES (%s,%s,%s,%s,%s)",(pid,programme_annotation_name,programme_annotation_value,programme_annotation_URIs,programme_annotation_analysis))
				db.commit()	
			except:
				db.rollback()

	ratings = data['ratings']
	if len(ratings)>0: 
		programme_annotation_name = 'Rotten Tomatoes Critic rating'
		programme_annotation_value = ratings[0]['critics_rating']
		try:
			cursor.execute("INSERT INTO programme_annotations(pid,annotation_name,annotation_value) VALUES (%s,%s,%s)",(pid,programme_annotation_name,programme_annotation_value))
			db.commit()	
		except:
			db.rollback()
	
		programme_annotation_name = 'Rotten Tomatoes Critic score'
		programme_annotation_value = ratings[1]['critics_score']		
		try:
			cursor.execute("INSERT INTO programme_annotations(pid,annotation_name,annotation_value) VALUES (%s,%s,%s)",(pid,programme_annotation_name,programme_annotation_value))
			db.commit()	
		except:
			db.rollback()

		programme_annotation_name = 'Rotten Tomatoes Audience rating'
		programme_annotation_value = ratings[2]['audience_rating']
		try:
			cursor.execute("INSERT INTO programme_annotations(pid,annotation_name,annotation_value) VALUES (%s,%s,%s)",(pid,programme_annotation_name,programme_annotation_value))
			db.commit()	
		except:
			db.rollback()

		programme_annotation_name = 'Rotten Tomatoes Audience score'
		programme_annotation_value = ratings[3]['audience_score']
		try:
			cursor.execute("INSERT INTO programme_annotations(pid,annotation_name,annotation_value) VALUES (%s,%s,%s)",(pid,programme_annotation_name,programme_annotation_value))
			db.commit()	
		except:
			db.rollback()
	db.close()

def external_BBC_data(credits,start,end):
	#print credits
	for elem in credits:
		for pid in elem.keys():
			for credit_name in elem[pid].keys():
				credit_role = elem[pid][credit_name]
# 				url = "http://eculture2.cs.vu.nl:3020/enrichCredit?pid=%s&credit_name=%s&credit_role=%s&source=%s&indent=true" % (pid,urllib.quote(credit_name.encode('utf8')),urllib.quote(credit_role.encode('utf8')),'BBC')
				print url
				try:
					json_data = urllib2.urlopen(url)
					data = json.load(json_data)
					#print data
					get_credit_enrichment(data[0],'vista_tv_bbc')
				except:
					continue
	
	data = get_data_to_enrich('vista_tv_bbc',start,end)
	titles = data[0]
	synopses = data[1]
	for pid in titles.iterkeys():
		title = titles[pid]
#		url = "http://eculture2.cs.vu.nl:3020/enrichTitle?pid=%s&title=%s&source=%s&indent=true" % (pid,urllib.quote(title.encode('utf8')),'BBC')
		
		try:
			json_data = urllib2.urlopen(url)
			data = json.load(json_data)
			get_title_enrichment(data[0],'vista_tv_bbc')
		except:
			continue
			
	for pid in synopses.iterkeys():
		synopsis = synopses[pid]
		url = "http://eculture2.cs.vu.nl:3020/enrichSynopsis?pid=%s&synopsis=%s&source=%s&indent=true" % (pid,urllib.quote(synopsis.encode('utf8')),'BBC')
		try:
			json_data = urllib2.urlopen(url)
			data = json.load(json_data)
			#print data
			get_synopsis_enrichment(data[0],'vista_tv_bbc')
		except:
			continue
			

	
