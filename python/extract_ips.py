import re
import sys
 
r = '(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})'
ips = []

filename=sys.argv[1]

print filename
f = open(filename, "r")
for line in f:
	line_ips = re.findall(r, line)
	if (len(line_ips) > 0):
		for ip in line_ips:
			ips.append(ip)
	
for ip in ips:
	print '%s' %ip
