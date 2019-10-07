#!/usr/bin/env python
# coding: utf-8

# In[3]:


from config import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import datetime
import time


# In[4]:


#Get date 2 weeks from now and convert to urlstring
def get_url(booking_url):
    book_date = datetime.datetime.today() + datetime.timedelta(days=15)#use 14 when testing 15 when executing
#     book_date = datetime.datetime.today() + datetime.timedelta(days=14)#use 14 when testing 15 when executing
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
#Wait for 1200:01
def wait_for_tomorrow():
    
    curr = datetime.datetime.today()
    start = (datetime.datetime.today() + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=4, microsecond=0)
    wait_time = start - curr
    wait_time_int = wait_time.total_seconds()            
    write_out('Waiting for {}'.format(wait_time_int))


# In[5]:


def book_facility():
    day_slots = slots[(datetime.datetime.today() + datetime.timedelta(days=1)).weekday()] #use 0 when testing 1 when executing
#     day_slots = slots[(datetime.datetime.today() + datetime.timedelta(days=0)).weekday()] #use 0 when testing 1 when executing

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
            wait_for_tomorrow()
            write_out('Starting...')
            driver.refresh()            
        except:
            driver.quit()

        for i in range(3):
            try:
                #refresh at midnight
                write_out("starting attempt " + str(i+1))

                #Select slots with loop            
                for day_slot in day_slots:
                    try:
                        write_out('Trying to book for slot' + frame[day_slot])
                        driver.find_element_by_xpath(booking_xpath(frame[day_slot])).click()                                        
                    except:                    
                        continue            

                #Attempt to submit booking            
                try:
                    driver.find_element_by_xpath('//*[@id="HeaderTable"]/tbody/tr[1]/td/input[2]').click()
                except:
                    driver.refresh()
                    continue
                try:
                    driver.switch_to.window(driver.window_handles[1])
                    driver.find_element_by_xpath('//*[@id="SubPageContentArea"]/form/table/tbody/tr[5]/td/input').click()
                    break
                except:
                    continue                       
            except ValueError as e:
                write_out("e")                

        #Exit Chrome Driver
        driver.quit()

    else:
        write_out('Found no desired booking slots for ' + datetime.datetime.today().weekday()) 


# In[6]:


def verify_bookings():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome('./chromedriver_win32/chromedriver.exe',options=chrome_options)
#     driver = webdriver.Chrome('./chromedriver_win32/chromedriver.exe')
    driver.get('http://bartleyrid.gotdns.com:8081/booking/mybookings.aspx?')
    driver.find_element_by_xpath('//*[@id="txtUser"]').send_keys(keys["user_id"]) #User
    driver.find_element_by_xpath('//*[@id="txtPassword"]').send_keys(keys["password"]) #Password
    driver.find_element_by_xpath('//*[@id="PageContentArea"]/form[1]/table/tbody/tr/td/table/tbody/tr/td/input[3]').click() #Submit
    
    book_date = datetime.datetime.today() + datetime.timedelta(days=15)#use 14 when testing 15 when executing
#     book_date = datetime.datetime.today() + datetime.timedelta(days=14)#use 14 when testing 15 when executing
    book_date_str = book_date.strftime('%d/%m/%Y')
    
    booking_list = []
    booking_info = {}    
    id_list=[]
    tbl = driver.find_element_by_id("Table1")
    ids = tbl.find_elements_by_xpath('//*[@id]')
    #Get a list of Ids from all items with IDs
    elements = [x for x in ids if x.get_attribute('id').startswith('ID_')]
    for element in elements:
        sub_element = element.find_elements_by_class_name("form3")
        booking_date = sub_element[0].text
        book_time = sub_element[1].text
        facility = sub_element[2].text

        booking_info = {'date': booking_date,
                        'time' : book_time,
                        'facility': facility}

        booking_list.append(booking_info)

    for booking in booking_list:
        if booking['date'] == book_date_str:
            write_out(json.dumps(booking))
        else:
            continue
    driver.quit()


# In[7]:


if __name__ == '__main__':
    book_facility()
    verify_bookings()


# In[ ]:




