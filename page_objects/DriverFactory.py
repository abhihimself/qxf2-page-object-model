"""
DriverFactory class
NOTE: Change this class as you add support for:
1. SauceLabs/BrowserStack
2. More browsers like Opera
"""
import dotenv,os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webdriver import RemoteConnection
from appium import webdriver as mobile_webdriver
import conf.browserstack_credentials as browserstack_credentials
import conf.sauce_credentials as sauce_credentials

class DriverFactory():
    
    def __init__(self,browser='ff',sauce_flag='N',browser_version=None,os_name=None):
        "Constructor for the Driver factory"
        self.browser=browser
        self.sauce_flag=sauce_flag
        self.browser_version=browser_version
        self.os_name=os_name

        
    def get_web_driver(self,browserstack_flag,os_name,os_version,browser,browser_version):
        "Return the appropriate driver"
        if (browserstack_flag.lower() == 'y'):
            web_driver = self.run_browserstack(os_name,os_version,browser,browser_version)                                    
        elif (browserstack_flag.lower() == 'n'):
            web_driver = self.run_local(os_name,os_version,browser,browser_version)       
        else:
            print "DriverFactory does not know the browser: ",browser
            web_driver = None

        return web_driver   
    

    def run_browserstack(self,os_name,os_version,browser,browser_version):
        "Run the test in browser stack browser stack flag is 'Y'"
        #Get the browser stack credentials from browser stack credentials file
        USERNAME = browserstack_credentials.username
        PASSWORD = browserstack_credentials.accesskey
        if browser.lower() == 'ff' or browser.lower() == 'firefox':
            desired_capabilities = DesiredCapabilities.FIREFOX            
        elif browser.lower() == 'ie':
            desired_capabilities = DesiredCapabilities.INTERNETEXPLORER
        elif browser.lower() == 'chrome':
            desired_capabilities = DesiredCapabilities.CHROME            
        elif browser.lower() == 'opera':
            desired_capabilities = DesiredCapabilities.OPERA        
        elif browser.lower() == 'safari':
            desired_capabilities = DesiredCapabilities.SAFARI

        desired_capabilities['os'] = os_name
        desired_capabilities['os_version'] = os_version
        desired_capabilities['browser_version'] = browser_version
        
        return webdriver.Remote(RemoteConnection("http://%s:%s@hub-cloud.browserstack.com/wd/hub"%(USERNAME,PASSWORD),resolve_ip= False),
            desired_capabilities=desired_capabilities)


    def run_local(self,os_name,os_version,browser,browser_version):
        "Return the local driver"
        local_driver = None
        if browser.lower() == "ff" or browser.lower() == 'firefox':
            local_driver = webdriver.Firefox()    
        elif  browser.lower() == "ie":
            local_driver = webdriver.Ie()
        elif browser.lower() == "chrome":
            local_driver = webdriver.Chrome()
        elif browser.lower() == "opera":
            local_driver = webdriver.Opera()
        elif browser.lower() == "safari":
            local_driver = webdriver.Safari()

        return local_driver


    def run_mobile(self,mobile_os_name,mobile_os_version,device_name,app_package,app_activity,mobile_sauce_flag,device_flag,emulator_flag):
        "Setup mobile device"
        #Get the sauce labs credentials from sauce.credentials file
        USERNAME = sauce_credentials.username
        PASSWORD = sauce_credentials.accesskey
        desired_capabilities = {}
        desired_capabilities['osName'] = mobile_os_name
        desired_capabilities['osVersion'] = mobile_os_version
        desired_capabilities['deviceName'] = device_name
        desired_capabilities['appPackage'] = app_package
        desired_capabilities['appActivity'] = app_activity
        
        if device_flag.lower() == 'y':
            driver = mobile_webdriver.Remote('http://localhost:4723/wd/hub', desired_capabilities)
        if emulator_flag.lower() == 'y':
            desired_capabilities['app'] = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','app','app-name')) #replace app-name with the application name
            driver = mobile_webdriver.Remote('http://localhost:4723/wd/hub', desired_capabilities)
        if mobile_sauce_flag.lower() == 'y':
            desired_capabilities['idleTimeout'] = 300
            self.sauce_upload() #upload the application to the Sauce storage every time the test is run
            desired_capabilities['app'] = 'sauce-storage:app-name' #replace app-name with the application name
            desired_capabilities['name'] = 'Appium Python Test'
            desired_capabilities['autoAcceptAlert']= 'true'
            driver = mobile_webdriver.Remote(command_executor="http://%s:%s@ondemand.saucelabs.com:80/wd/hub"%(USERNAME,PASSWORD),
                desired_capabilities= desired_capabilities)
        
        return driver


    def sauce_upload(self):  
        "Upload the apk to the sauce temperory storage"
        USERNAME = sauce_credentials.username
        PASSWORD = sauce_credentials.accesskey
        headers = {'Content-Type':'application/octet-stream'}
        params = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','app','app-name')) #replace app-name with the application name
        fp = open(params,'rb')
        data = fp.read()
        fp.close()
        response = requests.post('https://saucelabs.com/rest/v1/storage/%s/app-name?overwrite=true'%USERNAME,headers=headers,data=data,auth=('%s','%s')%(USERNAME,PASSWORD)) #reaplce app-name with the application name


    def get_firefox_driver(self):
        "Return the Firefox driver"
        driver = webdriver.Firefox(firefox_profile=self.get_firefox_profile())

        return driver 


    def get_firefox_profile(self):
        "Return a firefox profile"

        return self.set_firefox_profile()

    
    def set_firefox_profile(self):
        "Setup firefox with the right preferences and return a profile"
        try:
            self.download_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','downloads'))
            if not os.path.exists(self.download_dir):
                os.makedirs(self.download_dir)
        except Exception,e:
            self.write("Exception when trying to set directory structure")
            self.write(str(e))
            
        profile = webdriver.firefox.firefox_profile.FirefoxProfile()
        set_pref = profile.set_preference
        set_pref('browser.download.folderList', 2)
        set_pref('browser.download.dir', self.download_dir)
        set_pref('browser.download.useDownloadDir', True)
        set_pref('browser.helperApps.alwaysAsk.force', False)
        set_pref('browser.helperApps.neverAsk.openFile', 'text/csv,application/octet-stream,application/pdf')
        set_pref('browser.helperApps.neverAsk.saveToDisk', 'text/csv,application/vnd.ms-excel,application/pdf,application/csv,application/octet-stream')
        set_pref('plugin.disable_full_page_plugin_for_types', 'application/pdf')
        set_pref('pdfjs.disabled',True)

        return profile


