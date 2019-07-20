#!/usr/bin/env python
# coding: utf-8

# In[34]:


from config import keys
from config import slots
from config import frame
from selenium import webdriver
import sys
import datetime


# In[43]:


#Get date 2 weeks from now and convert to urlstring
def get_url(booking_url):
    book_date = datetime.datetime.today() + datetime.timedelta(days=14)
    book_date_str = book_date.strftime('%Y-%m-%d')
    booking_date_url = booking_url + book_date_str
    return booking_date_url

#Convert get_date() into xpath
def booking_xpath(day_slot):
    xpath = '//*[@id="GridTable"]/tbody/tr[2]/td[' + day_slot +']'
    return xpath
def write_out(message):
     with open('Bartley_Booker_Logs.txt','a+') as f:
                f.write(datetime.datetime.today().strftime('%Y-%m-%d:%H:%M') +                          ": "+ message + "\r\n")


# In[44]:


def book_facility():
    day_slots = slots[datetime.datetime.today().weekday()]        
    if day_slots:
        write_out('Found desired booking slots, initating booking')        
        try:            
            driver = webdriver.Chrome('./chromedriver_win32/chromedriver.exe')
            driver.get(get_url(keys['booking_url']))
            driver.find_element_by_xpath('//*[@id="txtUser"]').send_keys(keys["user_id"]) #User
            driver.find_element_by_xpath('//*[@id="txtPassword"]').send_keys(keys["password"]) #Password
            driver.find_element_by_xpath('//*[@id="PageContentArea"]/form[1]/table/tbody/tr/td/table/tbody/tr/td/input[3]').click() #Submit
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


# In[45]:


if __name__ == '__main__':
    book_facility()


# In[ ]:




