# coding:utf-8
import sys
import thread
import requests

KEYWORDS = [u"手机号码", u"QQ号码", u"用户昵称等"]

def has_sensitive_infomation(content):
	for keyword in KEYWORDS:
		if keyword in content:
			return True
	return False

def is_reffer_needed(url, reqHeaders_string):
	headers = {}
	for row in reqHeaders_string.split("\r\n")[1:]:
		if ": " not in row:
			continue
		k, v = row.strip().split(": ", 1)
		if k.lower() == "referer":
			continue
		headers[k.encode("utf8")] = v.encode("utf8")
		
	conn = requests.get(url=url, headers=headers, verify=False)
	data = conn.content.decode(conn.apparent_encoding, "ignore")
	
	output = "=" * 60 + "\n"
	output += url + "\n"
	output += data + "\n"
	sys.stdout.write(output)

def My_BeforeRequest(s):
	pass

def My_BeforeResponse(s):
	pass

def My_AfterSessionComplete(s):
	if s is None or s.oRequest is None or s.oRequest.headers is None:
		return

	if s.RequestMethod != "GET":
		return
	
	url = s.get_url()
	full_url = s.fullUrl
	reqHeaders = s.oRequest.headers.ToString()
	reqBody = s.GetRequestBodyAsString()
	
	respHeaders = s.oResponse.headers.ToString()
	respBody = s.GetResponseBodyAsString()
	
	if "application/json" in respHeaders.lower() and (not has_sensitive_infomation(url+"\n"+reqBody)) and has_sensitive_infomation(respBody):
		# ret = is_reffer_needed(full_url, reqHeaders)
		thread.start_new_thread(is_reffer_needed, (full_url, reqHeaders))
