# Need to install requests via 'pip install requests'
import requests
import time
import datetime

# the times you want to test at, in seconds
# minutes    5,   10,  15,  20,   25,   30
timesecs = { 300, 600, 900, 1200, 1500, 1800}

# now loop through each of these time frames
for t in sorted(set(timesecs)):
    current_time = datetime.datetime.now()
    print 'sending request at: ' + current_time.isoformat()

    # set your URL here. i usually use the first page that is requested after auth,
    # but choose a nice easy one, without many parameters
    url = 'https://energydocs.ihs.com/search_form'
    # This is a default, if there are any other headers that are needed, add it
    headers = { 'User-Agent' : 'Mozilla/5.0' }
    # set the cookies necessary to request the resources
    cookies = { "edocsMN" : "730b7a7263ea047927ec27235bd3e668",
      "edocsSID" : "9f106ce3d12fbb3bac339a2ec1e031e2" }

    #edocsMN=730b7a7263ea047927ec27235bd3e668; edocsSID=9f106ce3d12fbb3bac339a2ec1e031e2;

    proxyDict = {
        "http" : "http://127.0.0.1:8080",
        "https" : "https://127.0.0.1:8080"
    }

    r = requests.get(url, headers=headers, cookies=cookies, proxies=proxyDict, verify=False)

    # here are some checks you can use, or add your own
    # check1: do i receive a 200 OK HTML code
    if r.status_code == 200:
      print 'right status code'
    else:
      print 'status code has changed'
      break

    print 'waiting %0.1f minutes' %(t/60.0)
    time.sleep(t)
print 'done checking'
