#!/usr/bin/env python
# coding: utf-8

# In[9]:


from config import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys
import datetime
import time


# In[10]:


#Get date 2 weeks from now and convert to urlstring
def get_url(booking_url):
    book_date = datetime.datetime.today() + datetime.timedelta(days=15)
    book_date_str = book_date.strftime('%Y-%m-%d')
    booking_date_url = booking_url + book_date_str
    return booking_date_url

#Convert get_date() into xpath
def booking_xpath(day_slot):
    xpath = '//*[@id="GridTable"]/tbody/tr[2]/td[' + day_slot +']'
    return xpath
def write_out(message):
     with open('Bartley_Booker_Logs.txt','a+') as f:
                f.write(datetime.datetime.today().strftime('%Y-%m-%d:%H:%M:%S') + ": "+ message + "\n")
                print(datetime.datetime.today().strftime('%Y-%m-%d:%H:%M:%S') + ": "+ message) #For test purposes only

# In[11]:

def book_facility():
    day_slots = slots[(datetime.datetime.today() + datetime.timedelta(days=1)).weekday()]
    
    if day_slots:
        write_out('Found desired booking slots, initating booking')
        
        try:            
            #Run Headless
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome('./chromedriver_win32/chromedriver.exe',options=chrome_options)
#             driver = webdriver.Chrome('./chromedriver_win32/chromedriver.exe')
            driver.get(get_url(keys['booking_url']))
            driver.find_element_by_xpath('//*[@id="txtUser"]').send_keys(keys["user_id"]) #User
            driver.find_element_by_xpath('//*[@id="txtPassword"]').send_keys(keys["password"]) #Password
            driver.find_element_by_xpath('//*[@id="PageContentArea"]/form[1]/table/tbody/tr/td/table/tbody/tr/td/input[3]').click() #Submit
            #Wait for 12
            curr = datetime.datetime.now()
            start = (datetime.datetime.today() + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=1, microsecond=0)
            wait_time = start - curr
            write_out('Waiting for {}'.format(wait_time))
            wait_time_int = wait_time.total_seconds()            
            time.sleep(wait_time_int)
            write_out('Starting...')  
            driver.refresh()
        except:
            write_out("Failed to logon, exiting webdriver")
            driver.quit()
            
        #Select slots            
        for day_slot in day_slots:
            try:
                write_out('Trying to book for slot' + frame[day_slot])
                driver.find_element_by_xpath(booking_xpath(frame[day_slot])).click()                                        
            except:                    
                write_out('Failed to book for slot'+ frame[day_slot])
                continue            

        #Submit booking            
        try:
            driver.find_element_by_xpath('//*[@id="HeaderTable"]/tbody/tr[1]/td/input[2]').click()
            driver.switch_to.window(driver.window_handles[1])
            driver.find_element_by_xpath('//*[@id="SubPageContentArea"]/form/table/tbody/tr[5]/td/input').click()        
        except:
            write_out("No available slots")
        
        driver.quit()
    else:
        write_out('Found no desired booking slots for ' + datetime.datetime.today().weekday())                


# In[12]:


if __name__ == '__main__':
    book_facility()

