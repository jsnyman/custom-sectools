#!/usr/bin/env python

import httplib

connection = httplib.HTTPSConnection("www.google.com", 443)
connection.request("GET", "/")
response = connection.getresponse()

print response.status
data = response.read()
print data
