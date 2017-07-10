#!/usr/bin/env python
import sys
import requests
import json
from datetime import datetime
import xml.etree.cElementTree as ET

try:
	from bs4 import BeautifulSoup
except:
	pass

class SMS():
	def __init__(self):
		self.message = ''
		self.send_to = []

class SendSMS():
	def __init__(self):
		self.URL = 'http://192.168.8.1/' #the url for the donge, this is usually http://192.168.8.1/
		self.default_page = self.URL+'html/index.html'
		self.sms_sender_URL = self.URL+'html/smsinbox.html'
		self.sms_send_url = self.URL+'api/sms/send-sms'
	
		self.csrf_token_pattern = '<meta name="csrf_token" content="'
		self.csrf_token_name = "csrf_token"
		self.sms_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		self.session = requests.Session()
		self.token = ''
	
	
	def send(self, sms):
		self.create_session()
		self.get_token()
		data = self.merge_template(sms)
		headers = {}
		headers['__RequestVerificationToken'] = self.token
		headers['X-Requested-With'] = 'XMLHttpRequest'
		headers['Content-Type'] = 'text/xml'
	
		response = self.session.post(self.sms_send_url , data=data , headers = headers)
	
	def create_session(self):
		response = self.session.get(self.default_page)
	
	def get_token(self):
		#Huawei E3372: the CSRF token is in the HTML body inside a 'meta' element called 'csrf_token'. !!! There are 2 of such tokens in the response, you must use the first one!!
		response = self.session.get(self.sms_sender_URL)
		if 'bs4' not in sys.modules:
			#print 'WARNING! HTML processing module BeautifulSoup is not available, from this point onwards we can only guess where the csrf token is!'
			token_start = response.text.find(self.csrf_token_pattern)
			if token_start != -1:
				token_start += len(self.csrf_token_pattern)
				token_end = token_start + response.text[token_start:].find('"')
				self.token = response.text[token_start:token_end]
	
		else:
			soup = BeautifulSoup(response.text, "html.parser")
			for token in soup.findAll('meta', attrs={'name':self.csrf_token_name}):
				self.token = token['content']
				break
	
	def merge_template(self,sms):
		request = ET.Element("request")
		pageindex = ET.SubElement(request, "Index")
		pageindex.text = "-1"
	
		phones = ET.SubElement(request, "Phones")
		sca = ET.SubElement(request, "Sca")
		content = ET.SubElement(request, "Content")
		length = ET.SubElement(request, "Length")
		reserved = ET.SubElement(request, "Reserved")
		reserved.text = "1"
		date = ET.SubElement(request, "Date")
	
		for number in sms.send_to:
			phone = ET.SubElement(phones, "Phone")
			phone.text = number
	
		content.text = sms.message
		length.text = str(len(sms.message))
		date.text = self.sms_time
		return (ET.tostring(request, 'utf-8', method="xml"))
						
						
if __name__ == '__main__':

	number = ''
	sms = SMS()
	sms.send_to.append(number)
	sms.message = 'HELLO WORLD'

	smsSender = SendSMS()
	smsSender.send(sms)
	print 'Done!'