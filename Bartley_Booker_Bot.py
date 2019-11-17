#!/usr/bin/env python
# coding: utf-8

# # Bartley Booking Bot

# ### Import Packages

# In[ ]:


from config import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import datetime
import time
from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
# import datefinder


# ### Helper Functions

# In[ ]:


#Get date 2 weeks from now and convert to urlstring
def get_url(booking_url):
    book_date = datetime.datetime.today() + datetime.timedelta(days=15)#use 14 when testing 15 when executing
    # book_date = datetime.datetime.today() + datetime.timedelta(days=14)#use 14 when testing 15 when executing
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
# Wait for 1200:01
def wait_for_tomorrow():    
    curr = datetime.datetime.today()
    start = (datetime.datetime.today() + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=2, microsecond=0)
    wait_time = start - curr
    wait_time_int = wait_time.total_seconds()    
    write_out('Waiting for {}'.format(wait_time_int))
    return wait_time_int

def create_event(book_time,duration = 1, time_zone = 'Asia/Singapore'):
    
    credentials = pickle.load(open("token.pkl", "rb"))
    service = build("calendar", "v3", credentials = credentials)
    calendar_id = 'rory.tan@gmail.com'
    
    book_time_end = book_time + datetime.timedelta(hours =1)    
    event = {
      'summary': 'Bartley Tennis Court Booking (Cass)',
      'location': 'Bartley Ridge, Singapore 368063',  
      'start': {
        'dateTime': book_time.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone': time_zone,
      },
      'end': {
        'dateTime': book_time_end.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone': time_zone,
      },
      'attendees': [
        {'email': 'angelamacherie@gmail.com'}
      ],
        'colorId': '10',
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'email', 'minutes': 24 * 60},
          {'method': 'popup', 'minutes': 60},
        ],
      },
    }
    return service.events().insert(calendarId=calendar_id, body=event).execute()


# ### Facility booking

# In[ ]:


def book_facility():
    day_slots = slots[(datetime.datetime.today() + datetime.timedelta(days=1)).weekday()] #use 0 when testing 1 when executing
    # day_slots = slots[(datetime.datetime.today() + datetime.timedelta(days=0)).weekday()] #use 0 when testing 1 when executing

    if day_slots:
        write_out('Found desired booking slots, initating booking')

        try:            
            #Run Headless
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome('./chromedriver_win32/chromedriver.exe',options=chrome_options)
            # driver = webdriver.Chrome('./chromedriver_win32/chromedriver.exe')
            driver.get(get_url(keys['booking_url']))
            driver.find_element_by_xpath('//*[@id="txtUser"]').send_keys(keys["user_id"]) #User
            driver.find_element_by_xpath('//*[@id="txtPassword"]').send_keys(keys["password"]) #Password
            time.sleep(wait_for_tomorrow())
            write_out('Logging in...')            
            driver.find_element_by_xpath('//*[@id="PageContentArea"]/form[1]/table/tbody/tr/td/table/tbody/tr/td/input[3]').click() #Submit                        
        except:
            driver.quit()

        for i in range(3):
            try:
                #refresh at midnight
                write_out("Starting attempt " + str(i+1))

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
                    continue
                try:
                    driver.switch_to.window(driver.window_handles[1])
                    driver.find_element_by_xpath('//*[@id="SubPageContentArea"]/form/table/tbody/tr[5]/td/input').click()
                    break
                except Exception as err:                                        
                    write_out("No Confirmation window: " + str(err))
                    driver.switch_to.window(driver.window_handles[0]) #Switch back to original tab
                    driver.get(get_url(keys['booking_url']))
                    time.sleep(1)
                    write_out("Trying again...")
                    continue                       
            except Exception as e:
                write_out("Total Failure: " + str(e))

        #Exit Chrome Driver
        driver.quit()
        write_out("----------End of Booking----------") 
    else:
        write_out('Found no desired booking slots for ' + datetime.datetime.today().weekday()) 


# ### Booking Verification & Calendar Invite

# In[ ]:


def verify_bookings():
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome('./chromedriver_win32/chromedriver.exe',options=chrome_options)
#     driver = webdriver.Chrome('./chromedriver_win32/chromedriver.exe')
    driver.get('http://bartleyrid.gotdns.com:8081/booking/mybookings.aspx?')
    driver.find_element_by_xpath('//*[@id="txtUser"]').send_keys(keys["user_id"]) #User
    driver.find_element_by_xpath('//*[@id="txtPassword"]').send_keys(keys["password"]) #Password
    driver.find_element_by_xpath('//*[@id="PageContentArea"]/form[1]/table/tbody/tr/td/table/tbody/tr/td/input[3]').click() #Submit
    
    book_date = datetime.datetime.today() + datetime.timedelta(days=14)
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
            book_time_str = booking['date'] + " " + booking['time']
            book_time = datetime.datetime.strptime(book_time_str, '%d/%m/%Y %I%p')
            create_event(book_time)
            write_out(json.dumps(booking))
        else:
            continue
    driver.quit()
    write_out("----------End of Verification----------")


# In[ ]:


if __name__ == '__main__':
    book_facility()
    verify_bookings()