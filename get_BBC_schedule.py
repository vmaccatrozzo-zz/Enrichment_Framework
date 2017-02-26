from xml.dom.minidom import parse
import xml.dom.minidom
import urllib2
import MySQLdb
import time
from datetime import datetime
from datetime import timedelta

import time
from bbc_xml_to_db import write_programme_data
from enrich_per_day import external_BBC_data
credits=[]

def testTimeFormat(input):
    try:
        input = datetime.strptime(input, "%Y-%m-%dT%H:%M:%S+01:00")
        return True
    except:
        return False
def testTimeFormat2(input):
    try:
        input = datetime.strptime(input, "%Y-%m-%dT%H:%M:%S+02:00")
        return True
    except:
        return False
        
##date format YYYY/MM/DD

def get_data(cid, broadcast):
	start = broadcast.getElementsByTagName("start")[0].childNodes[0].data
	end = broadcast.getElementsByTagName("end")[0].childNodes[0].data
	if  testTimeFormat(start):
		st = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S+01:00")
		st = st - timedelta(hours=1) 
		start = st.strftime("%Y-%m-%d %H:%M:%S")
	elif  testTimeFormat2(start):
		st = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S+01:00")
		st = st - timedelta(hours=2) 
		start = st.strftime("%Y-%m-%d %H:%M:%S")
	else:
		start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")
		
	if  testTimeFormat(end):
		en = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S+01:00")
		en = en - timedelta(hours=1) 
		end = en.strftime("%Y-%m-%d %H:%M:%S")
	elif  testTimeFormat2(end):
		en = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S+01:00")
		en = en - timedelta(hours=2) 
		end = en.strftime("%Y-%m-%d %H:%M:%S")
	else:
		end = datetime.strptime(end, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")
	
	
	programmes = broadcast.getElementsByTagName("programme")
	for programme in programmes:
		programme_type = programme.getAttribute("type")
		if programme_type=='episode':
			pid = programme.getElementsByTagName("pid")[0].childNodes[0].data
			db = MySQLdb.connect("","","","")#set your own MySQL credentials
			cursor = db.cursor()
			cursor.execute("SELECT * FROM programme_info WHERE pid= %s",(pid))
			data = cursor.fetchall()
			if len(data)==0:
				credits.append(write_programme_data(pid))
				print(pid)
			cursor.execute("SELECT * FROM epg WHERE pid= %s and start_time=%s and channel_id=%s",(pid, start,cid))
			data_epg = cursor.fetchall()
			if len(data_epg)>0 and pid!=data_epg[0][0] and start != data_epg[0][1] and end != data_epg[0][2] and cid != data_epg[0][3]:
				#print pid
				wrong_pid = data_epg[0][0]
				wrong_start_time = data_epg[0][1]
				wrong_end_time = data_epg[0][2]
				wrong_channel_id=data_epg[0][3]
				try:	
					cursor.execute("UPDATE epg set pid=%s, start_time=%s, end_time=%s, channel_id=%s where pid=%s and start_time=%s and end_time=%s and channel_id=%s",(pid,start,end,cid, wrong_pid, wrong_start_time,wrong_end_time,wrong_channel_id))
					db.commit()
				except:
					db.rollback()
			
			elif len(data_epg)==0:	
				try:			
					cursor.execute("INSERT INTO epg(pid,start_time,end_time,channel_id) VALUES (%s,%s,%s,%s)",(pid,start,end,cid))
					db.commit()
				except:
					db.rollback()
			db.close()
	#print credits	
				
	
	

def get_schedule(date):

	db = MySQLdb.connect("127.0.0.1","vua","ulSZmNJy57eC","vista_tv_bbc")
	cursor = db.cursor()
	date_to_use = date
	
	########BBC ONE########		
	query_time = datetime.now()	
	#try:
	url='http://www.bbc.co.uk/bbcone/programmes/schedules/london/%s.xml' %date
	DOMTree = xml.dom.minidom.parse(urllib2.urlopen(url))
	print(url)		
	cid='bbcone'
	schedule = DOMTree.documentElement
	broadcasts = schedule.getElementsByTagName("broadcast")
	for broadcast in broadcasts: 
		get_data(cid,broadcast)
	#except:
	#	print '%s file not found' %cid

					
	########BBC TWO########		
	difference = datetime.now() - query_time
	if difference.seconds < 1 :
		time.sleep(difference.seconds)	
		query_time = datetime.now()	
	try:	
		url='http://www.bbc.co.uk/bbctwo/programmes/schedules/england/%s.xml' %date
		DOMTree = xml.dom.minidom.parse(urllib2.urlopen(url))
		print(url)
	
		cid='bbctwo'
		schedule = DOMTree.documentElement
		broadcasts = schedule.getElementsByTagName("broadcast")
		for broadcast in broadcasts: 
			get_data(cid,broadcast)
	except:
		print '%s file not found' %cid

		
	########BBC THREE########		
	difference = datetime.now() - query_time
	if difference.seconds < 1 :
		time.sleep(difference.seconds)	
		query_time = datetime.now()	
	try:
		url='http://www.bbc.co.uk/bbcthree/programmes/schedules/%s.xml' %date
		DOMTree = xml.dom.minidom.parse(urllib2.urlopen(url))
		print(url)
		cid='bbcthree'
		schedule = DOMTree.documentElement
		broadcasts = schedule.getElementsByTagName("broadcast")
		for broadcast in broadcasts: 
			get_data(cid,broadcast)
	except:
		print '%s file not found' %cid

	########BBC FOUR########		
	difference = datetime.now() - query_time
	headers = { 'User-Agent' : 'VistaTV/VU' }
	
	
	if difference.seconds < 1 :
		time.sleep(difference.seconds)	
		query_time = datetime.now()	
	try:
		url='http://www.bbc.co.uk/bbcfour/programmes/schedules/%s.xml' %date
		req = urllib2.Request(url, None, headers)
		#url="http://www.bbc.co.uk/programmes/b00b0c5b.xml"
		DOMTree = xml.dom.minidom.parse(urllib2.urlopen(req))
		print(url)
		cid='bbcfour'
		schedule = DOMTree.documentElement
		broadcasts = schedule.getElementsByTagName("broadcast")
		for broadcast in broadcasts: 
			get_data(cid,broadcast)
	except:
		print '%s file not found' %cid

	#######CBBC#########		
	difference = datetime.now() - query_time
	if difference.seconds < 1 :
		time.sleep(difference.seconds)	
		query_time = datetime.now()
	try:		 
		url='http://www.bbc.co.uk/cbbc/programmes/schedules/%s.xml' %date
		req = urllib2.Request(url, None, headers)
		
		DOMTree = xml.dom.minidom.parse(urllib2.urlopen(req))		
		print(url)
		cid='cbbc'
		schedule = DOMTree.documentElement
		broadcasts = schedule.getElementsByTagName("broadcast")
		for broadcast in broadcasts: 
			get_data(cid,broadcast)
	except:
		print '%s file not found' %cid
	
	#######CBEEBIES#########		
	difference = datetime.now() - query_time
	if difference.seconds < 1 :
		time.sleep(difference.seconds)	
		query_time = datetime.now()	
	try:	 
		url='http://www.bbc.co.uk/cbeebies/programmes/schedules/%s.xml' %date
		req = urllib2.Request(url, None, headers)
		#url="http://www.bbc.co.uk/programmes/b00b0c5b.xml"
		DOMTree = xml.dom.minidom.parse(urllib2.urlopen(req))
		print(url)
		cid='cbeebies'
		schedule = DOMTree.documentElement
		broadcasts = schedule.getElementsByTagName("broadcast")
		for broadcast in broadcasts: 
			get_data(cid,broadcast)
	except:
		print '%s file not found' %cid
	
	#######BBC parliament#########		
	difference = datetime.now() - query_time
	if difference.seconds < 1 :
		time.sleep(difference.seconds)	
		query_time = datetime.now()	
	
	try:	 
		url='http://www.bbc.co.uk/parliament/programmes/schedules/%s.xml' %date
		req = urllib2.Request(url, None, headers)
		#url="http://www.bbc.co.uk/programmes/b00b0c5b.xml"
		DOMTree = xml.dom.minidom.parse(urllib2.urlopen(req))
		print(url)
		cid='bbcparliament'
		schedule = DOMTree.documentElement
		broadcasts = schedule.getElementsByTagName("broadcast")
		for broadcast in broadcasts: 
			get_data(cid,broadcast)
	except:
		print '%s file not found' %cid
	
	#######BBC news#########		
	difference = datetime.now() - query_time
	if difference.seconds < 1 :
		time.sleep(difference.seconds)	
		query_time = datetime.now()	
	
	try:	 
		url='http://www.bbc.co.uk/bbcnews/programmes/schedules/%s.xml' %date
		req = urllib2.Request(url, None, headers)
		#url="http://www.bbc.co.uk/programmes/b00b0c5b.xml"
		DOMTree = xml.dom.minidom.parse(urllib2.urlopen(req))
		print(url)
		cid='bbcnews'
		schedule = DOMTree.documentElement
		broadcasts = schedule.getElementsByTagName("broadcast")
		for broadcast in broadcasts: 
			get_data(cid,broadcast)
	except:
		print '%s file not found' %cid
	
	#date ='%Y/%m/%d'
	start = datetime.strptime(date, "%Y/%m/%d").strftime('%Y-%m-%d')+ ' 00:00:00'
	end = datetime.strptime(date, "%Y/%m/%d").strftime('%Y-%m-%d')+ ' 23:59:59'
	print('starting enrichment')
	external_BBC_data(credits,start,end)
	return True

