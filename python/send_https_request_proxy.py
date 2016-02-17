#!/usr/bin/env python

import requests

proxies = {
  "http" : "http://127.0.0.1:8080",
  "https" : "http://127.0.0.1:8080"
}

r = requests.get("https://www.google.com", proxies=proxies, verify=False)

print r
