import requests

url = "https://www.hannaford.com/checkout/retrieve_pickup_timeslots.cmd"

payload = {}
headers = {

    'Referer': 'https://www.hannaford.com/checkout/retrieve_pickup_timeslots.cmd',
    'Cookie': 'PIPELINE_SESSION_ID=bbcb9809511f4872b8997868189694c2; USER_SESSION_VALIDATE_COOKIE=N; JSESSIONID=3E47207249D8B3C7F8D923B07FCC03D9.tomcat1; LAST_ACCESSED_COOKIE=1587571317778'
}

response = requests.request("GET", url, headers=headers, data = payload)

print(response.text.encode('utf8'))