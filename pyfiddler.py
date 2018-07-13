# coding:utf-8
"""
pip install pythonnet
.NET 公共语言运行库 (CLR)
"""
import os
import clr
import sys
import time
import json
import win32api
import win32con
from certificate import *
sys.path.append("./FiddlerCoreAPI")
clr.FindAssembly("FiddlerCore4")
clr.AddReference("FiddlerCore4")
import Fiddler as FC
import plugins

def onClose(sig=1):
	FC.FiddlerApplication.Shutdown()
	win32api.MessageBox(win32con.NULL, 'See you later', 'Exit', win32con.MB_OK)

def printLog(source, oLEA):
	pass

def printSession(s):
	pass

def fiddler(FC, flags):
	"""
	# register event handler
	# object.SomeEvent += handler
	#
	# unregister event handler
	# object.SomeEvent -= handler
	#
	# passed a callable Python object to get a delegate instance.
	"""
	
	FC.FiddlerApplication.Log.OnLogString += printLog
	FC.FiddlerApplication.AfterSessionComplete += plugins.My_AfterSessionComplete
	FC.FiddlerApplication.BeforeRequest += plugins.My_BeforeRequest
	FC.FiddlerApplication.BeforeResponse += plugins.My_BeforeResponse
	
	## When decrypting HTTPS traffic,ignore the server certificate errors
	FC.CONFIG.IgnoreServerCertErrors = True
	
	## start up capture
	FC.FiddlerApplication.Startup(8888, flags)


if __name__ == '__main__':
   
	win32api.SetConsoleCtrlHandler(onClose, 1)
	# captureType = "http"
	captureType = "https"
	
	"""
	#RegisterAsSystemProxy:1
	#OptimizeThreadPool:512
	#MonitorAllConnections:32
	#DecryptSSL:2
	#AllowRemoteClients:8
	"""
	
	if captureType == "https":
		prepareCert(FC)
		# fiddler(FC, 1+512+32+2)
		fiddler(FC, 512+32+2+8)
	else:
		# fiddler(FC, 1+512+32)
		fiddler(FC, 512+32+8)
		
	# os.system("cls")
	
	while True:
		try:
			time.sleep(2)
		except KeyboardInterrupt:
			onClose()
			sys.exit(0)

