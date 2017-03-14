#!/usr/bin/env python
import sys
import SimpleHTTPServer
import SocketServer

PORT=8080

class MyHTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    log_file = open("logfile.txt", "a")
    def log_message(self, format, *args):
        # can call baseclass method:
        # SimpleHTTPServer.SimpleHTTPRequestHandler.log_message(self, format, *args)
        self.log_file.write("%s - - [%s] %s\n" % (self.client_address[0],
                            self.log_date_time_string(), format%args))


Handler = MyHTTPHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "serving at port", PORT

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    httpd.socket.close()
    print "Server closed!"
