#!/usr/bin/env python
# coding: utf-8

# In[1]:


from config import keys
from config import sessions
from selenium import webdriver
import datetime


# In[2]:


#Get date 2 weeks from now and convert to string
def get_date():
    book_date = datetime.datetime.today() + datetime.timedelta(days=14)
    book_date_str = book_date.strftime('%Y-%m-%d')
    return book_date_str

#Convert get_date() into xpath
def booking_xpath(slot): 
    frame =  str(int(slot[0:2])-5)
    xpath = '//*[@id="GridTable"]/tbody/tr[2]/td[' + frame +']'
    return xpath    

#func to book facility
def book_facility(k,slot):
    try:
        driver = webdriver.Chrome('./chromedriver_win32/chromedriver.exe')
        driver.get(k["br_url"])
        #login
        driver.find_element_by_xpath('//*[@id="edit-name"]').send_keys(k["user_id"])
        driver.find_element_by_xpath('//*[@id="edit-pass"]').send_keys(k["password"])
        driver.find_element_by_xpath('//*[@id="edit-submit"]').click()
        #Route from BR site to Vitez site
        driver.find_element_by_xpath('//*[@id="block-block-9"]/div/form/input[2]').click()
        #Go to booking url and date
        driver.switch_to.window(driver.window_handles[1])
        driver.get(k["booking_url"] + get_date())
        #Book Court - highlight timeslot Frame 2 = 7 am at 1 hour increments
        driver.find_element_by_xpath(booking_xpath(slot)).click() #day would already have been checked
        driver.find_element_by_xpath('//*[@id="HeaderTable"]/tbody/tr[1]/td/input[2]').click()
        driver.switch_to.window(driver.window_handles[2])
        driver.find_element_by_xpath('//*[@id="SubPageContentArea"]/form/table/tbody/tr[5]/td/input').click()
        driver.quit()
        #write out log file success
        with open('Bartley_Booker_Logs.txt','a+') as f:
            f.write("Success " + get_date() + " @ " + slot + "\r\n")
    except:
        with open('Bartley_Booker_Logs.txt','a+') as f:
            f.write("Failure " + get_date() + " @ " + slot + "\r\n")


# In[3]:


#Main
def main(k,slots):
    for (day,slot) in slots:
        if datetime.datetime.today().weekday() == day:
                book_facility(keys,slot)


# In[4]:


if __name__ == '__main__':
    main(keys,sessions)

