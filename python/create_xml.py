#!/usr/bin/env python

import xml.etree.ElementTree as ET

""" Creates the following XML Tree (change as is needed):
<?xml version="1.0" ?>
<soapenv:Envelope xmlns:soap="http://schemas.microsoft.com/sharepoint/soap/" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Header/>
  <soapenv:Body>
    <soap:SearchPrincipals>
      <soap:searchText>a</soap:searchText>
      <soap:maxResults>100</soap:maxResults>
      <soap:principalType>All</soap:principalType>
    </soap:SearchPrincipals>
  </soapenv:Body>
</soapenv:Envelope>
"""

def createXml():
  root = ET.Element("soapenv:Envelope", {
    "xmlns:soapenv" : "http://schemas.xmlsoap.org/soap/envelope/",
    "xmlns:soap" : "http://schemas.microsoft.com/sharepoint/soap/"
  })
  header = ET.SubElement(root, "soapenv:Header")
  body = ET.SubElement(root, "soapenv:Body")
  sp = ET.SubElement(body, "soapenv:SearchPrincipals")
  st = ET.SubElement(sp, "soap:searchText")
  st.text = "a"
  mr = ET.SubElement(sp, "soap:maxResults")
  mr.text = "100"
  pt = ET.SubElement(sp, "soap:principalType")
  pt.text = "All"
  
  return ET.tostring(root)

print createXml()
