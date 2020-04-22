import http.client
import json
from datetime import datetime
import os
import sys
import config

def sendEmail(text):
    #https://www.geeksforgeeks.org/send-mail-attachment-gmail-account-using-python/

    # Python code to illustrate Sending mail with attachments 
    # from your Gmail account  

    # libraries to be imported 
    import smtplib 
    from email.mime.multipart import MIMEMultipart 
    from email.mime.text import MIMEText 
    from email.mime.base import MIMEBase 
    from email import encoders
    import secrets

    fromaddr = "martynjsmith@gmail.com"
    toaddr = "martynjsmith@gmail.com"

    # instance of MIMEMultipart 
    msg = MIMEMultipart() 

    # storing the senders email address   
    msg['From'] = fromaddr 

    # storing the receivers email address  
    msg['To'] = toaddr 

    # storing the subject  
    msg['Subject'] = "Grocery Pickup Slot Found"

    # string to store the body of the mail 
    body = text

    # attach the body with the msg instance 
    msg.attach(MIMEText(body, 'plain')) 

    # creates SMTP session 
    s = smtplib.SMTP('smtp.gmail.com', 587) 

    # start TLS for security 
    s.starttls() 

    # Authentication 
    s.login(fromaddr, secrets.password) 

    # Converts the Multipart msg into a string 
    text = msg.as_string() 

    # sending the mail 
    s.sendmail(fromaddr, toaddr, text) 

    # terminating the session 
    s.quit() 

def send_results(date, store, details, url):
    message = "On {}, found available pickup slots at {}: \r\nReserve now at: {}".format(date, store, url)
    for slot in details:
        message += "\r\nSlot: " + slot
    sendEmail(message)
    print(message)

def main():

    for item in config.stores:

        store = item["type"]
        name = item["name"]
        baseUrl = item["baseUrl"]
        sessionCookie = item["sessionCookie"]
        time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

        print(time + ": -- Checking for Grocery pickup availability at: " + name + " --") 

        conn = http.client.HTTPSConnection(baseUrl)
        payload = ''


        if store == "market-32":
            storeUrl = "https://www.instacart.com/store/" + store + "/storefront"
            reqUrl = "/v3/containers/" + store + "/next_gen/retailer_information/content/pickup?source=web"

            headers = {
                'Cookie': sessionCookie
            }

            conn.request("GET", reqUrl, payload, headers)
            res = conn.getresponse()
            if (res.status == 200):
                data = res.read()
                json_data = json.loads(data.decode("utf-8"))

                api_result = json_data["container"]["modules"][0]["types"][0]

                # Two possible values for api_result = icon_info or error
                # 'error' means no Pickup times are available!
                # 'icon_info' means Pickup options are listed into second list available in "modules" section
                if api_result == 'error':
                    # Do Nothing!)
                    print("No Pickup times are available! Let's check again in 10 minutes!")

                if api_result == 'icon_info':
                    print('Pickup Time Windows available, Send Alert!')
                    # We are in luck! Send Alert to Needy folks so that they can place their order right away!
                    Pickup_days_json = json_data["container"]["modules"][1]['data']['service_options']['service_options']['days']

                    Pickup_window_details = []

                    #print(Pickup_days_json)
                    for each_Pickup_day in Pickup_days_json:

                        for option in each_Pickup_day["options"]:

                            Pickup_window_details.append(option["full_window"])
                    
                    #print(Pickup_window_details)

                    send_results(time, name, Pickup_window_details, storeUrl)

            else:
                print('Error Code: ' + res.status)
     
        if store == "hannaford":
            storeUrl = "http://" + baseUrl
            reqUrl = "/checkout/retrieve_pickup_timeslots.cmd"

            headers = {
                'Referer': 'https://www.hannaford.com/checkout/retrieve_pickup_timeslots.cmd',
                'Cookie': sessionCookie
            }

            conn.request("GET", reqUrl, payload, headers)
            res = conn.getresponse()
            if (res.status == 200):
                data = res.read()
                json_data = json.loads(data.decode("utf-8"))

                Pickup_window_details = []

                for day in json_data["days"]:
                    #print(day)
                    date = day["date"]

                    #print('Checking date:', date)

                    if len(day["pickupTimes"]) > 0:

                        for pickupTime in day["pickupTimes"]:

                            if pickupTime["shortMessage"] != 'Unavailable':
                                print('Found a slot:', pickupTime)
                                Pickup_window_details.append(date + " " + pickupTime["timeSlot"])

                if len(Pickup_window_details) == 0:
                    print("No Pickup times are available! Let's check again in 10 minutes!")
                else:
                    print('Pickup Time Windows available, Send Alert!')
                    send_results(time, name, Pickup_window_details, storeUrl)
            else:
                print('Error Code: ' + res.status)
            
        print("-- End of Checking on Instacart Pickup Time Availability --") 

# Reference Implementation: https://github.com/utkuufuk/ping-sm/blob/master/__main__.py
# https://utkuufuk.com/2020/03/28/grocery-scraping/
if __name__ == '__main__':
    main()