#encoding=utf8
import os
import time
import psutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

My_PROXY = "127.0.0.1:8888"
TIMEOUT = 30 * 5

def run_xvfb():
	is_running = False
	for pid in psutil.pids():
		p = psutil.Process(pid)
		cmdline = p.cmdline()
		if "Xvfb" in cmdline:
			print "Xvfb IS RUNNING..."
			is_running = True
			os.system("export DISPLAY=:10")
			
	if not is_running:
		print "Xvfb IS NOT RUNNING..."
		os.system("killall Xvfb")
		time.sleep(2)
		os.system("Xvfb :10 -ac &")
		time.sleep(5)
		os.system("export DISPLAY=:10")
		time.sleep(1)
		
def create_browser(type="chrome", show=True):
	if type == "chrome":
		chrome_options = Options()
		
		# 0 == > default,
		# 1 == > Allow,
		# 2 == > Block.
		prefs = {
			# "profile.managed_default_content_settings.images": 2,
			# "profile.managed_default_content_settings.stylesheets": 2,
			# "profile.default_content_setting_values.notifications": 2,
			# "profile.managed_default_content_settings.cookies": 2,
			# "profile.managed_default_content_settings.javascript": 1,
			# "profile.managed_default_content_settings.plugins": 1,
			# "profile.managed_default_content_settings.popups": 2,
			# "profile.managed_default_content_settings.geolocation": 2,
			# "profile.managed_default_content_settings.media_stream": 2,
		}
		chrome_options.add_experimental_option("prefs", prefs)

		proxy = Proxy()
		proxy.proxy_type = ProxyType.MANUAL
		proxy.http_proxy = My_PROXY
		proxy.ssl_proxy = My_PROXY
		
		chrome_options.add_argument('--proxy-server={}'.format(My_PROXY))
		capabilities = webdriver.DesiredCapabilities.CHROME
		proxy.add_to_capabilities(capabilities)
		browser = webdriver.Chrome(desired_capabilities=capabilities, chrome_options=chrome_options)
	else:
		if not os.name == "nt":
			run_xvfb()
		
		# 0 == > default,
		# 1 == > Allow,
		# 2 == > Block.
		
		firefox_profile = FirefoxProfile()
		# firefox_profile.set_preference('permissions.default.stylesheet', 2)	## Disable CSS
		# firefox_profile.set_preference('permissions.default.image', 2)		## Disable images
		# # firefox_profile.set_preference('javascript.enabled', False)		    ## Disable JavaScript
		# # firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')	    ## Disable Flash
		# browser = webdriver.Firefox(firefox_profile)
		
		# firefox_profile = FirefoxProfile()
		# firefox_profile.add_extension("quickjava-2.1.2-fx.xpi")
		# firefox_profile.set_preference("thatoneguydotnet.QuickJava.curVersion", "2.1.2.1")			## Prevents loading the ‘thank you for installing screen’
		# firefox_profile.set_preference("thatoneguydotnet.QuickJava.startupStatus.Images", 2)			## Turns images off
		# firefox_profile.set_preference("thatoneguydotnet.QuickJava.startupStatus.AnimatedImage", 2)	## Turns animated images off
		# firefox_profile.set_preference("thatoneguydotnet.QuickJava.startupStatus.CSS", 2)  			## CSS
		# # firefox_profile.set_preference("thatoneguydotnet.QuickJava.startupStatus.Cookies", 2)  		## Cookies
		# # firefox_profile.set_preference("thatoneguydotnet.QuickJava.startupStatus.Flash", 2)  		## Flash
		# # firefox_profile.set_preference("thatoneguydotnet.QuickJava.startupStatus.Java", 2)  		## Java
		# # firefox_profile.set_preference("thatoneguydotnet.QuickJava.startupStatus.JavaScript", 2)  	## JavaScript
		# # firefox_profile.set_preference("thatoneguydotnet.QuickJava.startupStatus.Silverlight", 2)	## Silverlight
		
		firefox_profile.set_preference("network.proxy.type", 1)
		firefox_profile.set_preference("network.proxy.http", My_PROXY.split(":")[0])
		firefox_profile.set_preference("network.proxy.http_port", int(My_PROXY.split(":")[1]))
		firefox_profile.set_preference("network.proxy.https", My_PROXY.split(":")[0])
		firefox_profile.set_preference("network.proxy.https_port", int(My_PROXY.split(":")[1]))
		firefox_profile.set_preference("network.proxy.ssl", My_PROXY.split(":")[0])
		firefox_profile.set_preference("network.proxy.ssl_port", int(My_PROXY.split(":")[1]))
		
		# browser = webdriver.Firefox()
		browser = webdriver.Firefox(firefox_profile)
		
	browser.set_page_load_timeout(TIMEOUT)
	browser.set_script_timeout(TIMEOUT)
	# browser.maximize_window()
	
	if not show:
		browser.set_window_position(0, 2000)
	
	return browser

if __name__ == "__main__":
	browser = create_browser()
	browser.get("http://www.sina.com.cn/")
	raw_input("Quit?")
	browser.quit()