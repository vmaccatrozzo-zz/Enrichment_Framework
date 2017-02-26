#!/usr/bin/python

from xml.dom.minidom import parse
import xml.dom.minidom
import urllib2
import MySQLdb
import time
from datetime import datetime
from datetime import timedelta


def write_programme_data(pid):
	time.sleep(1)	
	headers = { 'User-Agent' : 'VistaTV/VU' }
	url = "http://www.bbc.co.uk/programmes/%s.xml" % pid
	req = urllib2.Request(url, None, headers)
	#url="http://www.bbc.co.uk/programmes/b00b0c5b.xml"
	DOMTree = xml.dom.minidom.parse(urllib2.urlopen(req))
	query_time = datetime.now()
	main_programme = DOMTree.documentElement
	#pid = main_programme.getElementsByTagName('pid')[0].childNodes[0].data
	try:
		short_synopsis = main_programme.getElementsByTagName('short_synopsis')[0].childNodes[0].data.encode('utf-8')
	except:
		short_synopsis =''
	try:
		medium_synopsis = main_programme.getElementsByTagName('medium_synopsis')[0].childNodes[0].data.encode('utf-8')
	except:
		medium_synopsis = ''
	try: 	
		long_synopsis = main_programme.getElementsByTagName('long_synopsis')[0].childNodes[0].data.encode('utf-8')
	except:
		long_synopsis = ''
	if not('Welsh Assembly' in short_synopsis or 'Welsh Assembly' in medium_synopsis or 'Welsh Assembly' in long_synopsis or 'Scottish Parliament' in short_synopsis or 'Scottish Parliament' in medium_synopsis or 'Scottish Parliament' in long_synopsis or 'Stormont' in short_synopsis or 'Stormont' in medium_synopsis or 'Stormont' in long_synopsis):
		title = main_programme.getElementsByTagName('display_title')[0].getElementsByTagName('title')[0].childNodes[0].data.encode('utf-8')
		try:
			subtitle = main_programme.getElementsByTagName('display_title')[0].getElementsByTagName('subtitle')[0].childNodes[0].data.encode('utf-8')
		except:
			subtitle = ''
		channel_name = main_programme.getElementsByTagName('ownership')[0].getElementsByTagName('title')[0].childNodes[0].data.encode('utf-8')
		channel_id = main_programme.getElementsByTagName('ownership')[0].getElementsByTagName('service')[0].getAttribute("id")
		version = main_programme.getElementsByTagName('versions')[0].getElementsByTagName('version')[0].getElementsByTagName('pid')[0].childNodes[0].data.encode('utf-8')	
	
		difference = datetime.now() - query_time
		if difference.seconds < 60 :
			time.sleep(difference.seconds)	
			query_time = datetime.now()	
		url = "http://www.bbc.co.uk/programmes/"+version+".xml"
		DOMTree = xml.dom.minidom.parse(urllib2.urlopen(url))
		version_programme = DOMTree.documentElement	
		if main_programme.getAttribute("type") == "episode":
			try:
				parent_pid = main_programme.getElementsByTagName("parent")[0].getElementsByTagName("programme")[0].getElementsByTagName('pid')[0].childNodes[0].data.encode('utf-8')
			except:
				parent_pid =''
	##########DATABASE POPULATION#################
		# Open database connection
		db = MySQLdb.connect("","","","")
		# prepare a cursor object using cursor() method
		cursor = db.cursor()
		# INSERT programme info
		#try:
		   # Execute the SQL command
		cursor.execute("INSERT INTO programme_info(pid,title,episode_title,short_synopsis,medium_synopsis,long_synopsis,main_programme_pid,language) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(pid,title,subtitle,short_synopsis,medium_synopsis,long_synopsis,parent_pid,'English'))
		   # Commit your changes in the database
		db.commit()
		#except:
		   # Rollback in case there is any error
		#	db.rollback()
		
		#INSERT categories
		categories = main_programme.getElementsByTagName("category")
		for category in categories: 
			try:
				category_id = category.getAttribute("id")
			except:
				category_id=''
			try:
			   # Execute the SQL command
				cursor.execute("INSERT INTO programme_categories(pid,cat_id) VALUES (%s,%s)",(pid,category_id))
			   # Commit your changes in the database
				db.commit()
			except:
			   # Rollback in case there is any error
				db.rollback()		
		contributors = version_programme.getElementsByTagName('contributor')
		credits={}
		for contributor in contributors:
			try:
				family_name = contributor.getElementsByTagName('family_name')[0].childNodes[0].data
			except: 
				family_name=''		
			try:
				given_name = contributor.getElementsByTagName('given_name')[0].childNodes[0].data
			except:
				given_name =''
			try:
				role = contributor.getElementsByTagName('role')[0].childNodes[0].data
			except:
				role=''
			credit_name = family_name + ' ' + given_name
			family_name='%'+family_name+'%'
			given_name='%'+given_name+'%'
			
			if not pid in credits.keys():
				credits[pid]={}
			credits[pid][credit_name]=role
			
			cursor.execute("SELECT credit_id FROM credits WHERE credit_name LIKE %s AND credit_name LIKE %s",(family_name, given_name)) 
			data = cursor.fetchall()
			if len(data)==0:					
				cursor.execute("INSERT INTO credits(credit_name) VALUES (%s)",(credit_name))
				db.commit()
				cursor.execute("SELECT credit_id FROM credits WHERE credit_name = %s",(credit_name))
				data = cursor.fetchall()
			for row in data :
				
				credit_id = (row[0])
			try:
				# Execute the SQL command
				cursor.execute("INSERT INTO programme_credits(pid,credit_id,role) VALUES (%s,%s,%s)",(pid,credit_id,role))
				# Commit your changes in the database
				db.commit()
			except:
				# Rollback in case there is any error
				db.rollback()	

		db.close()
		
	return credits
